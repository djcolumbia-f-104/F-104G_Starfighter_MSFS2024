"""Test T3-L: scripted approach and landing on EDDM runway 26L (Claude flies, AP-assisted).

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\landing_test.py <output.csv> [start_nm=6] [glide_deg=3]
Sequence: gear down + LAND flaps, reposition on the extended centreline start_nm before the threshold on the glide
path -> AP heading hold (heading bug steered from the cross-track error) + AP vertical speed (glide path) + throttle
loop on the FM final approach speed (Fig. A8-2: 170 KIAS up to 15 000 lb, +5 kt per 1 000 lb) -> flare: 60 ft AGL
VS -300 ft/min, thrust to ~83 % N1 (FM 2-25) -> touchdown: idle, AP off, nose down, after 2 s drag chute (ground spoiler
drag, cfg) + hard wheel braking -> stop.
Go-around (full AB, AP VS +3000, flaps TAKEOFF) if |cross-track| > 300 ft or |bank| > 30° below 500 ft AGL, or
glide path error > 300 ft below 400 ft AGL.
Results: touchdown IAS, sink rate, pitch, distance past the threshold; ground roll to a stop; CSV log.
"""
import csv
import math
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8")
out = sys.argv[1]
start_nm = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
glide = math.radians(float(sys.argv[3]) if len(sys.argv) > 3 else 3.0)
DEG = 57.29578
FT_PER_DEG = 60 * 6076.12
LAT0, LON0, HDG = 48.34472097713059, 11.803858844132039, 263.4     # 26L threshold = T3-D start position
AIM_FT = 1000.0                                                     # aim point past the threshold

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


h = math.radians(HDG)
U = (math.sin(h), math.cos(h))          # runway direction (east, north)
R = (math.cos(h), -math.sin(h))         # right of the runway direction


def track(lat, lon):
    """-> along-track distance past the threshold (ft, negative before it), cross-track (ft, + = right of centreline)"""
    n = (lat - LAT0) * FT_PER_DEG
    e = (lon - LON0) * FT_PER_DEG * math.cos(math.radians(LAT0))
    return e * U[0] + n * U[1], e * R[0] + n * R[1]


# --- set up: ground elevation from the threshold, weight -> speeds
elev = None
w = g("TOTAL_WEIGHT")
v_app = 170 + 5 * max(0.0, w / 1000 - 15)                            # FM Fig. A8-2 final approach, LAND flaps
v_td = 152 + 5 * max(0.0, w / 1000 - 15)                             # normal touchdown (lower edge)
start_ft = start_nm * 6076.12
lat_s = LAT0 - start_ft * U[1] / FT_PER_DEG
lon_s = LON0 - start_ft * U[0] / (FT_PER_DEG * math.cos(math.radians(LAT0)))
ev("GEAR_DOWN")
ev("FLAPS_DOWN")
for _ in range(3):
    if g("AUTOPILOT_MASTER") == 1:
        break
    ev("AP_MASTER")
    time.sleep(0.7)
field_elev = 1457.0                                                  # EDDM 26L ground (T3-D: 1461.6 ft MSL - 4.3 ft CG)
alt0 = field_elev + (start_ft + AIM_FT) * math.tan(glide)
ev("HEADING_BUG_SET", int(round(HDG)) % 360)
ev("AP_HDG_HOLD_ON")
ev("AP_ALT_VAR_SET_ENGLISH", int(field_elev) - 1000)                 # VS mode must not capture an altitude
ev("AP_VS_VAR_SET_ENGLISH", -int(v_app * 101.27 * math.tan(glide)))
ev("AP_PANEL_VS_ON")
sm.set_pos(alt0, lat_s, lon_s, int(v_app * 1.05), 0.0, 0.0, HDG, 0)
time.sleep(1.0)
ev("GEAR_DOWN")                                                      # AFTER set_pos: positioning in the air
ev("FLAPS_DOWN")                                                     # retracts the gear (landings 1/3 were belly landings)
ev("THROTTLE1_SET", 9500)
print(f"weight {w:.0f} lb -> final approach {v_app:.0f} KIAS, touchdown {v_td:.0f} KIAS; start {start_nm} NM, {alt0:.0f} ft MSL")

