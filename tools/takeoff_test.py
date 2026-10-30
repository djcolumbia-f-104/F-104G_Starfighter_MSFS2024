"""Test T3-D: takeoff run, controlled via SimConnect (Claude flies the takeoff per FM 6-5).

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\takeoff_test.py <output.csv> [vr_kt=157] [theta_target=10.5] [fm]
  fm: FM 2-20 brake release technique (D1b ground run, Fig. A2-5): Military against the brakes -> release -> max AB
      (default: full AB against the parking brake, released at N1 >= 99 %)
  qrot: EXPERIMENTAL pitch-rate rotation (2026-10-30, failed first try - see code); default: attitude ramp 3°/s + feed-forward 5000
Precondition: aircraft lined up on the runway, engine running, flaps TAKEOFF, trim 5°, parking brake set.
Sequence: full afterburner against the parking brake -> at N1 >= 99 % (max. 12 s) release the brake -> rudder holds
the runway heading -> from vr_kt pull the pitch to theta_target at 3°/s (rotate ~20 kt below liftoff speed, FM 6-5)
-> climb-out hand-flown (2026-10-30; the trim-based MSFS AP took over at 30 ft and held the jet at 20-35 ft for 12 s
while it accelerated to 330 kt -> gear up at 330 KIAS, TAKEOFF flaps up at 376 KIAS, both over the FM limits):
pitch to 15° (softer gains scaled with (185/IAS)²), wings level by aileron, gear UP when definitely airborne (1 s,
climbing), then Military (gear up before 260 KIAS, FM 2-11), flaps UP at ≥ 260 KIAS and ≥ 300 ft (FM), at 1 500 ft
above ground reduced power (throttle 7000) and AP altitude hold.
Abort (idle + brake) at a heading deviation > 10° on the ground or 90 s without liftoff.
Tail strike guard: on the ground the target pitch is limited to 11° (ground contact at 12.3°, AP-5).
Evaluation: liftoff IAS, ground roll, max. pitch on the ground (printed at the end + CSV).
"""
import csv
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8")
out = sys.argv[1]
vr = float(sys.argv[2]) if len(sys.argv) > 2 else 157.0
theta_target = float(sys.argv[3]) if len(sys.argv) > 3 else 10.5
FM_TECH = "fm" in sys.argv[4:]
# 2026-10-30: experimental pitch-RATE rotation ("qrot"). First try (..._T3D_takeoff_qrot1): the nose rose ≈ 6°/s, the P term
# PUSHED (+1 600), pitch fell 5 -> -0.8° right after the first liftoff, the AP fallback took over at 4 ft and the jet bounced
# along the runway at 180-230 kt and drifted off the centreline (pete: "neben der Piste") -> NOT the default; the default stays
# the old attitude ramp + feed-forward (known: slight overshoot, FM 6-5)
QROT = "qrot" in sys.argv[4:] or "taxi" in sys.argv[4:]
# build-up for a new rotation law (testcard rule 2026-10-30): high-speed taxi - apply the rotation law from vr until pitch
# 3° or 168 kt, then idle, lower the nose gently, brake to a stop (no liftoff)
TAXI = "taxi" in sys.argv[4:]
DEG = 57.29578
FULL = 16383

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)
ev = {n: ae.find(n) for n in ("AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET", "AXIS_AILERONS_SET", "AXIS_LEFT_BRAKE_SET", "AXIS_RIGHT_BRAKE_SET", "THROTTLE1_SET", "PARKING_BRAKES", "GEAR_UP",
                              "FLAPS_UP", "AP_MASTER", "AP_ALT_VAR_SET_ENGLISH", "AP_ALT_HOLD_ON", "AP_VS_VAR_SET_ENGLISH",
                              "AP_HDG_HOLD_ON", "HEADING_BUG_SET")}
# not in the library's catalog (ae.find -> None, run 5 crashed) -> map directly
ev["AP_PANEL_VS_ON"] = Event(b"AP_PANEL_VS_ON", sm)
missing = [n for n, e in ev.items() if e is None]
if missing:
    sys.exit(f"Events not found: {missing}")


def rad(v):
    return v or 0.0


