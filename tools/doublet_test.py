"""Test T3-J: rudder doublet (Dutch roll) with fast logging of sideslip, bank and yaw rate.

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\doublet_test.py <output.csv> [seconds=30]
Precondition: steady flight, AP altitude hold + wing leveler (no heading hold), yaw damper as wanted.
Sequence: 3 s quiet -> full right rudder 1 s -> full left rudder 1 s -> rudder free, log until the end.
Only 4 SimVars per sample (simlog.py with 26 SimVars reaches only ~0.7 Hz, too slow for a ~2-3 s period).
Prints the sideslip peaks after the doublet: period and ratio of successive peaks (damping).
"""
import csv
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect

sys.stdout.reconfigure(encoding="utf-8")
out = sys.argv[1]
seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
DEG = 57.29578
sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
rud = AircraftEvents(sm).find("AXIS_RUDDER_SET")
rows = []
t0 = time.time()
schedule = [(3.0, 0), (4.0, 16383), (5.0, -16383)]          # (until t, rudder axis)
cmd = None
while (t := time.time() - t0) < seconds:
    want = next((c for until, c in schedule if t < until), 0)
    if want != cmd:
        rud(want)
        cmd = want
    rows.append((round(t, 3), (aq.get("INCIDENCE_BETA") or 0) * DEG, (aq.get("PLANE_BANK_DEGREES") or 0) * DEG,
                 (aq.get("ROTATION_VELOCITY_BODY_Y") or 0) * DEG, cmd, (aq.get("RUDDER_DEFLECTION") or 0) * DEG))
rud(0)
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "beta_deg", "bank_deg", "yaw_rate_dps", "cmd_rud", "rudder_deg"])
    w.writerows(rows)
print(f"{len(rows)} samples ({len(rows) / seconds:.1f} Hz) -> {out}")
# peaks of |beta| after the doublet (local extrema with sign change in between)
free = [r for r in rows if r[0] > 5.0]
peaks = []
for a, b, c in zip(free, free[1:], free[2:]):
    if abs(b[1]) >= abs(a[1]) and abs(b[1]) >= abs(c[1]) and abs(b[1]) > 0.05:
        if not peaks or (peaks[-1][1] > 0) != (b[1] > 0):
            peaks.append((b[0], b[1]))
for t, v in peaks[:8]:
    print(f"peak t {t:6.2f} s  beta {v:+.2f}°")
if len(peaks) >= 3:
    period = (peaks[2][0] - peaks[0][0])
    ratio = abs(peaks[2][1] / peaks[0][1])
    print(f"period ≈ {period:.2f} s, amplitude ratio per cycle ≈ {ratio:.2f}")
