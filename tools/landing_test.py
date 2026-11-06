"""Test T3-L: scripted approach and landing on EDDM runway 26L - the script flies the jet itself (hand-flown, FM 2-24:
autopilot OFF before landing). Test card: docs/notes/test-cards/T3-L-landing.md.

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\landing_test.py <output.csv> [start_nm=6] [glide_deg=2.5] [high_ft=0] [nochute]
      [fmflare] [cfg=land|to|up] [vtd=kt]
Sequence: reposition on the extended centreline start_nm before the threshold, level ~2 NM below/short of the glide
path, nose 3° up, gear down + LAND flaps, trim preset 5.2° with the AP OFF -> level segment -> glide path intercept from
below -> glide path (vertical speed from ground speed + path error) -> flare from 120 ft (sink eased to -150 ft/min,
thrust to ~80-83 % N1, FM 2-25) -> touchdown: idle, nose down, drag chute (ground spoiler drag, cfg) after 1 s,
hard wheel braking -> stop.
Pitch: elevator PI controller on vertical speed + pitch-rate damping; roll: ailerons on a bank target from the
localizer (heading from cross-track); speed: throttle PI on the FM final approach speed (Fig. 2-7, +5 kt/1 000 lb).
Controller structure from sideslip_test.py (T3-E2 passed). Signs (probed 2026-10-27): +elevator axis = nose down,
+aileron axis = raw bank increases, raw PLANE_BANK positive = left bank, raw PLANE_PITCH negative = nose up.
Why not the MSFS AP: it flies pitch by trim only (~0.13°/s), cannot hold a repositioned jet nor flare (dry runs 1-9).
Optional 4th argument HIGH (ft): dry run against a virtual runway raised by HIGH (build-up, no crash risk).
Go-around, hand-flown (FM 2-29: Maximum to 300 KIAS, speed brakes in, +1 500 ft/min, level 2 000 ft above the field;
gear up once climbing, flaps TAKEOFF ≥ 180 KIAS, UP ≥ 260 KIAS after 30 s; then the AP takes over), also at the end of
a dry run, if IAS < v_app - 25 (not in the flare) or
|bank| > 35° or pitch outside -15..+20° at any height, |cross-track| > 300 ft or |bank| > 30° below 500 ft, glide path
error < -300 ft below 400 ft, or the gear is not down 2 NM out.
Results: touchdown IAS, sink rate, pitch, distance past the threshold; ground roll to a stop; CSV log + simlog CSV.
"""
import csv
import math
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)   # live output when run in the background
out = sys.argv[1]
start_nm = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
glide = math.radians(float(sys.argv[3]) if len(sys.argv) > 3 else 2.5)   # FM: 700-800 ft/min like ILS/PAR
# build-up / dry run: virtual runway raised by HIGH ft (e.g. 4000) -> the whole approach and flare are flown in the
# air, "touchdown" = reaching the virtual runway height, then climb away. Validates the approach without crash risk.
HIGH = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
CHUTE = "nochute" not in sys.argv[5:]                               # F3: landing without drag chute (FM Fig. A8-4)
FM_FLARE = "fmflare" in sys.argv[5:]       # FM 2-25 flare power (82-83 % rpm, idle at TD) - for the rpm-dependent BLC (H3)
# 2026-11-05 (S3 landing variants): cfg=land (default) | to (FM 3-32 BLC malfunction: TAKEOFF flaps, final >= 195, TD >= 165)
# | up (FM 3-36 no-flap: final >= 230, sink <= 2 000 ft/min, TD >= 190); speeds +5 kt per 1 000 lb above 16 100 lb like
# Fig. 2-7; vtd=<kt> overrides the touchdown speed (no-flap at sim weights: alpha vs. the 12.3 deg tail-strike angle)
CFG = next((a.split("=")[1] for a in sys.argv[5:] if a.startswith("cfg=")), "land")
VTD = next((float(a.split("=")[1]) for a in sys.argv[5:] if a.startswith("vtd=")), None)
# 2026-11-06 (F8, FM 2-29): ga=<ft> = go-around commanded in the flare when AGL falls below <ft> (height loss and time to
# a positive climb are reported); the go-around itself is the validated hand-flown FM 2-29 procedure
GA_FT = next((float(a.split("=")[1]) for a in sys.argv[5:] if a.startswith("ga=")), None)
# 2026-11-06 (F7, FM 2-28 touch-and-go): `tg` = after the touchdown IDLE -> flaps TAKEOFF + trim 5° + speed brakes in ->
# MILITARY -> srot rotation (takeoff_test law: stick schedule to S_HOLD, slow attitude integrator, rate damping, never push)
# -> at 35 ft AGL the go-around climb law (F8). `tg=stop` = build-up: the same ground run without rotation, abort at
# 170 KIAS / 7 000 ft past the threshold to a full stop. Card docs/notes/test-cards/F7-touch-and-go.md.
TG = next((a for a in sys.argv[5:] if a == "tg" or a.startswith("tg=")), None)
# 2026-11-06 (F4, FM 2-28 minimum-run landing): `minrun` = touchdown target 140 KIAS +5 kt per 1 000 lb above 15 100 lb
# (Fig. A8-2 note) unless vtd= is given, speed brakes OUT from the flare ("use the speed brakes to aid in controlling
# touchdown point and speed"), drag chute as usual. Card docs/notes/test-cards/F4-minimum-run.md.
MINRUN = "minrun" in sys.argv[5:]
# 2026-11-06 (F9, FM 2-25/2-28 crosswind): `xw=<kt>` = expected surface crosswind: approach and touchdown speed +5 kt per
# 10 kt (FM 2-28 note, LAND flaps); crab method (FM 2-25: "in strong crosswinds the crab method"): heading target + crab
# angle asin(crosswind/TAS) from the sim's wind at the aircraft (read in the slow group), crab removed with the rudder
# between 30 and 5 ft AGL. Forces the FAST loop. Card docs/notes/test-cards/F9-crosswind.md.
XW = next((float(a.split("=")[1]) for a in sys.argv[5:] if a.startswith("xw=")), None)
TG_STOP = TG == "tg=stop"
TG_HOLD, S_HOLD, THETA_T = 2000.0, -6600.0, 10.5     # nose-wheel hold (nose down), srot stick (takeoff_test [M]), target
if CFG != "land":
    FM_FLARE = True       # F6 dry 1: the idle cut in the flare bled 213 -> 192 KIAS and the sink rose to -926 ft/min ->
                          # FM 2-25 technique (82 % floor, idle at the touchdown) for the landing variants