def state(full=True):
    # During the takeoff run each read waits for the next sim frame (~70 ms) -> only the essentials per loop
    s = {
        "t": time.time(), "ias": aq.get("AIRSPEED_INDICATED") or 0, "gnd": aq.get("SIM_ON_GROUND") == 1,
        "theta": -rad(aq.get("PLANE_PITCH_DEGREES")) * DEG,          # nose up positive
        "hdg": rad(aq.get("PLANE_HEADING_DEGREES_TRUE")) * DEG, "gs": aq.get("GROUND_VELOCITY") or 0, "agl": 0.0,
        "bank": 0.0,
    }
    if full:
        s["agl"] = aq.get("PLANE_ALT_ABOVE_GROUND") or 0
        s["bank"] = rad(aq.get("PLANE_BANK_DEGREES")) * DEG              # raw: positive = left bank
    return s


def axis(name, v):
    ev[name](int(max(-FULL, min(FULL, v))))


def wrap(d):
    return (d + 180) % 360 - 180


s0 = state()
lat0, lon0 = aq.get("PLANE_LATITUDE"), aq.get("PLANE_LONGITUDE")
print(f"Start position (for msfs_set_aircraft_position): lat {lat0}, lon {lon0}, heading {s0['hdg']:.1f}° true")
if not s0["gnd"]:
    sys.exit("Aircraft is not on the ground - aborted")
# 2026-10-30: a bouncing jet after a bad respawn gave an invalid takeoff -> it must sit still before the run
if abs(aq.get("VERTICAL_SPEED") or 0) > 30 or not -0.5 < s0["theta"] < 1.5 or (aq.get("GEAR_TOTAL_PCT_EXTENDED") or 0) < 0.99:
    sys.exit(f"Aircraft not settled (pitch {s0['theta']:.1f}°, VS {aq.get('VERTICAL_SPEED') or 0:.0f}, gear "
             f"{aq.get('GEAR_TOTAL_PCT_EXTENDED')}) - aborted")
# The lever position alone is not enough (run 5: lever TAKEOFF, flaps 0° because hydraulic without a hydraulic system)
flap = rad(aq.get("TRAILING_EDGE_FLAPS_LEFT_ANGLE")) * DEG
print(f"Flaps trailing edge {flap:.1f}°, trim {rad(aq.get('ELEVATOR_TRIM_POSITION')) * DEG:.2f}°")
if not 10 <= flap <= 20:
    sys.exit("Flaps not in TAKEOFF (15°) - aborted")
# 2026-10-31 (H2_reg_takeoff): a fresh flight load has trim 0°; without runway_start the climb-out loop could not raise the
# nose (pitch ≈ 1° up to 330 KIAS, skipping at 4-10 ft) and the AP fallback later dived to 8 ft AGL at 435 kt -> FM takeoff trim 5°
trim = rad(aq.get("ELEVATOR_TRIM_POSITION")) * DEG
if not 4.0 <= trim <= 6.0:
    sys.exit(f"Trim {trim:.1f}° is not the FM takeoff trim 5° - aborted (run runway_start first)")
# 2026-10-30: runway_start once left the jet at 273° -> the script held that heading and rolled diagonally across the runway.
# Use the runway heading (EDDM 26L 263.4° true) and refuse to start if the jet is not aligned
RWY_HDG = 263.4
if abs(wrap(s0["hdg"] - RWY_HDG)) > 2.0:
    sys.exit(f"Aircraft heading {s0['hdg']:.1f}° not aligned with runway 26L ({RWY_HDG}°) - aborted (run runway_start again)")
hdg0 = RWY_HDG
# speed brakes out on the ground = drag chute emulation (spoiler_limit 65° > air limit) -> must be in for takeoff
ev_sb = Event(b"SPOILERS_OFF", sm)
ev_sb()
time.sleep(2.5)                                          # spoiler_extension_time 2 s
if (aq.get("SPOILERS_HANDLE_POSITION") or 0) > 0.01:
    sys.exit("Speed brakes not retracted - aborted")
if aq.get("BRAKE_PARKING_POSITION") != 1:
    ev["PARKING_BRAKES"]()
axis("AXIS_ELEVATOR_SET", 0)
axis("AXIS_RUDDER_SET", 0)
ev["THROTTLE1_SET"](11141 if FM_TECH else FULL)             # FM 2-20: Military -> brakes off -> AB
t_spool = time.time()
while time.time() - t_spool < 12 and (aq.get("TURB_ENG_N1:1") or 0) < 99:
    time.sleep(0.2)
