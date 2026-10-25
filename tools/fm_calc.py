"""Computes MSFS flight model values of the F-104G from the source data in docs/data/.

Usage: fm_calc.py <project folder>
Prints ready cfg lines (to paste into flight_model.cfg), with the derivation as a comment.
"""
import csv
import math
import os
import sys

root = sys.argv[1]
data_dir = os.path.join(root, "docs", "data")


def read_csv(name):
    with open(os.path.join(data_dir, name), encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    head = rows[0]
    return head, [[float(v) for v in r] for r in rows[1:]]


# --- Wing geometry: trapezoidal wing from S, b and MAC (NASA TN D-6398, CR-2144) ---
S, b, mac = 196.1, 21.94, 9.55
ar = b * b / S
# S = b/2 * cr * (1 + l);  MAC = 2/3 * cr * (1 + l + l^2) / (1 + l)  ->  solve for l (taper)
target = mac / (2 / 3 * (2 * S / b))
lo, hi = 0.0, 1.0
for _ in range(60):
    lam = (lo + hi) / 2
    f = (1 + lam + lam * lam) / (1 + lam) ** 2
    lo, hi = (lam, hi) if f > target else (lo, lam)
cr = 2 * S / (b * (1 + lam))
ct = cr * lam
print(f"; wing: AR = {ar:.3f}, taper = {lam:.3f}, root chord = {cr:.2f} ft, tip chord = {ct:.2f} ft")
print(f"wing_root_chord = {cr:.2f}  ; MSFS derives the tip chord from area/span")

# --- Lift: NASA TN D-7137 Table 1 ---
head, cl = read_csv("nasa_d7137_cl_alpha_mach.csv")
machs = [float(h[1:]) for h in head[1:]]
alphas = [r[0] for r in cl]
cl_m04 = [r[1] for r in cl]
slope = (cl_m04[-1] - cl_m04[0]) / math.radians(alphas[-1] - alphas[0])
print(f"\n; CL alpha (M 0.4, 0..14 degrees) = {slope:.2f} /rad; CR-2144 approach: 3.44 /rad")

# Polar in rad. 0..14 degrees measured (M 0.4). Above that an estimate: CLmax ~0.95 at 18 degrees,
# then a drop (pitch-up region, FM 6-5). Negative side symmetric about CL(0) = 0.01.
pts = [(-180, 0.0), (-90, 0.0), (-30, -0.6), (-18, -0.93)]
pts += [(-a, -(c - 0.01) + 0.01) for a, c in zip(alphas[::-1], cl_m04[::-1]) if a > 0]
pts += list(zip(alphas, cl_m04))
pts += [(16, 0.84), (18, 0.95), (20, 0.93), (25, 0.85), (30, 0.75), (45, 0.6), (90, 0.0), (180, 0.0)]
print("lift_coef_aoa_table = " + ", ".join(f"{math.radians(a):.4f}:{c:.3f}" for a, c in pts))

# Mach scaling: CL at 6 degrees relative to M 0.4 (linear range)
i6 = alphas.index(6)
ref = cl[i6][1]
scale = [(0.0, 1.0)] + [(m, cl[i6][j + 1] / ref) for j, m in enumerate(machs)]
print("lift_coef_mach_table = " + ", ".join(f"{m:.2f}:{s:.3f}" for m, s in scale))

# --- Drag: NASA TN D-7137 Table 2 ---
head, cd = read_csv("nasa_d7137_cd_mach_cl.csv")
cls = [float(h[2:]) for h in head[1:]]
cd0 = cd[0][1]
print(f"\ndrag_coef_zero_lift = {cd0:.4f}")
print("drag_coef_zero_lift_mach_tab = " + ", ".join(f"{r[0]:.3f}:{r[1] - cd0:.4f}" for r in cd))

# Oswald factor: least squares CD - CD0 = k * CL^2 subsonic (M <= 0.8), CL 0.1..0.5
num = den = 0.0
for r in cd:
    if r[0] <= 0.8:
        for c, d in zip(cls[1:], r[2:]):
            num += (d - r[1]) * c * c
            den += c ** 4
k = num / den
e = 1 / (math.pi * ar * k)
print(f"oswald_efficiency_factor = {e:.3f}  ; from k = {k:.4f} (CD = CD0 + k*CL^2, M <= 0.8)")