thr = 9500.0
phase = "approach"
res = {}
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
    agl, ias, gnd = g("PLANE_ALT_ABOVE_GROUND"), g("AIRSPEED_INDICATED"), g("SIM_ON_GROUND") == 1
    alt, bank = g("PLANE_ALTITUDE"), g("PLANE_BANK_DEGREES") * DEG
    vs = (alt - res.get("prev_alt", alt)) / dt * 60                 # ft/min from altitude (VERTICAL_SPEED unit unclear)
    res["prev_alt"] = alt
    gs_kt = g("GROUND_VELOCITY")
    path_alt = field_elev + (AIM_FT - s) * math.tan(glide)
    path_err = alt - path_alt                                        # + = above the glide path

    if phase in ("approach", "flare"):
        if phase == "approach":
            # glide path: nominal VS for the ground speed, corrected by the path error (1 ft/min per 0.25 ft, ±800)
            vs_cmd = -gs_kt * 101.27 * math.tan(glide) - max(-800, min(800, 4.0 * path_err))
            ev("AP_VS_VAR_SET_ENGLISH", int(vs_cmd))
            # PI throttle with feed-forward (run 1: pure integrator 120/kt/s oscillated 160-220 kt)
            err = v_app - ias
            res["i_spd"] = max(-60.0, min(60.0, res.get("i_spd", 0.0) + err * dt))
            thr = max(2000.0, min(11141.0, 9000.0 + 250.0 * err + 25.0 * res["i_spd"]))
            if s > -12000 and g("GEAR_TOTAL_PCT_EXTENDED") < 0.99 and not res.get("gear_go"):
                res["gear_go"] = True                                    # gear not down 2 NM out -> go around
                print(f"GEAR NOT DOWN ({g('GEAR_TOTAL_PCT_EXTENDED'):.2f}) at {s:.0f} ft")
            if agl < 100:
                phase = "flare"
                ev("AP_VS_VAR_SET_ENGLISH", -400)
                print(f"flare at {agl:.0f} ft AGL, {ias:.0f} KIAS, {s:.0f} ft from the threshold, path error {path_err:+.0f} ft")
        if phase == "flare":
            # FM 2-25: smooth thrust reduction to 82-83 % rpm in the flare (80 % to bleed ~15 kt), idle at touchdown;
            # sink rate eased from -400 (100 ft) to -150 ft/min (30 ft)
            thr = max(0.0, min(11141.0, thr + 300.0 * (80.0 - g("TURB_ENG_N1:1")) * dt))
            ev("AP_VS_VAR_SET_ENGLISH", int(-150 - 250 * max(0.0, min(1.0, (agl - 30) / 70))))
        ev("THROTTLE1_SET", int(thr))
        # localizer: heading bug = runway heading - 0.05°/ft cross-track (±15°)
        ev("HEADING_BUG_SET", int(round(HDG - max(-15, min(15, 0.05 * c)))) % 360)
        bad = (agl < 500 and (abs(c) > 300 or abs(bank) > 30)) or (agl < 400 and path_err < -300) or res.get("gear_go")
        if bad and not gnd:
            phase = "go-around"
            ev("THROTTLE1_SET", 16383)
            ev("FLAPS_1")
            ev("AP_VS_VAR_SET_ENGLISH", 3000)
            ev("AP_ALT_VAR_SET_ENGLISH", int(field_elev + 3000))
            print(f"GO-AROUND: AGL {agl:.0f}, cross-track {c:.0f} ft, bank {bank:.0f}°, path error {path_err:+.0f} ft")
        if gnd:
            phase = "rollout"
            res["td"] = dict(ias=ias, vs=res.get("last_vs", vs), pitch=-g("PLANE_PITCH_DEGREES") * DEG, s=s, c=c,
                             gear=g("GEAR_TOTAL_PCT_EXTENDED"),
                             t=t - t0)
            if g("AUTOPILOT_MASTER") == 1:
                ev("AP_MASTER")
            ev("THROTTLE1_SET", 0)
            res["t_td"] = t
            print(f"TOUCHDOWN {ias:.0f} KIAS, gear {res['td']['gear']:.0%}, sink {res['td']['vs']:.0f} ft/min, pitch {res['td']['pitch']:.1f}°, "
                  f"{s:.0f} ft past the threshold, {c:+.0f} ft off the centreline")
        res["last_vs"] = vs
    elif phase == "rollout":
        roll += gs_kt * 1.68781 * dt
        ev("AXIS_ELEVATOR_SET", 4000)                                # FM 2-25: lower the nose wheel at once
        if not res.get("chute") and t - res["t_td"] > 2.0:              # nose wheel down -> drag chute
            ev("SPOILERS_ON")                                         # = drag chute (ground spoiler drag, cfg)
            res["chute"] = ias
            print(f"drag chute at {ias:.0f} KIAS (limit 180 MB-7G / 205 BS-4000)")
        ev("AXIS_RUDDER_SET", int(max(-8000, min(8000, -700 * ((HDG - g("PLANE_HEADING_DEGREES_TRUE") * DEG + 180) % 360 - 180) - 3 * c))))
        if True:                                                      # FM A8-3/A8-4: hard braking during the stop
            ev("AXIS_LEFT_BRAKE_SET", 16383)
            ev("AXIS_RIGHT_BRAKE_SET", 16383)
        if gs_kt < 3:
            res["roll"] = roll
            break
    elif phase == "go-around":
        if agl > 1500:
            break
    rows.append([round(t - t0, 2), phase, round(s), round(c), round(agl), round(ias, 1), round(vs), round(bank, 1),
                 round(path_err), int(thr)])
    time.sleep(0.05)

for n in ("AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET"):
    ev(n, 0)
if phase == "rollout" or "roll" in res:
    ev("PARKING_BRAKES") if g("BRAKE_PARKING_POSITION") != 1 else None
    ev("AXIS_LEFT_BRAKE_SET", -16383)
    ev("AXIS_RIGHT_BRAKE_SET", -16383)
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["t", "phase", "along_ft", "cross_ft", "agl", "ias", "vs_fpm", "bank", "path_err_ft", "throttle"])
    wr.writerows(rows)
print(f"{len(rows)} samples ({len(rows) / max(rows[-1][0], 1):.1f} Hz) -> {out}" if rows else "no samples")
if "td" in res:
    print(f"Result: touchdown {res['td']['ias']:.0f} KIAS (FM normal {v_td:.0f}-{v_td + 5:.0f}), "
          f"{res['td']['s']:.0f} ft past the threshold, ground roll {res.get('roll', float('nan')):.0f} ft")
else:
    print(f"Result: no touchdown (phase {phase})")
