"""Test T3-L: scripted approach and landing on EDDM runway 26L - the script flies the jet itself (hand-flown, FM 2-24:
autopilot OFF before landing). Test card: docs/notes/test-cards/T3-L-landing.md.

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\landing_test.py <output.csv> [start_nm=6] [glide_deg=2.5] [high_ft=0]
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
Go-around (FM 2-29: Maximum, speed brakes in, AP on with VS +3000; gear up once climbing, flaps TAKEOFF ≥ 180 KIAS) if
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
DEG = 57.29578
FT_PER_DEG = 60 * 6076.12
LAT0, LON0, HDG = 48.34472097713059, 11.803858844132039, 263.4     # 26L threshold = T3-D start position (true)
AIM_FT = 1000.0                                                     # aim point past the threshold
TRIM_DEG = 5.2          # approach trim: 4.4° -> α 2.7°, T3-L 5.6° -> 4.1° => 5.2° for α ≈ 3.2° (CL 0.80 at 190 KIAS)
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
v_app = 175 + 5 * (w / 1000 - 16.1)                                  # FM Fig. 2-7: final 175 KIAS @ 16 100 lb
v_td = 155 + 5 * (w / 1000 - 16.1)                                   # FM Fig. 2-7: touchdown 155-160 KIAS
start_ft = start_nm * 6076.12
lat_s = LAT0 - start_ft * U[1] / FT_PER_DEG
lon_s = LON0 - start_ft * U[0] / (FT_PER_DEG * math.cos(math.radians(LAT0)))
field_elev = 1457.0 + HIGH                                           # EDDM 26L ground (T3-D: 1461.6 ft MSL - 4.3 ft CG)
# level segment below the glide path, intercept from below like an ILS; ~2 NM of level flight to configure
alt0 = field_elev + (max(start_ft - 12000, 6000) + AIM_FT) * math.tan(glide)

# --- position: speed argument behaves like IAS (dry run 1: 200 -> 205 KIAS; the TAS correction of dry runs 5-9
# started the jet at 250 KIAS). Nose 3° up = expected α (SimConnect pitch negative = nose up; dry run 8).
ap_master(False)
sm.set_pos(alt0, lat_s, lon_s, int(v_app), -3.0, 0.0, HDG, 0)
time.sleep(1.0)
ev("GEAR_DOWN")                                                      # AFTER set_pos: positioning in the air
ev("FLAPS_DOWN")                                                     # retracts the gear (landings 1/3 were belly landings)
ap_master(False)
# trim preset with the AP OFF (AP engaged = trim locked; 2026-10-27 isolated test, sim settings fixed by pete)
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", TRIM_DEG / DEG)
    time.sleep(0.2)
    if g("ELEVATOR_TRIM_POSITION") * DEG > TRIM_DEG - 0.3:
        break
ev("THROTTLE1_SET", 9500)
print(f"weight {w:.0f} lb -> final approach {v_app:.0f} KIAS, touchdown {v_td:.0f} KIAS; start {start_nm} NM, "
      f"level at {alt0:.0f} ft MSL; trim {g('ELEVATOR_TRIM_POSITION') * DEG:.1f}°, AP {g('AUTOPILOT_MASTER'):.0f}")
# full-rate flight data (alpha, pitch, elevator, trim, N1 ...) next to this script's own log
log = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "simlog.py"),
                        out.replace(".csv", "_simlog.csv"), "400", "3"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

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
    res["last_ias"] = ias
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
            if agl < 120:
                phase = "flare"
                res["vs0"] = res["vs_f"]
                print(f"flare at {agl:.0f} ft AGL, {ias:.0f} KIAS, {s:.0f} ft from the threshold, path error {path_err:+.0f} ft, "
                      f"sink {res['vs_f']:.0f} ft/min")
        if phase == "flare":
            vs_tgt = -150 + (res["vs0"] + 150) * clamp((agl - 20) / 100, 0.0, 1.0)
        # pitch: elevator PI on vertical speed + pitch-rate damping (+axis = nose down)
        err_fps = (res["vs_f"] - vs_tgt) / 60.0
        res["integ"] = clamp(res["integ"] + err_fps * dt, -200.0, 200.0)
        # dry run 10: flare gains too soft (pitch 1.9 -> 5.1° in 9 s, sink 864 ft/min at TD) -> x1.6 in the flare
        kp = KP_VS * (1.6 if phase == "flare" else 1.0)
        cmd_e = clamp(kp * err_fps + KI_VS * res["integ"] + KQ * q, -12000, 6000)
        ev("AXIS_ELEVATOR_SET", int(cmd_e))
        # roll: localizer -> heading target -> bank target (right turn = negative raw bank), ailerons PID
        hdg_tgt = HDG - clamp(0.05 * c, -15, 15)
        bank_tgt = -clamp(2.0 * wrap(hdg_tgt - hdg), -15, 15)
        e_b = bank - bank_tgt
        res["integ_b"] = clamp(res["integ_b"] + e_b * dt, -30.0, 30.0)
        cmd_a = clamp(-(KP_B * e_b + KD_B * p + KI_B * res["integ_b"]), -4000, 4000)
        ev("AXIS_AILERONS_SET", int(cmd_a))
        # speed: PI throttle with feed-forward on the approach speed; FM 2-25 in the flare: below 100 ft SMOOTHLY to
        # 82-83 % rpm, idle at touchdown (dry run 10: gain 300 towards 80 % cut the throttle to near idle in 3 s ->
        # thrust/BLC loss, sink rose again) -> gain 40 towards 83 %
        if phase != "flare" or agl >= 100:
            err = v_app - ias
            res["i_spd"] = clamp(res.get("i_spd", 0.0) + err * dt, -60.0, 60.0)
            thr = clamp(9000.0 + 250.0 * err + 25.0 * res["i_spd"], 2000.0, 11141.0)
        else:
            thr = clamp(thr + 40.0 * (83.0 - g("TURB_ENG_N1:1")) * dt, 0.0, 11141.0)
        ev("THROTTLE1_SET", int(thr))
        if s > -12000 and g("GEAR_TOTAL_PCT_EXTENDED") < 0.99 and not res.get("gear_go"):
            res["gear_go"] = True                                    # gear not down 2 NM out -> go around
            print(f"GEAR NOT DOWN ({g('GEAR_TOTAL_PCT_EXTENDED'):.2f}) at {s:.0f} ft")
        bad = (abs(bank) > 35 or not -15 < theta < 20 or (agl < 500 and (abs(c) > 300 or abs(bank) > 30))
               or (agl < 400 and path_err < -300) or res.get("gear_go"))
        if bad and not gnd:
            phase = "go-around"
            # FM 2-29 / Fig. 2-8: Maximum (marginal climb in landing config), speed brakes IN; AP takes over;
            # gear UP and flaps TAKEOFF (≥ 180 KIAS) only once climbing (landing 6: early FLAPS_1 -> crash)
            for n in ("AXIS_ELEVATOR_SET", "AXIS_AILERONS_SET"):
                ev(n, 0)
            ev("THROTTLE1_SET", 16383)
            ev("SPOILERS_OFF")
            ev("HEADING_BUG_SET", int(round(HDG)) % 360)
            ap_master(True)
            ev("AP_HDG_HOLD_ON")
            ev("AP_ALT_VAR_SET_ENGLISH", int(field_elev + 3000))
            ev("AP_VS_VAR_SET_ENGLISH", 3000)
            ev("AP_PANEL_VS_ON")
            print(f"GO-AROUND: AGL {agl:.0f}, cross-track {c:.0f} ft, bank {bank:.0f}°, pitch {theta:.0f}°, "
                  f"path error {path_err:+.0f} ft")
        if gnd:
            phase = "rollout"
            res["td"] = dict(ias=ias, vs=res.get("last_vs", vs), pitch=theta, s=s, c=c,
                             gear=g("GEAR_TOTAL_PCT_EXTENDED"), t=t - t0)
            print(f"{'VIRTUAL ' if HIGH else ''}TOUCHDOWN {ias:.0f} KIAS, gear {res['td']['gear']:.0%}, sink {res['td']['vs']:.0f} ft/min, "
                  f"pitch {theta:.1f}°, {s:.0f} ft past the threshold, {c:+.0f} ft off the centreline")
            if HIGH:                                                 # dry run ends here: climb away (cleanup below)
                break
            ev("AXIS_AILERONS_SET", 0)
            ev("THROTTLE1_SET", 0)
            res["t_td"] = t
        res["last_vs"] = vs
    elif phase == "rollout":
        roll += gs_kt * 1.68781 * dt
        ev("AXIS_ELEVATOR_SET", 4000)                                # FM 2-25: lower the nose wheel at once
        if not res.get("chute") and t - res["t_td"] > 1.0:              # FM 2-28: chute blossoms as the nose wheel touches
            ev("SPOILERS_ON")                                         # = drag chute (ground spoiler drag, cfg)
            res["chute"] = ias
            print(f"drag chute at {ias:.0f} KIAS (limit 180 MB-7G / 205 BS-4000)")
        ev("AXIS_RUDDER_SET", int(clamp(-700 * wrap(HDG - hdg) - 3 * c, -8000, 8000)))
        ev("AXIS_LEFT_BRAKE_SET", 16383)                              # FM A8-3/A8-4: hard braking to the stop
        ev("AXIS_RIGHT_BRAKE_SET", 16383)
        if gs_kt < 3:
            res["roll"] = roll
            break
    elif phase == "go-around":
        if vs > 500 and agl > 200 and not res.get("ga_gear"):          # climb established
            res["ga_gear"] = True
            ev("GEAR_UP")
        if res.get("ga_gear") and ias >= 180 and not res.get("ga_flaps"):
            res["ga_flaps"] = True
            ev("FLAPS_1")                                             # TAKEOFF
        if agl > 1500:
            break
    rows.append([round(t - t0, 2), phase, round(s), round(c), round(agl), round(ias, 1), round(vs), round(bank, 1),
                 round(theta, 1), round(path_err), round(vs_tgt), int(thr)])
    time.sleep(0.05)

for n in ("AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET", "AXIS_AILERONS_SET"):
    ev(n, 0)
if g("SIM_ON_GROUND") != 1:
    # still airborne (dry run / go-around): AP on, clean up and leave a fuel-saving cruise state - 2026-10-27 the jet
    # kept flying in full AB with gear + LAND flaps after a dry run and burned ~3 000 lb at 260 kt
    ev("HEADING_BUG_SET", int(round(g("PLANE_HEADING_DEGREES_MAGNETIC") * DEG)) % 360)
    ap_master(True)
    ev("AP_HDG_HOLD_ON")
    ev("GEAR_UP")
    ev("FLAPS_UP")
    ev("SPOILERS_OFF")
    ev("THROTTLE1_SET", 11141 if HIGH and "td" in res else 9000)
    ev("AP_ALT_VAR_SET_ENGLISH", int(g("PLANE_ALTITUDE") + 1000))
    ev("AP_VS_VAR_SET_ENGLISH", 1500)
    ev("AP_PANEL_VS_ON")
if phase == "rollout" or "roll" in res:
    ev("PARKING_BRAKES") if g("BRAKE_PARKING_POSITION") != 1 else None
    ev("AXIS_LEFT_BRAKE_SET", -16383)
    ev("AXIS_RIGHT_BRAKE_SET", -16383)
sm.exit()
log.terminate()                                                     # simlog writes each row as it goes
with open(out, "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["t", "phase", "along_ft", "cross_ft", "agl", "ias", "vs_fpm", "bank", "pitch", "path_err_ft",
                 "vs_tgt", "throttle"])
    wr.writerows(rows)
print(f"{len(rows)} samples ({len(rows) / max(rows[-1][0], 1):.1f} Hz) -> {out}" if rows else "no samples")
if "td" in res:
    print(f"Result: touchdown {res['td']['ias']:.0f} KIAS (FM normal {v_td:.0f}-{v_td + 5:.0f}), "
          f"{res['td']['s']:.0f} ft past the threshold, ground roll {res.get('roll', float('nan')):.0f} ft")
else:
    print(f"Result: no touchdown (phase {phase})")