# 2026-11-06 (S9-ID, card S3-bank-loop.md): the bank PID 250/150/60 is stable at 6.3 Hz at 210 KIAS / TAKEOFF / gear down
# (8 recoveries from up to 48°) but limit-cycles with this script's 0.55 s pass (≈ 12 reads). FAST loop: every airborne
# pass reads only altitude, bank and pitch (+ one of three groups of the slow values in turn) and updates elevator and
# ailerons -> ≈ 4 Hz uniform. Default for cfg=to|up; option `fast` for cfg=land (the validated LAND path is unchanged
# without it). Same gains; the VS filter keeps its time constant (coefficient from dt).
FAST = CFG != "land" or "fast" in sys.argv[5:] or TG is not None or XW is not None
AIR = ("level", "approach", "flare", "go-around")
FASTPH = AIR + ("tg",)
DEG = 57.29578
FT_PER_DEG = 60 * 6076.12
LAT0, LON0, HDG = 48.34472097713059, 11.803858844132039, 263.4     # 26L threshold = T3-D start position (true)
AIM_FT = 1000.0                                                     # aim point past the threshold
TRIM_DEG = {"land": 5.2, "to": 7.0, "up": 8.0}[CFG]   # to/up [S] as config_test slow mode; land: approach trim: 4.4° -> α 2.7°, T3-L 5.6° -> 4.1° => 5.2° for α ≈ 3.2° (CL 0.80 at 190 KIAS)
# controller gains (sideslip_test.py at ~350 KIAS: 120/40 and 400/250/150; scaled up for ~190 KIAS, q about 1/3)
KP_VS, KI_VS, KQ = 300.0, 10.0, 150.0    # counts per ft/s, per ft (integral), per °/s pitch rate
# dry run 11: 600/400/200 -> roll limit cycle ±20-31°, period ~4.5 s (F-104 roll power + ~2 Hz loop) -> ~40 %
KP_B, KD_B, KI_B = 250.0, 150.0, 60.0    # counts per ° bank error, per °/s, per °·s

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def wrap(d):
    return (d + 180) % 360 - 180


def lat_fast(n=2):
    """2026-11-05 (F6 dry 2): the main loop runs at ≈ 1.8 Hz (≈ 12 reads per pass) - at 210 KIAS the bank loop had no
    margin left (oscillation ±10-24°, lesson 19). Inner bank loop for the landing variants: n extra aileron updates per
    pass that read ONLY the bank (one read ≈ 30 ms) against the localizer bank target of the last fly() call.
    cfg=land keeps the validated 2 Hz behaviour (sleep only)."""
    # DISABLED 2026-11-05 (F6 dry 4): with the fast P+D updates the bank loop diverged too (29° level, 103° in the
    # go-around) - the loop must be designed at the desk from identified roll response data first (lesson 20)
    if True or CFG == "land" or "bank_tgt" not in res:
        time.sleep(0.05)
        return
    for _ in range(n):
        tb = time.time()
        bank = g("PLANE_BANK_DEGREES") * DEG
        dtb = max(tb - res.get("fast_t", tb - 0.1), 0.03)
        p = (bank - res.get("fast_bank", bank)) / dtb
        res["fast_t"], res["fast_bank"] = tb, bank
        e_b = bank - res["bank_tgt"]           # no integration here: fly() integrates (dry 3: double-counted I term)
        ev("AXIS_AILERONS_SET", int(clamp(-res["ka"] * (KP_B * e_b + KD_B * p + KI_B * res["integ_b"]), -8000, 8000)))
        res["n_fast"] = res.get("n_fast", 0) + 1


def fly(vs_tgt, kp_scale, bank, p, q, hdg, c, dt, ks_e=1.0, ks_a=1.0):
    """Hand flying: elevator PI on vertical speed + pitch-rate damping (+axis = nose down); ailerons PID on a bank
    target from the localizer (heading from cross-track; right turn = negative raw bank)."""
    err_fps = (res["vs_f"] - vs_tgt) / 60.0
    res["integ"] = clamp(res["integ"] + err_fps * dt, -200.0, 200.0)
    cmd_e = clamp(ks_e * (KP_VS * kp_scale * err_fps + KI_VS * res["integ"] + KQ * q), -12000, 6000)
    if res.get("tg_xfer"):                                            # F7: bumpless transfer from the srot stick (5 s)
        if res.get("tg_off") is None:
            res["tg_off"] = res["tg_last"] - cmd_e
        cmd_e = clamp(cmd_e + res["tg_off"] * max(0.0, 1.0 - (time.time() - res["tg_xfer"]) / 5.0), -12000, 6000)
    res["cmd_e"] = cmd_e                                              # start value of the rollout ramp (bumpless)
    ev("AXIS_ELEVATOR_SET", int(cmd_e))
    # F9: crab into the wind (+ = right); removed between 30 and 5 ft AGL (decrab with the rudder, see the flare)
    crab = res.get("crab", 0.0) * clamp((res.get("agl_now", 999.0) - 5.0) / 25.0, 0.0, 1.0)
    hdg_tgt = HDG + crab - clamp(0.05 * c, -15, 15)
    bank_tgt = -clamp(2.0 * wrap(hdg_tgt - hdg), -15, 15)
    e_b = bank - bank_tgt
    res["integ_b"] = clamp(res["integ_b"] + e_b * dt, -30.0, 30.0)
    # limit ±8000 (landing 9: a gust rolled the jet -7 -> -22° in the flare with the ailerons at the ±4000 limit;
    # the gains, not the limit, set the small-signal stability - dry run 11)
    # 2026-11-05 (F6 dry 1, cfg=to at 200-213 KIAS: bank ±8-13°): roll power ∝ q̄ -> gains scaled down above 185 KIAS
    # for the landing variants only (cfg=land unchanged: validated landings at 175-190 KIAS)
    # F6 dry 2/3 (2026-11-05): scaling P/D down with (185/IAS)² left the integrator dominant -> 4.5 s divergent PI
    # oscillation (bank 30-36°) -> no scaling (ka = 1); dry 1 with the original gains flew level/approach cleanly
    ka = ks_a                    # 1.0 except in the go-around above v_app (2026-11-06, F7: see the go-around phase)
    res["bank_tgt"], res["ka"] = bank_tgt, ka                         # for the fast inner bank loop (lat_fast)
    cmd_a = clamp(-ka * (KP_B * e_b + KD_B * p + KI_B * res["integ_b"]), -8000, 8000)
    ev("AXIS_AILERONS_SET", int(cmd_a))


