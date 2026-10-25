"""Berechnet MSFS-Flugmodellwerte der F-104G aus den Quelldaten in docs/data/.

Aufruf: fm_calc.py <projektordner>
Gibt fertige cfg-Zeilen aus (zum Einfügen in flight_model.cfg), mit Herleitung als Kommentar.
"""
import csv
import math
import os
import sys

root = sys.argv[1]
daten = os.path.join(root, "docs", "data")


def read_csv(name):
    with open(os.path.join(daten, name), encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    head = rows[0]
    return head, [[float(v) for v in r] for r in rows[1:]]


# --- Flügelgeometrie: Trapezflügel aus S, b und MAC (NASA TN D-6398, CR-2144) ---
S, b, mac = 196.1, 21.94, 9.55
ar = b * b / S
# S = b/2 * cr * (1 + l);  MAC = 2/3 * cr * (1 + l + l^2) / (1 + l)  ->  nach l (Zuspitzung) lösen
target = mac / (2 / 3 * (2 * S / b))
lo, hi = 0.0, 1.0
for _ in range(60):
    lam = (lo + hi) / 2
    f = (1 + lam + lam * lam) / (1 + lam) ** 2
    lo, hi = (lam, hi) if f > target else (lo, lam)
cr = 2 * S / (b * (1 + lam))
ct = cr * lam
print(f"; Flügel: AR = {ar:.3f}, Zuspitzung = {lam:.3f}, Wurzeltiefe = {cr:.2f} ft, Spitzentiefe = {ct:.2f} ft")
print(f"wing_root_chord = {cr:.2f}  ; Spitzentiefe ergibt MSFS aus Fläche/Spannweite")

# --- Auftrieb: NASA TN D-7137 Table 1 ---
head, cl = read_csv("nasa_d7137_cl_alpha_mach.csv")
machs = [float(h[1:]) for h in head[1:]]
alphas = [r[0] for r in cl]
cl_m04 = [r[1] for r in cl]
slope = (cl_m04[-1] - cl_m04[0]) / math.radians(alphas[-1] - alphas[0])
print(f"\n; CL alpha (M 0.4, 0..14 Grad) = {slope:.2f} /rad; CR-2144 Landeanflug: 3.44 /rad")

# Polare in rad. 0..14 Grad gemessen (M 0.4). Darüber Schätzung: CLmax ~0.95 bei 18 Grad,
# danach Abfall (Pitch-up-Bereich, FM 6-5). Negativ symmetrisch um CL(0) = 0.01.
pts = [(-180, 0.0), (-90, 0.0), (-30, -0.6), (-18, -0.93)]
pts += [(-a, -(c - 0.01) + 0.01) for a, c in zip(alphas[::-1], cl_m04[::-1]) if a > 0]
pts += list(zip(alphas, cl_m04))
pts += [(16, 0.84), (18, 0.95), (20, 0.93), (25, 0.85), (30, 0.75), (45, 0.6), (90, 0.0), (180, 0.0)]
print("lift_coef_aoa_table = " + ", ".join(f"{math.radians(a):.4f}:{c:.3f}" for a, c in pts))

# Machskalierung: CL bei 6 Grad relativ zu M 0.4 (linearer Bereich)
i6 = alphas.index(6)
ref = cl[i6][1]
scale = [(0.0, 1.0)] + [(m, cl[i6][j + 1] / ref) for j, m in enumerate(machs)]
print("lift_coef_mach_table = " + ", ".join(f"{m:.2f}:{s:.3f}" for m, s in scale))

# --- Widerstand: NASA TN D-7137 Table 2 ---
head, cd = read_csv("nasa_d7137_cd_mach_cl.csv")
cls = [float(h[2:]) for h in head[1:]]
cd0 = cd[0][1]
print(f"\ndrag_coef_zero_lift = {cd0:.4f}")
print("drag_coef_zero_lift_mach_tab = " + ", ".join(f"{r[0]:.3f}:{r[1] - cd0:.4f}" for r in cd))

# Oswald-Faktor: Kleinste Quadrate CD - CD0 = k * CL^2 im Unterschall (M <= 0.8), CL 0.1..0.5
num = den = 0.0
for r in cd:
    if r[0] <= 0.8:
        for c, d in zip(cls[1:], r[2:]):
            num += (d - r[1]) * c * c
            den += c ** 4
k = num / den
e = 1 / (math.pi * ar * k)
print(f"oswald_efficiency_factor = {e:.3f}  ; aus k = {k:.4f} (CD = CD0 + k*CL^2, M <= 0.8)")
