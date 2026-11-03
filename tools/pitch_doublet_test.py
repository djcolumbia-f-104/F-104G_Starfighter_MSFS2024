"""H1 pitch: short-period doublet through the stabilizer TRIM (the pitch-damper channel), card H1-sas.md.

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE in level flight on the AP at ≈ 16 000 ft, M 0.9 - e.g.
right after takeoff_test.py; never from the ground):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\pitch_doublet_test.py <output.csv> [amp_deg=0.5] [half_s=0.4]
Sequence: AP off (trim stays at the AP's level trim), stick neutral, 3 s quiet -> trim +amp for half_s (nose up),
-amp for half_s, back to trim0 -> 7 s free response (only pitch rate and alpha read, ≈ 12 Hz) -> MCP `position` routine.
Reference CR-2144 Table III-5 F/C 4 (15 000 ft, M 0.9, SAS off): short period zeta 0.289, omega_n 4.54 rad/s
(F/C 6 35 000 ft M 0.9: 0.185 / 3.53). Evaluation: fit of the free pitch-rate response (from 0.15 s after the input)
q(t) = c0 + c1 t + exp(-sigma t) (A cos wd t + B sin wd t), grid over sigma/wd, linear least squares for the rest.
Abort: |q| > 15°/s, |pitch| > 20°, IAS outside 380-540 -> trim0, position routine.
"""
import csv
import math
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
AMP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
HALF = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
DEG = 57.29578

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def g(name):
    return aq.get(name) or 0


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def set_trim(deg):
    aq.set("ELEVATOR_TRIM_POSITION", deg / DEG)


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 2000:
    sm.exit()
    sys.exit("ABORT: on the ground or fuel < 2 000 lb")
for _ in range(3):
    if g("AUTOPILOT_MASTER") != 1:
        break
    ev("AP_MASTER")
    time.sleep(0.3)
ev("AXIS_ELEVATOR_SET", 0)
trim0 = g("ELEVATOR_TRIM_POSITION") * DEG
print(f"pitch doublet at {g('PLANE_ALTITUDE'):.0f} ft / {g('AIRSPEED_INDICATED'):.0f} KIAS / M {g('AIRSPEED_MACH'):.3f}, "
      f"weight {g('TOTAL_WEIGHT'):.0f} lb, CG {g('CG_PERCENT') * 100:.1f} % MAC, trim0 {trim0:.2f}°, AP "
      f"{g('AUTOPILOT_MASTER'):.0f}; amp ±{AMP}° x {HALF} s")

rows, reason = [], "done"
schedule = [(3.0, 0.0), (3.0 + HALF, AMP), (3.0 + 2 * HALF, -AMP), (10.0 + 2 * HALF, 0.0)]
t0 = time.time()
cmd = None
while (t := time.time() - t0) < schedule[-1][0]:
    want = next(c for until, c in schedule if t < until)
    if want != cmd:
        set_trim(trim0 + want)
        cmd = want
    q = g("ROTATION_VELOCITY_BODY_X") * DEG
    a = g("INCIDENCE_ALPHA") * DEG
    th = -g("PLANE_PITCH_DEGREES") * DEG                     # nose up positive; cross-check of q (2026-11-03)
    rows.append((round(t, 3), cmd, q, a, th))
    if abs(q) > 15:
        reason = f"ABORT t {t:.1f}: pitch rate {q:.1f}°/s"
        break
    if len(rows) % 25 == 0:
        pitch, ias = -g("PLANE_PITCH_DEGREES") * DEG, g("AIRSPEED_INDICATED")
        if abs(pitch) > 20 or not 380 < ias < 540:
            reason = f"ABORT t {t:.1f}: pitch {pitch:.1f}°, IAS {ias:.0f}"
            break
set_trim(trim0)
end_state = (g("PLANE_ALTITUDE"), g("AIRSPEED_INDICATED"), -g("PLANE_PITCH_DEGREES") * DEG)
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "trim_cmd_delta", "q_body_x_dps", "alpha_deg", "pitch_deg"])
    w.writerows(rows)
print(f"{reason}; {len(rows)} samples ({len(rows) / max(rows[-1][0], 1e-3):.1f} Hz) -> {out}; end alt {end_state[0]:.0f} "
      f"ft, {end_state[1]:.0f} KIAS, pitch {end_state[2]:.1f}°")


def solve(m, v):
    """Gaussian elimination for the small normal equations."""
    n = len(v)
    a = [row[:] + [v[i]] for i, row in enumerate(m)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        if abs(a[c][c]) < 1e-12:
            return None
        for r in range(n):
            if r != c:
                k = a[r][c] / a[c][c]
                a[r] = [x - k * y for x, y in zip(a[r], a[c])]
    return [a[i][n] / a[i][i] for i in range(n)]


def fit(ts, ys):
    best = None
    for si in range(1, 121):
        s = si * 0.05                                   # sigma 0.05 .. 6 1/s
        for wi in range(100, 401):
            wd = wi * 0.02                              # wd 2 .. 8 rad/s
            basis = [[1.0, t, math.exp(-s * t) * math.cos(wd * t), math.exp(-s * t) * math.sin(wd * t)] for t in ts]
            m = [[sum(b[i] * b[j] for b in basis) for j in range(4)] for i in range(4)]
            v = [sum(b[i] * y for b, y in zip(basis, ys)) for i in range(4)]
            c = solve(m, v)
            if c is None:
                continue
            res = sum((y - sum(ci * bi for ci, bi in zip(c, b))) ** 2 for b, y in zip(basis, ys))
            if best is None or res < best[0]:
                best = (res, s, wd, c)
    return best


if reason == "done":
    t_free = 3.0 + 2 * HALF + 0.15
    free = [(r[0] - t_free, r[2]) for r in rows if t_free <= r[0] <= t_free + 4.0]
    peak = max(abs(r[2]) for r in rows)
    res, s, wd, c = fit([x[0] for x in free], [x[1] for x in free])
    wn = math.hypot(s, wd)
    rms = math.sqrt(res / len(free))
    print(f"peak |q| {peak:.2f}°/s; free response fit ({len(free)} samples, rms {rms:.3f}°/s): sigma {s:.2f} 1/s, "
          f"wd {wd:.2f} rad/s -> zeta {s / wn:.3f}, omega_n {wn:.2f} rad/s, period {2 * math.pi / wd:.2f} s, "
          f"amplitude ratio per cycle {math.exp(-s * 2 * math.pi / wd):.3f}")
    print("CR-2144 F/C 4 (SAS off): zeta 0.289, omega_n 4.54 rad/s, period 1.44 s, ratio per cycle 0.15")

pos = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "mcp_f104", "sim_actions.py"),
                      "position", "16500", "520", "263", "48.36", "11.9", "8000", "wl"],
                     capture_output=True, text=True, timeout=120)
print("End: position routine ->", (pos.stdout.strip().splitlines() or ["no output"])[-1][:140])