def go_around(reason):
    """FM 2-29 / Fig. 2-8: Maximum (marginal climb in landing config), speed brakes IN; the script keeps flying by hand
    (dry run 14: handing over to the trim-based AP lost 558 ft); gear/flaps are handled in the go-around phase
    (landing 6: early FLAPS_1 -> crash). The AP takes over only when clean at ≥ 260 KIAS (cleanup)."""
    ev("THROTTLE1_SET", 16383)
    ev("SPOILERS_OFF")
    ev("AXIS_RUDDER_SET", 0)                                          # F9: decrab rudder off
    print(f"GO-AROUND: {reason}")
    return "go-around"


def ap_master(on):
    """AP_MASTER is a toggle: read, toggle, verify."""
    for _ in range(3):
        if (g("AUTOPILOT_MASTER") == 1) == on:
            return
        ev("AP_MASTER")
        time.sleep(0.3)


h = math.radians(HDG)
U = (math.sin(h), math.cos(h))          # runway direction (east, north)
R = (math.cos(h), -math.sin(h))         # right of the runway direction


def track(lat, lon):
    """-> along-track distance past the threshold (ft, negative before it), cross-track (ft, + = right of centreline)"""
    n = (lat - LAT0) * FT_PER_DEG
    e = (lon - LON0) * FT_PER_DEG * math.cos(math.radians(LAT0))
    return e * U[0] + n * U[1], e * R[0] + n * R[1]


# --- set up: weight -> speeds, preconditions
w = g("TOTAL_WEIGHT")
fuel, n1 = g("FUEL_TOTAL_QUANTITY_WEIGHT"), g("TURB_ENG_N1:1")
if fuel < 1500 or n1 < 60:                                           # idling on the runway burns the tanks empty
    sm.exit()
    sys.exit(f"ABORT: fuel {fuel:.0f} lb, N1 {n1:.0f} % - reload the flight / refuel before the landing test")
V_FM = {"land": (175, 155), "to": (195, 165), "up": (230, 190)}[CFG]   # Fig. 2-7 / FM 3-32 / FM 3-36 at 16 100 lb
v_app = V_FM[0] + 5 * (w / 1000 - 16.1)                               # final approach, +5 kt per 1 000 lb
v_app += 0.5 * (XW or 0.0)                                            # F9: +5 kt per 10 kt crosswind
v_td = VTD if VTD else V_FM[1] + 5 * (w / 1000 - 16.1)               # touchdown
v_td += 0.5 * (XW or 0.0) if not VTD else 0.0
if MINRUN and not VTD:
    v_td = 140.0 + 5 * (w / 1000 - 15.1)
start_ft = start_nm * 6076.12
lat_s = LAT0 - start_ft * U[1] / FT_PER_DEG
lon_s = LON0 - start_ft * U[0] / (FT_PER_DEG * math.cos(math.radians(LAT0)))
field_elev = 1457.0 + HIGH                                           # EDDM 26L ground (T3-D: 1461.6 ft MSL - 4.3 ft CG)
# level segment below the glide path, intercept from below like an ILS; ~2 NM of level flight to configure
alt0 = field_elev + (max(start_ft - 12000, 6000) + AIM_FT) * math.tan(glide)

# --- position: speed argument behaves like IAS (dry run 1: 200 -> 205 KIAS; the TAS correction of dry runs 5-9
# started the jet at 250 KIAS). Nose 3° up = expected α (SimConnect pitch negative = nose up; dry run 8).
ap_master(False)
ev("SPOILERS_OFF")                                                   # chute/speed brakes of a previous run
sm.set_pos(alt0, lat_s, lon_s, int(v_app), -3.0, 0.0, HDG, 0)
time.sleep(1.0)
ev("GEAR_DOWN")                                                      # AFTER set_pos: positioning in the air
ev({"land": "FLAPS_DOWN", "to": "FLAPS_1", "up": "FLAPS_UP"}[CFG])   # set_pos retracts the gear (landings 1/3 were belly landings)
ap_master(False)
# trim preset with the AP OFF (AP engaged = trim locked; 2026-10-27 isolated test, sim settings fixed by pete)
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", TRIM_DEG / DEG)
    time.sleep(0.2)
    if g("ELEVATOR_TRIM_POSITION") * DEG > TRIM_DEG - 0.3:
        break
ev("THROTTLE1_SET", 9500)
print(f"cfg {CFG}: weight {w:.0f} lb -> final approach {v_app:.0f} KIAS, touchdown {v_td:.0f} KIAS; start {start_nm} NM, "
      f"level at {alt0:.0f} ft MSL; trim {g('ELEVATOR_TRIM_POSITION') * DEG:.1f}°, AP {g('AUTOPILOT_MASTER'):.0f}")
# full-rate flight data (alpha, pitch, elevator, trim, N1 ...) next to this script's own log
log = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "simlog.py"),
                        out.replace(".csv", "_simlog.csv"), "400", "3"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

def slow_read(dt):
    """The validated full read of every pass (cfg=land, rollout; ≈ 12 reads, 0.55 s pass) - unchanged code, moved here
    2026-11-06 when the FAST pass was added."""
    lat, lon = g("PLANE_LATITUDE"), g("PLANE_LONGITUDE")
    if abs(lat) < 1.6:                                               # library may return radians
        lat, lon = lat * DEG, lon * DEG
    s, c = track(lat, lon)
    # dry runs 6/12: a failed read returns 0 -> lat/lon 0 -> s, c in the millions -> false glide path intercept 510 ft
    # below the path. Reject samples that jump more than 2 000 ft (≈ 6 s of flight at ~2 Hz) and keep the last good one.
    if "s" in res and (abs(s - res["s"]) > 2000 or abs(c - res["c"]) > 2000):
        s, c = res["s"], res["c"]
    res["s"], res["c"] = s, c
    agl, ias, gnd = g("PLANE_ALT_ABOVE_GROUND"), g("AIRSPEED_INDICATED"), g("SIM_ON_GROUND") == 1
    alt, bank = g("PLANE_ALTITUDE"), g("PLANE_BANK_DEGREES") * DEG    # raw bank: + = left
    theta, hdg = -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_HEADING_DEGREES_TRUE") * DEG
    if alt == 0 and "prev_alt" in res:                               # failed read (returns 0): keep the last value
        alt = res["prev_alt"]
    if ias == 0 and "last_ias" in res and not gnd:
        ias = res["last_ias"]
    res["last_ias"] = res["ias"] = ias
    if HIGH:                                                         # dry run: height above the virtual runway
        agl = alt - field_elev
        gnd = agl < 5
    vs = (alt - res.get("prev_alt", alt)) / dt * 60                 # ft/min from altitude (VERTICAL_SPEED unit unclear)
    res["prev_alt"] = alt
    res["vs_f"] = 0.5 * res.get("vs_f", vs) + 0.5 * vs               # smoothed for the controller
    q = (theta - res.get("prev_theta", theta)) / dt                 # pitch rate, nose up +
    p = (bank - res.get("prev_bank", bank)) / dt
    res["prev_theta"], res["prev_bank"] = theta, bank
    gs_kt = g("GROUND_VELOCITY")
    return s, c, agl, ias, gnd, alt, bank, theta, hdg, vs, q, p, gs_kt


