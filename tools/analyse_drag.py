"""Test T3-F: Widerstandsbeiwert im Sim aus einem Verzögerungslauf vs. NASA TN D-7137 Table 2.

Aufruf: analyse_drag.py <projektordner> <flugtest.csv> [t_von t_bis]   (CSV von tools/simlog.py)
Bahnbilanz: m·dV/dt = T_netto - D - W·sin γ  ->  D = T_netto - m·dV/dt - W·sin γ,  CD = D / (q·S).
T_netto = TURB_ENG_JET_THRUST (Bruttoschub minus Einlaufwiderstand); Schubachse ≈ Bahn (cos(α+2,5°) ≈ 1).
dV/dt und γ aus wahrer Fahrt und Höhe (zentrale Differenzen über ±2 Punkte), CL wie analyse_lift.py.
Nur Punkte in der Luft, Klappen/Fahrwerk ein, Gashebel konstant. Abnahme: |CD_sim/CD_nasa - 1| <= 10 %.
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
      f"{'CD_sim':>7} {'CD_nasa':>7} {'Verh.':>6}")
ratios = []
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
    sin_g = (b["PLANE_ALTITUDE[ft]"] - a["PLANE_ALTITUDE[ft]"]) / dt / v   # aus Höhe, unabhängig von VS-Einheit
    w = d["TOTAL_WEIGHT[lb]"]
    q = 0.5 * d["AMBIENT_DENSITY[slug/ft3]"] * v * v
    thrust = d["TURB_ENG_JET_THRUST:1[lbf]"]
    drag = thrust - w / G0 * dvdt - w * sin_g
    cd = drag / (q * S)
    cl = d["G_FORCE[g]"] * w / (q * S)
    mach = d["AIRSPEED_MACH[mach]"]
    cn = cd_nasa(mach, cl)
    ratios.append((mach, cd / cn))
    print(f"{d['t']:6.1f} {d['AIRSPEED_INDICATED[kt]']:5.0f} {mach:5.2f} {d['INCIDENCE_ALPHA[deg]']:6.2f} {cl:6.3f} "
          f"{thrust:7.0f} {dvdt:6.1f} {sin_g * 57.3:5.1f} {cd:7.4f} {cn:7.4f} {cd / cn:6.2f}")

if ratios:
    print()
    for lo, hi in ((0.4, 0.6), (0.6, 0.8), (0.8, 0.95), (0.95, 1.2)):
        sel = [r for m, r in ratios if lo <= m < hi]
        if sel:
            print(f"M {lo:.2f}-{hi:.2f}: CD_sim/CD_nasa Mittel {sum(sel) / len(sel):.2f} (n={len(sel)})")
    sel = [r for m, r in ratios if 0.4 <= m <= 0.95]
    if sel:
        mean = sum(sel) / len(sel)
        print(f"T3-F: {len(sel)} Punkte M 0.4-0.95, Mittel {mean:.2f} -> "
              f"{'BESTANDEN' if abs(mean - 1) <= TOL else 'NICHT BESTANDEN'} (Toleranz ±{TOL:.0%})")