print(f"N1 {aq.get('TURB_ENG_N1:1') or 0:.1f} % after {time.time() - t_spool:.1f} s -> brake released")
ev["PARKING_BRAKES"]()
if FM_TECH:
    ev["THROTTLE1_SET"](FULL)

# Gains for a ~3 Hz control loop (run 2 with 2500/1500 and 1500/900 oscillated and ended in the ground)
KP_HDG, KD_HDG = 700.0, 400.0            # counts per ° and per °/s (positive axis = nose LEFT, T3-D run 1)
KP_TH, KD_TH = 800.0, 200.0              # counts per ° and per °/s (positive axis = nose down, rounds D/E)
# feed-forward "pull the stick" (run 3 with 2500: only 6-7° on the ground). 2026-10-30 (pete: "pulls too early and too
# hard"): 5000 + 3°/s over-rotates (8.9° at liftoff with 5° commanded, nose falls back = FM 6-5 "dynamic overshoot").
# Tried 3000 + 2°/s: same overshoot on the ground and a weak climb-out (5-7° pitch at 5-7 ft up to 230 kt) -> reverted;
# open: redesign the rotation as a pitch-rate command (≈ 2°/s) instead of attitude + feed-forward
FF_TH = 5000.0
LIM_RUD, LIM_PULL, LIM_PUSH = 8000, 12000, 3000
KP_B, KD_B = 250.0, 150.0                # aileron on bank (landing_test.py; +axis increases raw bank)
THETA_CLIMB = 15.0                       # [S] climb-out attitude
ap_on = False                            # AP only at the end (1 500 ft), not in the climb-out (trim-based, too slow)
res = {"start": s0, "liftoff": None, "first_air": None, "theta_max_gnd": 0.0, "vr_t": None}
prev = state()
t0 = prev["t"]
theta_cmd = 0.0
gear_up = flaps_up = False
aborted = ""
air_since = None
dist = 0.0
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "ias", "gnd", "theta", "theta_cmd", "hdg_err", "agl", "dist_ft", "gs", "cmd_elev", "cmd_rud"])
    while True:
        s = state(full=not prev["gnd"] or res["liftoff"] is not None)
        dt = max(s["t"] - prev["t"], 0.02)
        err_h = wrap(hdg0 - s["hdg"])
        r = wrap(s["hdg"] - prev["hdg"]) / dt
        q = (s["theta"] - prev["theta"]) / dt
        if s["ias"] >= vr and res["vr_t"] is None:
            res["vr_t"] = s["t"] - t0
        if res["vr_t"] is not None:
            theta_cmd = min(THETA_CLIMB if res["liftoff"] else theta_target, theta_cmd + (2.0 if res["liftoff"] else 3.0) * dt)
            if s["gnd"]:
                theta_cmd = min(theta_cmd, 11.0)       # tail touches at 12.3°
        cmd_rud = -(KP_HDG * err_h - KD_HDG * r) if res["liftoff"] is None or s["agl"] < 50 else 0.0
        cmd_rud = max(-LIM_RUD, min(LIM_RUD, cmd_rud))
        cmd_elev = 0.0
        if res["vr_t"] is not None and res["first_air"] is None and QROT:
            # pitch-rate rotation: q_cmd ≤ 2°/s, reduced to 0 approaching the target attitude (no overshoot); PI on the
            # filtered pitch rate, the integral finds the stick position (FM 6-5: smooth back stick, no fast input)
            # v2 (after qrot1 pushed the nose down): never push during the rotation (output pull..0), lower gains,
            # integrate only while not saturated at 0
            res["qf"] = 0.6 * res.get("qf", 0.0) + 0.4 * q
            q_cmd = max(0.0, min(2.0, 0.8 * (theta_target - s["theta"])))
            e_q = q_cmd - res["qf"]
            raw = -(300.0 * e_q + 1000.0 * res.get("iq", 0.0))
            if raw < 0 or e_q > 0:
                res["iq"] = max(0.0, min(6.0, res.get("iq", 0.0) + e_q * dt))
            cmd_elev = max(-LIM_PULL, min(0.0, -(300.0 * e_q + 1000.0 * res["iq"])))
            if TAXI and (s["theta"] >= 2.5 or s["ias"] >= 165):                # well below liftoff (≈ 170 kt)
                aborted = f"taxi test end at {s['ias']:.0f} kt, pitch {s['theta']:.1f}°"
            theta_cmd = s["theta"]                      # airborne attitude ramp starts from the actual attitude
        elif res["vr_t"] is not None and res["first_air"] is None:
            cmd_elev = -(FF_TH + KP_TH * (theta_cmd - s["theta"]) - KD_TH * q)
            cmd_elev = max(-LIM_PULL, min(LIM_PUSH, cmd_elev))
        # fallback only well clear of the ground (2026-10-30: a pitch dip to -0.8° at 4 ft handed over to the slow AP and
        # left the elevator at 0 while the jet bounced along the runway)
        elif res["first_air"] is not None and not ap_on and s["agl"] > 100 and (abs(s["bank"]) > 20 or not 0 < s["theta"] < 25):
            # fallback (hand-flown climb-out unstable): old AP handover, vertical speed mode + heading hold
            axis("AXIS_ELEVATOR_SET", 0)
            axis("AXIS_AILERONS_SET", 0)
            ev["HEADING_BUG_SET"](int(round(hdg0)) % 360)
            ev["AP_ALT_VAR_SET_ENGLISH"](int(aq.get("PLANE_ALTITUDE") or 0) + 3000)
            ev["AP_VS_VAR_SET_ENGLISH"](4000)
            if aq.get("AUTOPILOT_MASTER") != 1:
                ev["AP_MASTER"]()
            ev["AP_PANEL_VS_ON"]()
            ev["AP_HDG_HOLD_ON"]()
            ap_on = True
            print(f"FALLBACK to AP at {s['agl']:.0f} ft, {s['ias']:.0f} kt: bank {s['bank']:.0f}°, pitch {s['theta']:.0f}°")
        elif res["first_air"] is not None and not ap_on:
            # airborne: the ground-run gains oscillate at ~3 Hz in the air -> half gains, scaled with 1/q, no feed-forward
            # beyond the trim-equivalent share
            ks = max(0.25, min(1.0, (185.0 / max(s["ias"], 100.0)) ** 2))
            # 2026-10-30 (pete: "schwingt beim Starten"): 400/150 gave a pitch limit cycle 1° <-> 21° (≈ 1.5 s) - the airborne
            # loop runs at only ≈ 1.3 Hz (more reads) -> lower gains
            cmd_elev = -(0.5 * FF_TH * ks + ks * (200.0 * (theta_cmd - s["theta"]) - 60.0 * q))
            cmd_elev = max(-LIM_PULL, min(LIM_PUSH, cmd_elev))
            p_rate = (s["bank"] - prev["bank"]) / dt
            axis("AXIS_AILERONS_SET", max(-8000, min(8000, -(KP_B * s["bank"] + KD_B * p_rate))))
        axis("AXIS_RUDDER_SET", cmd_rud)
        if not ap_on:
            axis("AXIS_ELEVATOR_SET", cmd_elev)
        dist += s["gs"] * 1.68781 * dt                      # kt -> ft/s
        s["dist"] = dist
        if s["gnd"]:
            res["theta_max_gnd"] = max(res["theta_max_gnd"], s["theta"])
            air_since = None
        elif air_since is None:
            air_since = s
            if res["first_air"] is None:                # first liftoff (run 5 touched down once more afterwards)
                res["first_air"] = s
                print(f"First liftoff: {s['ias']:.0f} kt, pitch {s['theta']:.1f}°, ground roll {dist:.0f} ft")
        elif res["liftoff"] is None and s["t"] - air_since["t"] > 1.0:
            res["liftoff"] = dict(air_since, tt=air_since["t"] - t0)
            print(f"Liftoff: {air_since['ias']:.0f} kt, pitch {air_since['theta']:.1f}°, "
                  f"ground roll {res['liftoff']['dist']:.0f} ft, {res['liftoff']['tt']:.1f} s")
        if res["liftoff"] and s["agl"] > 20 and not gear_up:          # FM: gear up when definitely airborne
            ev["GEAR_UP"]()
            ev["THROTTLE1_SET"](11141)                                 # Military: gear up before 260 KIAS
            gear_up = True
            print(f"Gear up at {s['ias']:.0f} KIAS, {s['agl']:.0f} ft")
        if gear_up and s["ias"] >= 260 and s["agl"] > 300 and not flaps_up:   # FM: flaps UP at ≥ 260 KIAS
            ev["FLAPS_UP"]()
            flaps_up = True
            print(f"Flaps up at {s['ias']:.0f} KIAS, {s['agl']:.0f} ft")
        w.writerow([round(s["t"] - t0, 2), round(s["ias"], 1), int(s["gnd"]), round(s["theta"], 2),
                    round(theta_cmd, 2), round(err_h, 2), round(s["agl"]), round(dist), round(s["gs"], 1),
                    int(cmd_elev), int(cmd_rud)])
        f.flush()
        prev = s
        if res["liftoff"] is None and s["gnd"] and abs(err_h) > 10:
            aborted = f"Abort: heading deviation {err_h:.1f}°"
        elif res["liftoff"] is None and s["t"] - t0 > 90:
            aborted = "Abort: 90 s without liftoff"
        if aborted and TAXI and "taxi" in aborted:
            # gentle stop: idle, nose down over 3 s, wheel brakes once the nose is down, heading hold by rudder
            ev["THROTTLE1_SET"](0)
            t_s = time.time()
            while True:
                st = state(full=False)
                eh = wrap(hdg0 - st["hdg"])
                # 2026-10-30 incident: a 0 -> push ramp left the 5° nose-up takeoff trim in charge at ≈ 170 kt -> airborne, 28°.
                # Hold the attitude at 0° actively (push as needed, up to the full nose-down stop)
                axis("AXIS_ELEVATOR_SET", max(0.0, min(16383.0, 3000.0 + 2500.0 * st["theta"])))
                axis("AXIS_RUDDER_SET", max(-LIM_RUD, min(LIM_RUD, -KP_HDG * eh)))
                if st["theta"] < 1.0 and time.time() - t_s > 1.0:
                    ev["AXIS_LEFT_BRAKE_SET"](16383) if ev.get("AXIS_LEFT_BRAKE_SET") else None
                    ev["AXIS_RIGHT_BRAKE_SET"](16383) if ev.get("AXIS_RIGHT_BRAKE_SET") else None
                w.writerow([round(st["t"] - t0, 2), round(st["ias"], 1), int(st["gnd"]), round(st["theta"], 2), 0, round(eh, 2),
                            0, 0, round(st["gs"], 1), 0, 0])
                if st["gs"] < 3 or time.time() - t_s > 60:
                    break
                time.sleep(0.05)
            break
        if aborted:
            ev["THROTTLE1_SET"](0)
            ev["PARKING_BRAKES"]()
            break
        if s["agl"] > 1500 or s["t"] - t0 > 150:
            break
        time.sleep(0.05)

