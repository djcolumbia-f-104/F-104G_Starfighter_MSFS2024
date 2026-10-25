"""Test T3-H: excess thrust (climb potential) in the sim from a level max-afterburner acceleration vs. NASA TN D-6398.

Usage: analyse_climb.py <project folder> <flighttest.csv> [t_from t_to]   (CSV from tools/simlog.py)
Energy balance: Fn,ex = Fn - D = W/g·dV/dt + W·sin γ  (dV/dt, γ from true airspeed and altitude, central differences
over ±2 points). Corrected to the NASA weight of 18 000 lb via the induced drag: D_i = K·W²/(q·S), K = 0.194 (D-7137
polar, flight-model-values.md). Compared with docs/data/nasa_d6398_excess_thrust_lbf.csv at the nearest tabulated
altitude (only points within ±1 500 ft of 10 000 or 20 000 ft). Climb potential = Fn,ex·V/W.
Only points in the air, flaps/gear up, throttle at full afterburner. Acceptance: |Fn,ex sim/NASA - 1| <= 10 %
on Mach band means (D-6398: predicted vs. measured within 10 %).
"""
import csv
import os
import sys

S = 196.1
KT = 1.68781
G0 = 32.174
K_IND = 0.194
W_REF = 18000.0
TOL = 0.10

sys.stdout.reconfigure(encoding="utf-8")
root, path = sys.argv[1], sys.argv[2]
t_from = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
t_to = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9

with open(os.path.join(root, "docs", "data", "nasa_d6398_excess_thrust_lbf.csv"), encoding="utf-8") as f:
    rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
alts = [float(h[1:]) for h in rows[0][1:]]
ref = {h: [(float(r[0]), float(r[j + 1])) for r in rows[1:] if r[j + 1]] for j, h in enumerate(alts)}


def fnex_nasa(alt, mach):
    pts = ref[alt]
    if not pts[0][0] <= mach <= pts[-1][0]:
        return None
    for (m0, f0), (m1, f1) in zip(pts, pts[1:]):
        if m0 <= mach <= m1:
            return f0 + (f1 - f0) * (mach - m0) / (m1 - m0)


with open(path, encoding="utf-8") as f:
    data = []
    for d in csv.DictReader(f):
        try:
            data.append({k: float(v) for k, v in d.items()})
        except (TypeError, ValueError):
            continue

print(f"{'t':>6} {'alt':>6} {'Mach':>5} {'W':>6} {'dV/dt':>6} {'γ°':>5} {'Fn,ex':>7} {'@18k':>7} {'NASA':>7} {'ratio':>6} {'R/C':>6}")
bands = {}
for i in range(2, len(data) - 2):
    a, d, b = data[i - 2], data[i], data[i + 2]
    if not (t_from <= d["t"] <= t_to):
        continue
    if d["SIM_ON_GROUND[-]"] or d["FLAPS_HANDLE_INDEX[-]"] or d["GEAR_HANDLE_POSITION[-]"]:
        continue
    lever = "GENERAL_ENG_THROTTLE_LEVER_POSITION:1[pct]"
    if min(a[lever], d[lever], b[lever]) < 99:
        continue
    alt = d["PLANE_ALTITUDE[ft]"]
    href = min(alts, key=lambda h: abs(h - alt))
    if abs(href - alt) > 1500:
        continue
    dt = b["t"] - a["t"]
    v = d["AIRSPEED_TRUE[kt]"] * KT
    dvdt = (b["AIRSPEED_TRUE[kt]"] - a["AIRSPEED_TRUE[kt]"]) * KT / dt
    sin_g = (b["PLANE_ALTITUDE[ft]"] - a["PLANE_ALTITUDE[ft]"]) / dt / v
    w = d["TOTAL_WEIGHT[lb]"]
    q = 0.5 * d["AMBIENT_DENSITY[slug/ft3]"] * v * v
    fnex = w / G0 * dvdt + w * sin_g
    fnex18 = fnex + K_IND * (w * w - W_REF * W_REF) / (q * S)       # less weight -> less induced drag
    mach = d["AIRSPEED_MACH[mach]"]
    rc = fnex18 * v / W_REF * 60
    nasa = fnex_nasa(href, mach)
    ratio = fnex18 / nasa if nasa else float("nan")
    if nasa:
        bands.setdefault((int(href), round(mach * 20) / 20), []).append(ratio)
    print(f"{d['t']:6.1f} {alt:6.0f} {mach:5.2f} {w:6.0f} {dvdt:6.1f} {sin_g * 57.3:5.1f} {fnex:7.0f} {fnex18:7.0f} "
          f"{nasa if nasa else float('nan'):7.0f} {ratio:6.2f} {rc:6.0f}")

if bands:
    print("\nBand means (altitude, Mach ±0.025): Fn,ex sim/NASA")
    worst = 0.0
    for (h, m), rs in sorted(bands.items()):
        if len(rs) >= 2:
            mean = sum(rs) / len(rs)
            worst = max(worst, abs(mean - 1))
            print(f"  {h:6d} ft  M {m:.2f}: {mean:5.2f} (n={len(rs)})")
    print(f"T3-H: largest band deviation {worst:.0%} -> {'PASSED' if worst <= TOL else 'FAILED'} (tolerance ±{TOL:.0%})")