phase = "level"
thr = 9500.0
res = {"integ": 0.0, "integ_b": 0.0}
roll = 0.0
t0 = prev_t = time.time()
rows = []
while time.time() - t0 < 600:
    t = time.time()
    dt = max(t - prev_t, 0.05)
    prev_t = t
    if FAST and phase in FASTPH:
        # fast pass (see FAST above): altitude, bank, pitch every pass; slow groups in turn (each ≈ every 3rd pass)
        kk = res.get("n_pass", 0) % 3
        res["n_pass"] = res.get("n_pass", 0) + 1
        alt, bank = g("PLANE_ALTITUDE"), g("PLANE_BANK_DEGREES") * DEG
        theta = -g("PLANE_PITCH_DEGREES") * DEG
        if alt == 0 and "prev_alt" in res:                           # failed read (returns 0): keep the last value
            alt = res["prev_alt"]
        if bank == 0 and abs(res.get("prev_bank", 0)) > 1:           # failed read: no false rate spike
            bank = res["prev_bank"]
        if theta == 0 and abs(res.get("prev_theta", 0)) > 1:
            theta = res["prev_theta"]
        if kk == 0 or "s" not in res:
            lat, lon = g("PLANE_LATITUDE"), g("PLANE_LONGITUDE")
            if abs(lat) < 1.6:
                lat, lon = lat * DEG, lon * DEG
            s, c = track(lat, lon)
            # failed read (lat/lon 0) -> jump of millions of ft: keep the last good fix and its time
            if not ("s" in res and (abs(s - res["s"]) > 2000 or abs(c - res["c"]) > 2000)):
                res["s"], res["c"], res["t_s"] = s, c, t
        # along-track dead-reckoned with the ground speed between the position reads (0.7 s ≈ 300 ft ≈ 13 ft of glide path)
        s = res["s"] + res.get("gs", 0.0) * 1.68781 * (t - res["t_s"])
        c = res["c"]
        if kk == 1 or "agl_raw" not in res:
            agl_r = g("PLANE_ALT_ABOVE_GROUND")
            # 2026-11-06 (F7 S16b): a failed read (0) dead-reckoned AGL to 15 ft at 1 480 ft AGL - in the approach that
            # would trigger the flare -> keep the last value when 0 arrives from above 50 ft
            if not (agl_r == 0 and res.get("agl_raw", 0) > 50):
                res["agl_raw"], res["alt_at_agl"] = agl_r, alt
            ias_r = g("AIRSPEED_INDICATED")
            res["ias_raw"] = ias_r if ias_r else res.get("ias_raw", 0.0)
            res["gnd_raw"] = g("SIM_ON_GROUND") == 1
        agl = res["agl_raw"] + (alt - res["alt_at_agl"])            # dead-reckoned between the AGL reads
        ias, gnd = res["ias_raw"], res["gnd_raw"]
        res["gear_fresh"] = kk == 2 or "hdg" not in res
        if res["gear_fresh"]:
            h_r = g("PLANE_HEADING_DEGREES_TRUE") * DEG
            res["hdg"] = h_r if h_r else res.get("hdg", HDG)
            res["gs"], res["gear"] = g("GROUND_VELOCITY"), g("GEAR_TOTAL_PCT_EXTENDED")
            res["n_wind"] = res.get("n_wind", 0) + 1
            if XW is not None and res["n_wind"] % 2 == 1:             # F9: crab angle from the sim's wind (every 2nd)
                wd, wv, tas = g("AMBIENT_WIND_DIRECTION"), g("AMBIENT_WIND_VELOCITY"), g("AIRSPEED_TRUE")
                if tas and tas > 100:
                    xc = wv * math.sin(math.radians(wd - HDG))        # + = from the right
                    res["xw_now"] = xc
                    res["crab"] = math.degrees(math.asin(clamp(xc / tas, -0.3, 0.3)))
        hdg, gs_kt = res["hdg"], res["gs"]
        res["last_ias"] = res["ias"] = ias
        if HIGH:
            agl = alt - field_elev
            gnd = agl < 5
        res["agl_now"] = agl                                          # F9: decrab height for fly()
        vs = (alt - res.get("prev_alt", alt)) / dt * 60
        res["prev_alt"] = alt
        a_f = 1.0 - 0.5 ** (dt / 0.55)                               # = the 0.5/0.5 filter of the 0.55 s pass
        res["vs_f"] = (1.0 - a_f) * res.get("vs_f", vs) + a_f * vs
        q = (theta - res.get("prev_theta", theta)) / dt
        p = (bank - res.get("prev_bank", bank)) / dt
        res["prev_theta"], res["prev_bank"] = theta, bank
    else:
        s, c, agl, ias, gnd, alt, bank, theta, hdg, vs, q, p, gs_kt = slow_read(dt)
    path_alt = field_elev + (AIM_FT - s) * math.tan(glide)
    path_err = alt - path_alt                                        # + = above the glide path
    vs_tgt = 0.0

    if phase in ("level", "approach", "flare"):
        if phase == "level" and path_err >= 0:                       # glide path intercepted from below
            phase = "approach"
            print(f"glide path intercept {s:.0f} ft from the threshold, {ias:.0f} KIAS, gear {g('GEAR_TOTAL_PCT_EXTENDED'):.0%}, "
                  f"flaps {g('TRAILING_EDGE_FLAPS_LEFT_ANGLE') * DEG:.0f}°, α {g('INCIDENCE_ALPHA') * DEG:.1f}°")
        if phase == "level":
            vs_tgt = clamp(4.0 * (alt0 - alt), -1000, 1000)
        elif phase == "approach":
            # nominal VS for the ground speed, corrected by the path error (1 ft/min per 0.25 ft, ±800)
            vs_tgt = -gs_kt * 101.27 * math.tan(glide) - clamp(4.0 * path_err, -800, 800)
            if agl < (120 if CFG == "land" else 150):            # F6 dry 1: flare from 112 ft could not stop the sink
                phase = "flare"
                res["vs0"] = res["vs_f"]
                if MINRUN:
                    ev("SPOILERS_ON")                                 # FM 2-28: speed brakes for TD point/speed
                    print("minimum run: speed brakes OUT")
                print(f"flare at {agl:.0f} ft AGL, {ias:.0f} KIAS, {s:.0f} ft from the threshold, path error {path_err:+.0f} ft, "
                      f"sink {res['vs_f']:.0f} ft/min")
        if phase == "flare":
            # 2026-10-30: -150 gave 20-60 ft/min touchdowns at ≈ 174 KIAS and a float/skip of ≈ 5 s (template ground
            # effect ≈ +8 % lift, gear rebound) -> firmer touchdown, ≈ 250 ft/min (no float, FM: avoid holding off)
            vs_tgt = -250 + (res["vs0"] + 250) * clamp((agl - 20) / 100, 0.0, 1.0)
        # dry run 10: flare gains too soft (pitch 1.9 -> 5.1° in 9 s, sink 864 ft/min at TD) -> x1.6 in the flare
        # 2026-10-31 (dry 20): with idle in the flare the sink grew to ≈ 700 ft/min at TD (target 250) -> x2.2
        # FM flare (82 % N1 floor, H3): x2.2 ballooned (pitch -0.4 -> 8.3 -> -3°, back up to 29 ft, TD 519-1 017 ft/min in
        # dry H3_dry2/3, with and without BLC loss) -> x1.6 for the FM flare
        fly(vs_tgt, (1.6 if FM_FLARE else 2.2) if phase == "flare" else 1.0, bank, p, q, hdg, c, dt)
        if XW is not None and phase == "flare" and agl < 30:
            # F9 decrab, step-1 version (gentle: -350 counts/°, bank ±0.7° below 50 ft at 5 kt). 2026-11-06 step 2 repeat: a
            # feed-forward of 2 640 counts per degree of crab rolled the jet to -16° at 13 ft (F-104 roll due to sideslip,
            # δa/δr 0.37) -> REVERTED; FM 2-25: strong crosswind = crab method to the touchdown (desk work: card F9)
            ev("AXIS_RUDDER_SET", int(clamp(-350 * wrap(HDG - hdg), -8000, 8000)))
        # speed: PI throttle with feed-forward on the approach speed; FM 2-25 in the flare: below 100 ft SMOOTHLY to
        # 82-83 % rpm, idle at touchdown (dry run 10: gain 300 towards 80 % cut the throttle to near idle in 3 s ->
        # thrust/BLC loss, sink rose again) -> gain 40 towards 83 %
        # 2026-10-31: the FM 83 % rpm rule (it keeps the BLC alive in the real jet) bled only ≈ 10 kt in the flare (TD 170
        # vs. FM 158-163 KIAS); the sim models no rpm-dependent BLC -> in the flare the speed target ramps from v_app to
        # the FM touchdown speed between 100 and 20 ft AGL and the same PI throttle (idle..Military) flies it
        spd_tgt = v_app if phase != "flare" else v_td + 2.5 + (v_app - v_td - 2.5) * clamp((agl - 20) / 80, 0.0, 1.0)
        if True:
            err = spd_tgt - ias
            res["i_spd"] = clamp(res.get("i_spd", 0.0) + err * dt, -60.0, 60.0)
            # dry run 13 (19 170 lb): Military could not hold the speed level in landing config (170 -> 157 KIAS) ->
            # AB allowed in the level segment (FM 2-24 heavy weight: Military may not be enough); approach ≤ Military
            thr = clamp(9000.0 + 250.0 * err + 25.0 * res["i_spd"], 0.0 if phase == "flare" else 2000.0,
                        16383.0 if phase == "level" else 11141.0)
            if phase == "flare" and ias > spd_tgt + 3 and not FM_FLARE:  # dry run 19: PI only went to ≈ 5 300 -> idle while fast
                thr = 0.0
            # 2026-11-06 (F6 dry 5, cfg=to): virtual TD 197 KIAS with this floor. FM Fig. A8-2 gives only a MINIMUM
            # touchdown speed for TAKEOFF flaps (180 KIAS at 19 000 lb); even the idle cut of dry 1 bled only 213 -> 192 in the
            # flare -> 197 is FM-conform and kept (no change: the PI alone would stay at ≈ 91 % N1 at -10 kt)
            if phase == "flare" and FM_FLARE:
                # 2026-10-31 (H3, rpm-dependent BLC via tools/blc_driver.py): the idle cut in the flare dropped the BLC lift
                # -> TD sink 1 125 ft/min at 10.6° pitch (dry H3_dry1) = FM 2-25 "abrupt thrust reduction -> rapid increase
                # in rate of sink". FM technique: smooth reduction to 82-83 % rpm, IDLE as the main gear touches ->
                # N1 floor 82 % in the flare (integrating throttle floor)
                res["thr_floor"] = clamp(res.get("thr_floor", thr) + 400.0 * (82.0 - g("TURB_ENG_N1:1")) * dt, 0.0, 11141.0)
                thr = max(thr, res["thr_floor"])
        ev("THROTTLE1_SET", int(thr))
        # 2026-10-31: a single failed read (returns 0) triggered a go-around with the gear 100 % down -> 3 reads in a row
        if not FAST:
            res["gear_bad"] = res.get("gear_bad", 0) + 1 if s > -12000 and g("GEAR_TOTAL_PCT_EXTENDED") < 0.99 else 0
        elif res.get("gear_fresh"):                                  # FAST: count only real reads (cached value otherwise)
            res["gear_bad"] = res.get("gear_bad", 0) + 1 if s > -12000 and res["gear"] < 0.99 else 0
        res.setdefault("gear_bad", 0)
        if res["gear_bad"] >= 3 and not res.get("gear_go"):
            res["gear_go"] = True                                    # gear not down 2 NM out -> go around
            print(f"GEAR NOT DOWN ({g('GEAR_TOTAL_PCT_EXTENDED'):.2f}) at {s:.0f} ft")
        # low speed: FM Fig. 6-4 minimum control speed LAND flaps ≈ 150-155 KIAS at 19 500 lb (not in the flare)
        bad = (abs(bank) > 35 or not -15 < theta < 20 or (agl < 500 and (abs(c) > 300 or abs(bank) > 30))
               or (phase != "flare" and ias < v_app - 25)
               or (agl < 400 and path_err < -300) or res.get("gear_go")
               or (agl < 60 and theta > 11.0))                         # tail strike at 12.3 deg pitch (CR-2144, AP-5)
        if GA_FT and phase == "flare" and agl < GA_FT and not gnd:
            res["ga_cmd"] = dict(t=t, agl=agl, ias=ias, vs=res["vs_f"], min_agl=agl, t_min=t, t_pos=None)
            phase = go_around(f"F8 commanded at {agl:.0f} ft AGL, {ias:.0f} KIAS, sink {res['vs_f']:.0f} ft/min")
        if bad and not gnd:
            phase = go_around(f"AGL {agl:.0f}, {ias:.0f} KIAS, cross-track {c:.0f} ft, bank {bank:.0f}°, "
                              f"pitch {theta:.0f}°, path error {path_err:+.0f} ft")
        if gnd and phase != "go-around":
            res["td"] = dict(ias=ias, vs=res.get("last_vs", vs), pitch=theta, s=s, c=c,
                             gear=g("GEAR_TOTAL_PCT_EXTENDED"), t=t - t0)
            print(f"{'VIRTUAL ' if HIGH else ''}TOUCHDOWN {ias:.0f} KIAS, gear {res['td']['gear']:.0%}, sink {res['td']['vs']:.0f} ft/min, "
                  f"pitch {theta:.1f}°, {s:.0f} ft past the threshold, {c:+.0f} ft off the centreline")
            if HIGH:
                # dry run ends with a real FM go-around (dry run 13: the old cleanup selected flaps UP at ~170 KIAS,
                # far below the clean minimum speed 200-225 KIAS (Fig. 6-4) -> the jet sank into the ground)
                phase = go_around("dry run end")
                continue
            phase = "rollout" if not TG else "tg"
            ev("AXIS_AILERONS_SET", 0)
            ev("THROTTLE1_SET", 0)
            res["t_td"] = t
            res["cmd_e_td"] = res.get("cmd_e", 0.0)
            if TG:
                res["tg"] = dict(sub="idle", t=t, s_td=s)
                print(f"TOUCH-AND-GO: idle at {ias:.0f} KIAS, {s:.0f} ft past the threshold")
            else:
                print(f"rollout elevator ramp starts at the flare command {res['cmd_e_td']:.0f}")
        res["last_vs"] = vs
    elif phase == "tg":
        tg, el = res["tg"], t - res["tg"]["t"]
        ev("AXIS_RUDDER_SET", int(clamp(-700 * wrap(HDG - hdg) - 3 * c, -8000, 8000)) if agl < 50 else 0)
        res["integ_b"] = clamp(res["integ_b"] + bank * dt, -30.0, 30.0)
        ev("AXIS_AILERONS_SET", int(clamp(-(KP_B * bank + KD_B * p + KI_B * res["integ_b"]), -8000, 8000)))
        cmd = TG_HOLD
        stop = None
        if tg["sub"] == "idle":                                       # bumpless from the flare command to the hold
            cmd = res["cmd_e_td"] + (TG_HOLD - res["cmd_e_td"]) * clamp(el / 1.5, 0.0, 1.0)
            if el > 1.0 and theta < 1.5 and gnd:
                tg.update(sub="config", t_c=t)
                ev("FLAPS_1")
                ev("SPOILERS_OFF")
                aq.set("ELEVATOR_TRIM_POSITION", 5.0 / DEG)          # takeoff trim (srot S_HOLD is tuned for 5°)
                print(f"T&G: flaps TAKEOFF, trim 5°, speed brakes in at {ias:.0f} KIAS, {s:.0f} ft")
        elif tg["sub"] == "config":
            if g("TRAILING_EDGE_FLAPS_LEFT_ANGLE") * DEG <= 16.0 or t - tg["t_c"] > 6.0:
                tg.update(sub="mil", t_m=t)
                ev("THROTTLE1_SET", 11141)
                print(f"T&G: MILITARY at {ias:.0f} KIAS, {s:.0f} ft")
        elif tg["sub"] == "mil":
            if TG_STOP and (ias >= 170 or s > 7000):
                stop = f"build-up end (tg=stop) at {ias:.0f} KIAS, {s:.0f} ft"
            elif not TG_STOP and g("TURB_ENG_N1:1") >= 95 and ias >= 155:
                tg.update(sub="rot", t_r=t, vr0=ias)
                print(f"T&G: rotation (srot) from {ias:.0f} KIAS, {s:.0f} ft")
        elif tg["sub"] == "rot":
            ramp = clamp(max((ias - tg["vr0"]) / 25.0, (t - tg["t_r"]) / 4.0), 0.0, 1.0)
            ff = TG_HOLD + (S_HOLD - TG_HOLD) * ramp
            if theta > 3.0:                                           # nose wheel off: slow attitude trim
                res["ith"] = clamp(res.get("ith", 0.0) + (THETA_T - theta) * dt, -10.0, 10.0)
            res["qf"] = 0.6 * res.get("qf", 0.0) + 0.4 * q
            cmd = ff - 150.0 * res.get("ith", 0.0) + 150.0 * res["qf"]   # +axis = nose down: rate relieves the pull
            if agl < 20 and theta > 11.0:                             # tail strike guard (contact 12.3°)
                cmd += 2000.0 * (theta - 11.0)
            cmd = clamp(cmd, -12000.0, 0.0)                           # never push during the rotation
            if not gnd and agl > 5 and "lo" not in tg:
                tg["lo"] = dict(ias=ias, s=s, theta=theta)
                print(f"T&G: liftoff at {ias:.0f} KIAS, pitch {theta:.1f}°, {s:.0f} ft past the threshold "
                      f"({s - tg['s_td']:.0f} ft after the touchdown)")
            if not gnd and agl > 35:
                phase = "go-around"                                   # validated FM 2-29 climb (F8), bumpless
                res["integ"], res["tg_last"], res["tg_xfer"] = 0.0, cmd, time.time()
                ev("THROTTLE1_SET", 11141)
                print(f"T&G: climb-out law at {agl:.0f} ft, {ias:.0f} KIAS, pitch {theta:.1f}°")
        if tg["sub"] in ("idle", "config", "mil") and gnd and ias < 140:
            stop = f"ABORT T&G: {ias:.0f} KIAS before the rotation"
        if gnd and s > 8000 and phase == "tg":
            stop = stop or f"ABORT T&G: still on the ground {s:.0f} ft past the threshold at {ias:.0f} KIAS"
        if stop:
            print(stop)
            phase = "rollout"                                         # validated rollout: idle, nose down, brakes
            ev("THROTTLE1_SET", 0)
            res["t_td"], res["cmd_e_td"] = t, cmd
            tg["stop"] = stop
        if phase == "tg":
            ev("AXIS_ELEVATOR_SET", int(cmd))
        res["cmd_e"] = cmd
    elif phase == "rollout":
        # 2026-10-30 (landing 18, high-rate rollout log): the jet skipped twice after the first touch (3.5 s airborne,
        # ≈ 1 000 ft) -> the ground roll counts from the FINAL touchdown (FM A8-3/A8-4 assume no skip); skips are reported
        # a failed read returns 0 for SIM_ON_GROUND -> count a skip only when really off the ground (landing 22: a "skip"
        # that the high-rate log does not show)
        if not gnd and agl > 2:
            roll = 0.0
            res["air"] = True
        else:                                                         # on the ground (or a failed read)
            if res.get("air") and gnd:
                res["air"] = False
                res["skips"] = res.get("skips", 0) + 1
                res["td_final_ias"] = ias
            roll += gs_kt * 1.68781 * dt
        # FM 2-25: lower the nose wheel at once (4 000 already gives -4.2° of the 5° nose-down stop; 10 000 tried
        # 2026-10-30: -5.0°, no benefit). 2026-10-30 (landing 19, high-rate log): the instant push at ≈ 175 kt slammed the
        # nose wheel down and the jet porpoised (pitch +4.8 <-> -2.4°, ≈ 1 s) with 2-3 skips -> ramp the push over 3 s
        # 2026-10-31 (F3 regression after H2): the ramp started at 0 although the flare loop was pushing at the touchdown
        # (elevator ≈ -0.9°) -> with the 5.2° approach trim the nose rose 1.8 -> 4.4° within 0.6 s after the main-gear
        # contact, α 3.2 -> 3.9°, 1.12 g at 168 KIAS -> 2 s hop. The gear springs are not the cause (computed at 26 600 lb
        # the effective damping at 18 000 lb is ≈ 0.85, nearly critical). -> bumpless: ramp from the last flare command
        c0 = res.get("cmd_e_td", 0.0)
        ev("AXIS_ELEVATOR_SET", int(c0 + (4000 - c0) * clamp((t - res["t_td"]) / 3.0, 0.0, 1.0)))
        nose_down = theta < 1.0 and t - res["t_td"] > 1.0                # FM: brakes after the nose wheel is down
        # FM 2-25: deploy the chute as soon as the nose wheel is on the ground (all three gear down). 2026-10-31 (H3_F2a): the
        # old "1 s after the first touch" deployed it during a hop -> only on the ground with the nose down (pitch < 1°)
        if CHUTE and not res.get("chute") and gnd and nose_down:
            ev("SPOILERS_ON")                                         # = drag chute (ground spoiler drag, cfg)
            res["chute"] = ias
            print(f"drag chute at {ias:.0f} KIAS (limit 180 MB-7G / 205 BS-4000)")
        if XW is None:
            # validated law (F2/F3). NOTE 2026-11-06 (F9 step 2): the -3 x c term has the WRONG sign (c > 0 = right of the
            # centreline needs nose LEFT = + axis); harmless in calm air (c ±2 ft) - fix only with an F3 regression
            ev("AXIS_RUDDER_SET", int(clamp(-700 * wrap(HDG - hdg) - 3 * c, -8000, 8000)))
        elif not gnd:
            # F9 step 2 repeat: the rollout rudder acting during the post-touchdown skip rolled the jet to -11.7° (sideslip in
            # the air) -> no rudder while airborne in the rollout phase
            ev("AXIS_RUDDER_SET", 0)
        else:
            # F9 step 2: weather-vaning held the heading 1.2° into the wind (P only) and with the wrong-sign c term the jet
            # drifted to +66 ft -> PI on a heading that steers back to the centreline (0.1°/ft, ±5°), + axis = nose left.
            # NOT yet flown in this form (step 2 repeat: overshoot to -5.8° / -21 ft after the skip) - desk work first
            e_r = wrap((HDG - clamp(0.1 * c, -5.0, 5.0)) - hdg)
            res["i_rud"] = clamp(res.get("i_rud", 0.0) + e_r * dt, -20.0, 20.0)
            ev("AXIS_RUDDER_SET", int(clamp(-700 * e_r - 100 * res["i_rud"], -12000, 12000)))
        if XW is not None and ias > 80:
            # F9 step 1 (2026-11-06): a skip after the touchdown rolled the jet to -7° with the ailerons at 0 -> with a
            # crosswind the ailerons keep the wings level on the rollout (P+D of the validated bank loop, no I term)
            ev("AXIS_AILERONS_SET", int(clamp(-(KP_B * bank + KD_B * p), -8000, 8000)))
        if nose_down or res.get("braking"):
            res["braking"] = True
            ev("AXIS_LEFT_BRAKE_SET", 16383)                          # FM A8-3/A8-4: hard braking to the stop
            ev("AXIS_RIGHT_BRAKE_SET", 16383)
        if gs_kt < 3:
            res["roll"] = roll
            break
    elif phase == "go-around":
        # hand-flown climb: +1 500 ft/min, less if the speed is low (0 at v_app - 20), level off 2 000 ft above the field
        vs_tgt = min(clamp(100.0 * (ias - (v_app - 20)), 0.0, 1500.0), clamp(2.0 * (field_elev + 2000 - alt), -500, 1500))
        # 2026-11-06 (F7 S16b): the go-around accelerates to 350-450 KIAS at 1 000-1 500 ft AGL with the gains for ≈ 190 KIAS
        # -> pitch 0 <-> 11-15° (≈ 5 s) and bank up to -42° (F8/dry runs: pitch swings of 14° above 330 KIAS already).
        # Whole-controller scaling: elevator x (v_app/IAS)² (pitch power ∝ q̄), ailerons x v_app/IAS (p_ss ∝ TAS)
        ks_e = clamp((v_app / max(ias, 100.0)) ** 2, 0.25, 1.0)
        ks_a = clamp(v_app / max(ias, 100.0), 0.4, 1.0)
        fly(vs_tgt, 1.0, bank, p, q, hdg, c, dt, ks_e, ks_a)
        # Maximum until 300 KIAS, then Military (TAKEOFF flap limit 370 KIAS, gear transient 260 KIAS)
        # 2026-11-06 (F5 dry 2, cfg=up): from a 227 KIAS go-around the clean jet reached 271 KIAS before the climb criterion
        # raised the gear (transient limit 260) -> no-flap: Military (FM 2-29 "Military, Maximum if needed"), and the gear
        # goes up at > 245 KIAS once clear of the ground in any configuration
        ev("THROTTLE1_SET", 16383 if ias < 300 and CFG != "up" else 11141)
        # FM 2-29: gear UP once climbing, flaps TAKEOFF at ≥ 180 KIAS (≥ 30 s), UP at ≥ 260 KIAS; done when clean
        if ((vs > 500 and agl > 200) or (ias > 245 and agl > 50)) and not res.get("ga_gear"):   # climb established / gear limit
            res["ga_gear"] = True
            ev("GEAR_UP")
        if res.get("ga_gear") and ias >= 180 and not res.get("ga_flaps"):
            res["ga_flaps"] = t
            # 2026-11-06 (F5 dry 1, cfg=up): FLAPS_1 EXTENDED the flaps from UP at 250 KIAS with the 8° no-flap trim ->
            # pitch-up to 38° at full nose-down stick. The FM 2-29 step retracts LAND -> TAKEOFF; only for cfg=land
            if CFG == "land":
                ev("FLAPS_1")                                         # TAKEOFF
        # 2026-11-06 (F5 dry 1): no trim management in the go-around - with the elevator command at the nose-down clamp
        # (6 000 = stabilizer -5°) the approach trim kept the nose rising -> trim relief like a pilot: 1°/s nose down
        # while the command is within 10 % of the clamp, not below 1°
        if res.get("cmd_e", 0.0) > 5400:
            trim_now = g("ELEVATOR_TRIM_POSITION") * DEG
            if trim_now > 1.0:
                aq.set("ELEVATOR_TRIM_POSITION", max(1.0, trim_now - 1.0 * dt) / DEG)
                res["ga_trim_relief"] = res.get("ga_trim_relief", 0) + 1
        if theta > 25 and not res.get("ga_pitch_warn"):
            res["ga_pitch_warn"] = True
            print(f"WARNING go-around pitch {theta:.0f}° at {ias:.0f} KIAS, elevator command {res.get('cmd_e', 0):.0f}")
        # TAKEOFF flap limit 370 KIAS (FM 3-36) has priority over the 30 s BLC cooling time -> retract at 340 KIAS latest
        if res.get("ga_flaps") and ((t - res["ga_flaps"] > 30 and ias >= 260) or ias >= 340) and not res.get("ga_clean"):
            res["ga_clean"] = True
            ev("FLAPS_UP")
        if res.get("ga_clean") and agl > 1500 and g("TRAILING_EDGE_FLAPS_LEFT_ANGLE") * DEG < 1:
            break
    if res.get("ga_cmd") and phase == "go-around":                   # F8: height loss after the commanded go-around
        gc = res["ga_cmd"]
        if agl < gc["min_agl"]:
            gc["min_agl"], gc["t_min"], gc["ias_min"] = agl, t, ias
        if gc["t_pos"] is None and res["vs_f"] > 0:
            gc["t_pos"] = t
    rows.append([round(t - t0, 2), phase, round(s), round(c), round(agl), round(ias, 1), round(vs), round(bank, 1),
                 round(theta, 1), round(path_err), round(vs_tgt), int(thr), round(hdg, 2)])
    if FAST and phase in FASTPH:
        time.sleep(0.01)
    elif phase in AIR:
        lat_fast()
    else:
        time.sleep(0.05)

