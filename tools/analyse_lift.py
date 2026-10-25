"""Vergleicht den im Sim geflogenen Auftriebsbeiwert mit der NASA-Tabelle (TN D-7137 Table 1).

Aufruf: analyse_lift.py <projektordner> <flugtest.csv>  (CSV von tools/simlog.py)
CL_sim = G * W / (0.5 * rho * V_TAS^2 * S); CL_nasa = Tabelle(alpha, Mach), Mach < 0.4 wie 0.4.
Nur Punkte in der Luft, mit Klappen/Fahrwerk eingefahren.
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
TOL = 0.03  # Abnahme T3-A (docs/flight-model-plan.md): |Bandmittel CL_sim - CL_nasa| <= 0.03 bei M 0.4-0.95
print(f"{'t':>6} {'IAS':>5} {'Mach':>5} {'alpha':>6} {'G':>5} {'CL_sim':>7} {'CL_nasa':>7} {'Verh.':>6} {'HR':>6} {'Trim':>6}")
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
    hr = float(d.get("ELEVATOR_DEFLECTION[deg]") or "nan")      # erst ab simlog-Stand 2026-10-25
    tr = float(d.get("ELEVATOR_TRIM_POSITION[deg]") or "nan")
    if 0.4 <= m <= 0.95:
        diffs.append(cl - cn)
        if abs(g - 1) < 0.15:                      # quasistationär (keine Abfang-/Positioniermanöver)
            bands.setdefault(int(a), []).append(cl - cn)
        if hr == hr and tr == tr and abs(g - 1) < 0.1 and abs(tr) < 9.9:   # nan-frei, ~1 g, nicht im Anschlag
            trim_pts.append((a, hr + tr))
    print(f"{float(d['t']):6.1f} {ias:5.0f} {m:5.2f} {a:6.2f} {g:5.2f} {cl:7.3f} {cn:7.3f} {ratio:6.2f} {hr:6.2f} {tr:6.2f}")
if len(trim_pts) > 5:
    # T3-G: gesamter Leitwerksausschlag (Höhenruder + Trimmung) über α; CR-96008: -Cmα/Cmδe = 0,67 (M 0,84) .. 1,05 (Start)
    n = len(trim_pts)
    ma, md = sum(p[0] for p in trim_pts) / n, sum(p[1] for p in trim_pts) / n
    k = sum((a - ma) * (d - md) for a, d in trim_pts) / sum((a - ma) ** 2 for a, _ in trim_pts)
    print(f"\nT3-G: Leitwerksausschlag (HR + Trim) = {md - k * ma:+.2f}° + {k:.2f} × α  ({n} Punkte, nur Trimmung < Anschlag)")
if diffs:
    worst = max(diffs, key=abs)
    # Abnahme über 1°-Bandmittel (>= 3 Punkte, |g-1| < 0,15): Einzelpunkte streuen in Übergängen (Runde A/C 2026-10-25)
    means = {b: sum(v) / len(v) for b, v in bands.items() if len(v) >= 3}
    wb, wm = max(means.items(), key=lambda kv: abs(kv[1])) if means else (0, 0.0)
    print(f"\nT3-A: {len(diffs)} Punkte M 0.4-0.95, mittl. Abw. {sum(diffs) / len(diffs):+.3f}, größter Einzelpunkt {worst:+.3f};"
          f" größtes Bandmittel {wm:+.3f} (α {wb}-{wb + 1}°, {len(means)} Bänder)"
          f" -> {'BESTANDEN' if means and abs(wm) <= TOL else 'NICHT BESTANDEN'} (Toleranz {TOL})")
