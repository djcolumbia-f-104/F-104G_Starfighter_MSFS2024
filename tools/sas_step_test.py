"""H1 yaw damper washout check: steady pedal-rudder step with the AP wing leveler holding the wings, SAS off vs. on.

Usage (with the Python of the simconnect-mcp venv; jet positioned at 15 000-16 500 ft, M 0.9, AP ALT + wing leveler):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\sas_step_test.py <output.csv> <sas_gain> [rudder_axis=5461] [hold_s=10]
Sequence: yaw damper OFF (sas_gain 0: L:F104_SAS_YAW_OFF 1) or ON with L:F104_SAS_YAW_GAIN = sas_gain, 3 s quiet -> AXIS_RUDDER_SET rudder_axis (5461 = 1/3 = 2° gear up) for hold_s -> 0, 6 s.
Card H1-sas.md: with the washout (tau 1 s) the SAS rudder (L:F104_SAS_YAW_DEG) must decay to ≈ 0 and the steady beta of the
last 3 s of the hold must equal the SAS-off run (bu0: 0.33° beta per rudder degree). End: damper back to the default
(ON, gain 1.0 - FM 2-15/6-4).
Abort: |beta| > 5°, |bank| > 30°, |yaw rate| > 15°/s -> rudder 0, damper OFF (left off).
"""
import csv
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.RequestList import Request

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out, gain = sys.argv[1], float(sys.argv[2])
RUD = int(sys.argv[3]) if len(sys.argv) > 3 else 5461
HOLD = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
DEG = 57.29578

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
rud = AircraftEvents(sm).find("AXIS_RUDDER_SET")
sas_off = Request((b"L:F104_SAS_YAW_OFF", b"number"), sm, _time=0, _settable=True)
sas_gain = Request((b"L:F104_SAS_YAW_GAIN", b"number"), sm, _time=0, _settable=True)
sas_deg = Request((b"L:F104_SAS_YAW_DEG", b"number"), sm, _time=0)
sas_off.value = 0.0 if gain > 0 else 1.0
sas_gain.value = gain if gain > 0 else 0.0
schedule = [(3.0, 0), (3.0 + HOLD, RUD), (9.0 + HOLD, 0)]
rows, aborted, cmd = [], "", None
t0 = time.time()
while (t := time.time() - t0) < schedule[-1][0]:
    want = next(c for until, c in schedule if t < until)
    if want != cmd:
        rud(want)
        cmd = want
    b = (aq.get("INCIDENCE_BETA") or 0) * DEG
    bank = (aq.get("PLANE_BANK_DEGREES") or 0) * DEG
    r = (aq.get("ROTATION_VELOCITY_BODY_Y") or 0) * DEG
    rows.append((round(t, 3), cmd, round(b, 3), round(bank, 2), round(r, 2), round(sas_deg.value or 0, 3)))
    if abs(b) > 5 or abs(bank) > 30 or abs(r) > 15:
        aborted = f"ABORT t {t:.1f}: beta {b:.1f}, bank {bank:.1f}, r {r:.1f}"
        sas_off.value = 1.0
        break
rud(0)
if not aborted:
    sas_off.value = 0.0                                       # default: damper ON, gain 1.0
    sas_gain.value = 0.0
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "cmd_rud", "beta_deg", "bank_deg", "yaw_rate_dps", "sas_rud_deg"])
    w.writerows(rows)
print(f"{len(rows)} samples ({len(rows) / max(rows[-1][0], 1e-3):.1f} Hz) -> {out}")
if aborted:
    print(aborted)


def mean(sel, i):
    v = [r[i] for r in rows if sel(r[0])]
    return sum(v) / len(v) if v else float("nan")


h0, h1 = 3.0, 3.0 + HOLD
print(f"gain {gain}: steady (last 3 s of the hold) beta {mean(lambda t: h1 - 3 <= t < h1, 2):+.3f}°, "
      f"bank {mean(lambda t: h1 - 3 <= t < h1, 3):+.2f}°, SAS rudder {mean(lambda t: h1 - 3 <= t < h1, 5):+.3f}°")
print(f"SAS rudder peak during the hold {min((r[5] for r in rows if h0 <= r[0] < h1), default=0):+.2f} / "
      f"{max((r[5] for r in rows if h0 <= r[0] < h1), default=0):+.2f}°; max |beta| {max(abs(r[2]) for r in rows):.2f}°")

# postconditions (test process step 6, tools/post.py): jet in a safe, defined state after the script
post = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.py"), "air"],
                      capture_output=True, text=True, timeout=60)
print((post.stdout.strip().splitlines() or ["POST FAIL: no output"])[-1])