for n in ("AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET", "AXIS_AILERONS_SET"):
    ev(n, 0)
if g("SIM_ON_GROUND") != 1:
    # still airborne: the go-around phase has cleaned up per FM (or the time ran out). Leave a safe cruise state:
    # AP on, ALT hold; flaps UP and cruise power only at ≥ 260 KIAS (FM 2-22/2-29), else Military and flaps as they are
    # (2026-10-27: full AB with gear + LAND flaps burned ~3 000 lb; dry run 13: flaps UP at ~170 KIAS -> sank to the ground)
    ap_master(True)
    ev("AP_HDG_HOLD_ON")
    ev("SPOILERS_OFF")
    clean = g("AIRSPEED_INDICATED") >= 260
    if clean:
        ev("GEAR_UP")
        ev("FLAPS_UP")
    # 2026-10-31: 9 000 left the jet at 558 KIAS at 7 600 ft after a dry run (fuel 4 000 -> 600 lb in a few minutes,
    # high-q AP regime) -> 5 000 once clean (≈ 300-350 KIAS at low altitude)
    ev("THROTTLE1_SET", 5000 if clean else 11141)
    ev("AP_ALT_VAR_SET_ENGLISH", int(g("PLANE_ALTITUDE") + 500))
    ev("AP_ALT_HOLD_ON")