for n in ("AXIS_RUDDER_SET", "AXIS_ELEVATOR_SET", "AXIS_AILERONS_SET"):
    axis(n, 0)
if not aborted:
    # reduced power: with military + ALT hold the jet reached 600 KIAS at 3 000 ft (run 6)
    ev["THROTTLE1_SET"](7000)
    ev["HEADING_BUG_SET"](int(round(hdg0)) % 360)
    ev["AP_ALT_VAR_SET_ENGLISH"](int(aq.get("PLANE_ALTITUDE") or 0) + 3000)
    if aq.get("AUTOPILOT_MASTER") != 1:
        ev["AP_MASTER"]()
    ev["AP_ALT_HOLD_ON"]()
    ev["AP_HDG_HOLD_ON"]()
sm.exit()
lo, fa = res["liftoff"], res["first_air"]
print(aborted or "done", "->", out)
print(f"Vr reached after {res['vr_t']} s; max. pitch on the ground {res['theta_max_gnd']:.1f}° (tail at 12.3°)")
if fa:
    print(f"Result: first liftoff at {fa['ias']:.0f} kt IAS, pitch {fa['theta']:.1f}°, after {fa['dist']:.0f} ft")
if lo:
    print(f"Result: sustained liftoff at {lo['ias']:.0f} kt IAS after {lo['dist']:.0f} ft / {lo['tt']:.1f} s")
