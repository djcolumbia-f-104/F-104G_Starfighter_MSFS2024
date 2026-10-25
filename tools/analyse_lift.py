"""Compares the lift coefficient flown in the sim with the NASA table (TN D-7137 Table 1).

Usage: analyse_lift.py <project folder> <flighttest.csv>  (CSV from tools/simlog.py)
CL_sim = G * W / (0.5 * rho * V_TAS^2 * S); CL_nasa = table(alpha, Mach), Mach < 0.4 treated as 0.4.
Only points in the air with flaps/gear retracted.
"""
import csv
import os
import sys

S = 196.1
KT = 1.68781


def interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0] + (ys[1] - ys[0]) * (x - xs[0]) / (xs[1] - xs[0])
    if x >= xs[-1]:
        return ys[-2] + (ys[-1] - ys[-2]) * (x - xs[-2]) / (xs[-1] - xs[-2])
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            return ys[i] + (ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i])


sys.stdout.reconfigure(encoding="utf-8")
root, path = sys.argv[1], sys.argv[2]
with open(os.path.join(root, "docs", "data", "nasa_d7137_cl_alpha_mach.csv"), encoding="utf-8") as f:
    rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
machs = [float(h[1:]) for h in rows[0][1:]]
tab = [[float(v) for v in r] for r in rows[1:]]
alphas = [r[0] for r in tab]


def cl_nasa(alpha, mach):
    m = max(mach, machs[0])
    per_mach = [interp(alpha, alphas, [r[j + 1] for r in tab]) for j in range(len(machs))]
    return interp(m, machs, per_mach)


with open(path, encoding="utf-8") as f:
    data = list(csv.DictReader(f))
TOL = 0.03  # acceptance T3-A (docs/flight-model-plan.md): |band mean CL_sim - CL_nasa| <= 0.03 at M 0.4-0.95
print(f"{'t':>6} {'IAS':>5} {'Mach':>5} {'alpha':>6} {'G':>5} {'CL_sim':>7} {'CL_nasa':>7} {'ratio':>6} {'elev':>6} {'trim':>6}")
diffs, trim_pts, bands = [], [], {}
for d in data:
    try:
        if float(d["SIM_ON_GROUND[-]"]) or float(d["FLAPS_HANDLE_INDEX[-]"]) or float(d["GEAR_HANDLE_POSITION[-]"]):
            continue
        a = float(d["INCIDENCE_ALPHA[deg]"])
        g = float(d["G_FORCE[g]"])
        w = float(d["TOTAL_WEIGHT[lb]"])
        rho = float(d["AMBIENT_DENSITY[slug/ft3]"])
        v = float(d["AIRSPEED_TRUE[kt]"]) * KT
        m = float(d["AIRSPEED_MACH[mach]"])
        ias = float(d["AIRSPEED_INDICATED[kt]"])
    except (ValueError, TypeError, KeyError):
        continue
    cl = g * w / (0.5 * rho * v * v * S)
    cn = cl_nasa(a, m)
    ratio = cl / cn if abs(cn) > 0.02 else float("nan")
    hr = float(d.get("ELEVATOR_DEFLECTION[deg]") or "nan")      # only in simlog versions from 2026-10-25
    tr = float(d.get("ELEVATOR_TRIM_POSITION[deg]") or "nan")
    if 0.4 <= m <= 0.95:
        diffs.append(cl - cn)
        if abs(g - 1) < 0.15:                      # quasi-steady (no pull-outs/positioning manoeuvres)
            bands.setdefault(int(a), []).append(cl - cn)
        if hr == hr and tr == tr and abs(g - 1) < 0.1 and abs(tr) < 9.9:   # no nan, ~1 g, not at the stop
            trim_pts.append((a, hr + tr))
    print(f"{float(d['t']):6.1f} {ias:5.0f} {m:5.2f} {a:6.2f} {g:5.2f} {cl:7.3f} {cn:7.3f} {ratio:6.2f} {hr:6.2f} {tr:6.2f}")
if len(trim_pts) > 5:
    # T3-G: total tail deflection (elevator + trim) over α; CR-96008: -Cmα/Cmδe = 0.67 (M 0.84) .. 1.05 (takeoff)
    n = len(trim_pts)
    ma, md = sum(p[0] for p in trim_pts) / n, sum(p[1] for p in trim_pts) / n
    k = sum((a - ma) * (d - md) for a, d in trim_pts) / sum((a - ma) ** 2 for a, _ in trim_pts)
    print(f"\nT3-G: tail deflection (elevator + trim) = {md - k * ma:+.2f}° + {k:.2f} × α  ({n} points, trim below the stop only)")
if diffs:
    worst = max(diffs, key=abs)
    # acceptance on 1° band means (>= 3 points, |g-1| < 0.15): single points scatter in transitions (rounds A/C 2026-10-25)
    means = {b: sum(v) / len(v) for b, v in bands.items() if len(v) >= 3}
    wb, wm = max(means.items(), key=lambda kv: abs(kv[1])) if means else (0, 0.0)
    print(f"\nT3-A: {len(diffs)} points M 0.4-0.95, mean dev. {sum(diffs) / len(diffs):+.3f}, largest single point {worst:+.3f};"
          f" largest band mean {wm:+.3f} (α {wb}-{wb + 1}°, {len(means)} bands)"
          f" -> {'PASSED' if means and abs(wm) <= TOL else 'FAILED'} (tolerance {TOL})")
