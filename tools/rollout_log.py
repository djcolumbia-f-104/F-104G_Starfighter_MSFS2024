"""High-rate rollout logger for the landing ground roll (F2/F3): few SimVars so it runs much faster than simlog.py.

Usage (with the Python of the simconnect-mcp venv, in the background before landing_test.py):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\rollout_log.py <output.csv> [seconds=420]
Writes only while the jet is below 500 ft AGL (approach end, flare, touchdown, rollout). Columns: t, IAS, ground speed,
on ground, pitch (nose up +), gear compression nose/left/right, brake positions, body longitudinal acceleration,
throttle, N1, net thrust.
"""
import csv
import sys
import time

from SimConnect import AircraftRequests, SimConnect

out = sys.argv[1]
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 420.0
DEG = 57.29578
VARS = ["AIRSPEED_INDICATED", "GROUND_VELOCITY", "SIM_ON_GROUND", "PLANE_PITCH_DEGREES", "CONTACT_POINT_COMPRESSION:0",
        "CONTACT_POINT_COMPRESSION:1", "CONTACT_POINT_COMPRESSION:2", "BRAKE_LEFT_POSITION", "BRAKE_RIGHT_POSITION",
        "ACCELERATION_BODY_Z", "GENERAL_ENG_THROTTLE_LEVER_POSITION:1", "TURB_ENG_N1:1", "TURB_ENG_JET_THRUST:1"]

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
t0 = time.time()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "ias", "gs", "gnd", "pitch", "comp_nose", "comp_l", "comp_r", "brake_l", "brake_r", "ax_body_fps2",
                "throttle", "n1", "thrust"])
    while time.time() - t0 < dur:
        agl = aq.get("PLANE_ALT_ABOVE_GROUND") or 0
        if agl > 500:
            time.sleep(0.5)
            continue
        v = [aq.get(n) or 0 for n in VARS]
        v[3] = -v[3] * DEG
        w.writerow([round(time.time() - t0, 2)] + [round(x, 4) for x in v])
        f.flush()
        if v[2] == 1 and v[1] < 2:
            break
sm.exit()