if phase == "rollout" or "roll" in res:
    ev("PARKING_BRAKES") if g("BRAKE_PARKING_POSITION") != 1 else None
    ev("AXIS_LEFT_BRAKE_SET", -16383)
    ev("AXIS_RIGHT_BRAKE_SET", -16383)
sm.exit()
log.terminate()                                                     # simlog writes each row as it goes
with open(out, "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["t", "phase", "along_ft", "cross_ft", "agl", "ias", "vs_fpm", "bank", "pitch", "path_err_ft",
                 "vs_tgt", "throttle", "hdg_true"])
    wr.writerows(rows)
if res.get("ga_cmd"):
    gc = res["ga_cmd"]
    print(f"F8 GO-AROUND: commanded at {gc['agl']:.0f} ft AGL / {gc['ias']:.0f} KIAS / {gc['vs']:.0f} ft/min; lowest "
          f"{gc['min_agl']:.0f} ft AGL after {gc['t_min'] - gc['t']:.1f} s (height loss {gc['agl'] - gc['min_agl']:.0f} ft, "
          f"{gc.get('ias_min', gc['ias']):.0f} KIAS); positive climb after "
          f"{(gc['t_pos'] - gc['t']) if gc['t_pos'] else float('nan'):.1f} s")
print(f"{len(rows)} samples ({len(rows) / max(rows[-1][0], 1):.1f} Hz main loop, {res.get('n_fast', 0) / max(rows[-1][0], 1):.1f} Hz extra bank updates) -> {out}" if rows else "no samples")
if "td" in res:
    print(f"Result: touchdown {res['td']['ias']:.0f} KIAS (FM normal {v_td:.0f}-{v_td + 5:.0f}), "
          f"{res['td']['s']:.0f} ft past the threshold, ground roll {res.get('roll', float('nan')):.0f} ft from the final touchdown "
          f"at {res.get('td_final_ias', res['td']['ias']):.0f} KIAS ({res.get('skips', 0)} skip(s) after the first touch)")
else:
    print(f"Result: no touchdown (phase {phase})")
