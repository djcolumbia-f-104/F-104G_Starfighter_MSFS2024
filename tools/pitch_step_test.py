"""Short period (SAS off): stabilizer step through the TRIM, alpha logged fast, card H1-sas.md (pitch).

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE in level flight on the AP - never from the ground):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\pitch_step_test.py <output.csv> [amp_deg=0.2] [hold_s=4]
Sequence: AP off (the trim stays at the AP's level trim), stick neutral, 3 s quiet -> trim +amp (nose up) for hold_s ->
back to trim0 for hold_s -> trim0, MCP `position` routine (16 500 ft, AP). Only INCIDENCE_ALPHA is read during the steps
(≈ 20 Hz distinct values; the library returns repeated values between sim updates - deduplicated).
Why the trim and alpha (2026-11-03): the trim is the damper channel (1 trim° = 1 stab°, symmetric; the stick gearing
is 17° up / 5° down) and ROTATION_VELOCITY_BODY_X reads ≈ 3.5x the true pitch rate (∫q vs. Δθ) - not usable.
Evaluation per step (up and down): fit alpha(t) = c0 + c1 t + exp(-sigma t)(A cos wd t + B sin wd t) over 3 s from the
step -> omega_n, zeta; alpha_ss/delta from the mean of the last second of each hold.
References (CR-2144 Table III-5, SAS off, 16 300 lb, CG 0.07): F/C 4 15 000 ft M 0.9 zeta 0.289 wn 4.54; F/C 5 35 000 ft
M 0.6 0.165 / 1.91; F/C 6 35 000 ft M 0.9 0.185 / 3.53; F/C 7 35 000 ft M 1.2 0.125 / 5.78.
Abort: |alpha - alpha0| > 4°, |pitch| > 20° -> trim0, position routine.
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
AMP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
HOLD = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
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


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 1800:
    sm.exit()
    sys.exit("ABORT: on the ground or fuel < 1 800 lb")
for _ in range(3):
    if g("AUTOPILOT_MASTER") != 1:
        break
    ev("AP_MASTER")
    time.sleep(0.3)
ev("AXIS_ELEVATOR_SET", 0)
trim0 = g("ELEVATOR_TRIM_POSITION") * DEG
cond = (f"{g('PLANE_ALTITUDE'):.0f} ft / {g('AIRSPEED_INDICATED'):.0f} KIAS / M {g('AIRSPEED_MACH'):.3f} / q "
        f"{g('DYNAMIC_PRESSURE') / 32.174:.0f} psf, weight {g('TOTAL_WEIGHT'):.0f} lb, CG {g('CG_PERCENT') * 100:.1f} % MAC, "
        f"trim0 {trim0:.2f}°, AP {g('AUTOPILOT_MASTER'):.0f}")
print(f"pitch step {AMP:+.2f}° x {HOLD} s at {cond}")

schedule = [(3.0, 0.0), (3.0 + HOLD, AMP), (3.0 + 2 * HOLD, 0.0)]
rows, reason, cmd = [], "done", None
a0 = g("INCIDENCE_ALPHA") * DEG
t0 = time.time()
while (t := time.time() - t0) < schedule[-1][0]:
    want = next(c for until, c in schedule if t < until)
    if want != cmd:
        set_trim(trim0 + want)
        cmd = want
    a = g("INCIDENCE_ALPHA") * DEG
    if not rows or a != rows[-1][2]:
        rows.append((round(t, 3), cmd, a))
    if abs(a - a0) > 4:
        reason = f"ABORT t {t:.1f}: alpha {a:.1f}° (start {a0:.1f}°)"
        break
set_trim(trim0)
pitch = -g("PLANE_PITCH_DEGREES") * DEG
end = f"end {g('PLANE_ALTITUDE'):.0f} ft, {g('AIRSPEED_INDICATED'):.0f} KIAS, pitch {pitch:.1f}°"
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "trim_cmd_delta", "alpha_deg"])
    w.writerows(rows)
print(f"{reason}; {len(rows)} distinct samples ({len(rows) / max(rows[-1][0], 1e-3):.1f} Hz) -> {out}; {end}")


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
    """Grid over sigma (0.05..6 1/s) and wd (1..9 rad/s), linear least squares for c0, c1, A, B."""
    best = None
    for si in range(1, 121):
        s = si * 0.05
        for wi in range(50, 451):
            wd = wi * 0.02
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
    for k, (t_step, d_cmd) in enumerate([(3.0, AMP), (3.0 + HOLD, -AMP)]):
        seg = [(r[0] - t_step, r[2]) for r in rows if t_step + 0.02 <= r[0] <= t_step + 3.0]
        before = [r[2] for r in rows if t_step - 1.0 <= r[0] < t_step]
        res, s, wd, c = fit([x[0] for x in seg], [x[1] for x in seg])
        # short-period equilibrium = fit asymptote c0 (the mean of the last second also contains the phugoid drift)
        d_ss = c[0] - sum(before) / len(before)
        wn = math.hypot(s, wd)
        print(f"step {'up' if k == 0 else 'down'}: fit ({len(seg)} samples, rms {math.sqrt(res / len(seg)):.4f}°) "
              f"zeta {s / wn:.3f}, omega_n {wn:.2f} rad/s (period {2 * math.pi / wd:.2f} s, "
              f"{math.exp(-s * 2 * math.pi / wd):.2f} per cycle); alpha_ss/delta {d_ss / d_cmd:.2f}")

pos = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "mcp_f104", "sim_actions.py"),
                      "position", "16500", "520", "263", "48.36", "11.9", "8000", "wl"],
                     capture_output=True, text=True, timeout=120)
print("End: position routine ->", (pos.stdout.strip().splitlines() or ["no output"])[-1][:140])
