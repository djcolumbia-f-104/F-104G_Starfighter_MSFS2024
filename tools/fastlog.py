"""High-rate logger for a few SimVars (H2 kicker shape, any short event): the fewer variables, the faster (≈ 70 ms per read).

Usage (with the Python of the simconnect-mcp venv, in the background next to a test script):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\fastlog.py <output.csv> <seconds> [VAR ...]
Default variables: INCIDENCE_ALPHA (deg), ELEVATOR_POSITION, YOKE_Y_POSITION, AIRSPEED_INDICATED. Radian SimVars listed in
RAD are converted to degrees. Failed reads are written as empty fields (never as 0).
"""
import csv
import sys
import time

from SimConnect import AircraftRequests, SimConnect

out, dur = sys.argv[1], float(sys.argv[2])
VARS = sys.argv[3:] or ["INCIDENCE_ALPHA", "ELEVATOR_POSITION", "YOKE_Y_POSITION", "AIRSPEED_INDICATED"]
RAD = {"INCIDENCE_ALPHA", "PLANE_PITCH_DEGREES", "ELEVATOR_DEFLECTION", "ELEVATOR_TRIM_POSITION"}
DEG = 57.29578

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
t0 = time.time()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t"] + VARS)
    while time.time() - t0 < dur:
        row = [round(time.time() - t0, 3)]
        for n in VARS:
            v = aq.get(n)
            row.append("" if v is None else round(v * DEG if n in RAD else v, 4))
        w.writerow(row)
        f.flush()
sm.exit()
