"""Test T3-F: drag coefficient in the sim from a deceleration run vs. NASA TN D-7137 Table 2.

Usage: analyse_drag.py <project folder> <flighttest.csv> [t_from t_to]   (CSV from tools/simlog.py)
Flight path balance: m·dV/dt = T_net - D - W·sin γ  ->  D = T_net - m·dV/dt - W·sin γ,  CD = D / (q·S).
T_net = TURB_ENG_JET_THRUST (gross thrust minus ram drag); thrust axis ≈ flight path (cos(α+2.5°) ≈ 1).
dV/dt and γ from true airspeed and altitude (central differences over ±2 points), CL as in analyse_lift.py.
Only points in the air, flaps/gear up, throttle constant. Acceptance: |CD_sim/CD_nasa - 1| <= 10 %.
"""
import csv
import os
import sys

S = 196.1
KT = 1.68781
G0 = 32.174
TOL = 0.10

sys.stdout.reconfigure(encoding="utf-8")
root, path = sys.argv[1], sys.argv[2]
t_from = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
t_to = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9


def interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            return ys[i] + (ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i])


with open(os.path.join(root, "docs", "data", "nasa_d7137_cd_mach_cl.csv"), encoding="utf-8") as f:
    rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
cls = [float(h[2:]) for h in rows[0][1:]]
tab = [[float(v) for v in r] for r in rows[1:]]


def cd_nasa(mach, cl):
    per_mach = [interp(cl, cls, r[1:]) for r in tab]
    return interp(mach, [r[0] for r in tab], per_mach)


with open(path, encoding="utf-8") as f:
    data = []
    for d in csv.DictReader(f):
        try:
            data.append({k: float(v) for k, v in d.items()})
        except (TypeError, ValueError):
            continue

print(f"{'t':>6} {'IAS':>5} {'Mach':>5} {'alpha':>6} {'CL':>6} {'T_net':>7} {'dV/dt':>6} {'γ°':>5} "
      f"{'CD_sim':>7} {'CD_nasa':>7} {'ratio':>6}")
ratios, brake_dcd = [], []
for i in range(2, len(data) - 2):
    a, d, b = data[i - 2], data[i], data[i + 2]
    if not (t_from <= d["t"] <= t_to):
        continue
    if d["SIM_ON_GROUND[-]"] or d["FLAPS_HANDLE_INDEX[-]"] or d["GEAR_HANDLE_POSITION[-]"]:
        continue
    lever = "GENERAL_ENG_THROTTLE_LEVER_POSITION:1[pct]"
    if not (a[lever] == d[lever] == b[lever]):
        continue
    dt = b["t"] - a["t"]
    v = d["AIRSPEED_TRUE[kt]"] * KT
    dvdt = (b["AIRSPEED_TRUE[kt]"] - a["AIRSPEED_TRUE[kt]"]) * KT / dt
    sin_g = (b["PLANE_ALTITUDE[ft]"] - a["PLANE_ALTITUDE[ft]"]) / dt / v   # from altitude, independent of the VS unit
    w = d["TOTAL_WEIGHT[lb]"]
    q = 0.5 * d["AMBIENT_DENSITY[slug/ft3]"] * v * v
    thrust = d["TURB_ENG_JET_THRUST:1[lbf]"]
    drag = thrust - w / G0 * dvdt - w * sin_g
    cd = drag / (q * S)
    cl = d["G_FORCE[g]"] * w / (q * S)
    mach = d["AIRSPEED_MACH[mach]"]
    cn = cd_nasa(mach, cl)
    brake = d.get("SPOILERS_HANDLE_POSITION[pct]", 0)              # only in simlog versions from round F
    if brake > 99:
        brake_dcd.append(cd - cn)                                  # speed brakes fully out: ΔCD over the clean polar
        print(f"{d['t']:6.1f} {d['AIRSPEED_INDICATED[kt]']:5.0f} {mach:5.2f}  speed brakes out: ΔCD {cd - cn:+.4f}")
        continue
    if brake > 1:
        continue                                                   # brakes moving
    ratios.append((mach, cd / cn))
    print(f"{d['t']:6.1f} {d['AIRSPEED_INDICATED[kt]']:5.0f} {mach:5.2f} {d['INCIDENCE_ALPHA[deg]']:6.2f} {cl:6.3f} "
          f"{thrust:7.0f} {dvdt:6.1f} {sin_g * 57.3:5.1f} {cd:7.4f} {cn:7.4f} {cd / cn:6.2f}")

if ratios:
    print()
    for lo, hi in ((0.4, 0.6), (0.6, 0.8), (0.8, 0.95), (0.95, 1.2)):
        sel = [r for m, r in ratios if lo <= m < hi]
        if sel:
            print(f"M {lo:.2f}-{hi:.2f}: CD_sim/CD_nasa mean {sum(sel) / len(sel):.2f} (n={len(sel)})")
    sel = [r for m, r in ratios if 0.4 <= m <= 0.95]
    if sel:
        mean = sum(sel) / len(sel)
        print(f"T3-F: {len(sel)} points M 0.4-0.95, mean {mean:.2f} -> "
              f"{'PASSED' if abs(mean - 1) <= TOL else 'FAILED'} (tolerance ±{TOL:.0%})")
if brake_dcd:
    m = sum(brake_dcd) / len(brake_dcd)
    print(f"Speed brakes (S11e): ΔCD mean {m:+.4f} (n={len(brake_dcd)}), target 0.042 ±20 % -> "
          f"{'PASSED' if abs(m / 0.042 - 1) <= 0.2 else 'FAILED'}")
