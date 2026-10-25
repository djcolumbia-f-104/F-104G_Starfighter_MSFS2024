"""Back-calculates the MSFS engine tables of the F-104G from NASA TN D-7137 Table 3.

Usage: engine_calc.py <project folder>

MSFS model (SDK: engines.cfg-additional-information, supersonic_inlet = 1, supersonic_ram_drag = 1):
  gross   = static_thrust * mult(N1c, M) * ab_scale * delta_total
  ram     = TAS * airflow_corr(N1c) * delta_total / sqrt(theta_total) / g
  net     = gross - ram
  delta_total = delta * (1 + 0.2 M^2)^3.5 * mach_losses,  mach_losses = 1 - 0.075 (M - 1)^1.35 (M >= 1)
  theta_total = theta * (1 + 0.2 M^2)
Control as on the J79: mechanical speed 100 % at full throttle (uncorrected_commanded_Ne_table),
hence corrected speed N1c = 100 / sqrt(theta_total). For each Mach number every altitude gives a pair
(N1c, mult) that exactly matches the NASA net thrust (max. afterburner); the table is interpolated from these.
"""
import csv
import math
import os
import sys

STATIC_THRUST = 10000.0   # lbf dry (FM 1-5)
AB_SCALE = 1.58           # 15 800 / 10 000 (FM 1-5)
AIRFLOW = 160.0           # lb/s primary air J79-GE-11A at 100 % (Stoelinga, Zipper #42, 2000)
INLET_AREA = 5.0          # ft^2; MSFS: airflow = corrected_airflow_table (per ft^2) x inlet_area
                          # (confirmed on the F-4J: 5 ft^2 x 33.6 = 168 lb/s). With 1 ft^2 the airspeed indicator rose while static.
G = 32.174
A0 = 1116.45              # ft/s speed of sound, sea level ISA
N1_ROWS = [0, 50, 67, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]


def atmosphere(h):
    """ISA: (theta, delta) for altitude h in ft."""
    if h <= 36089:
        theta = 1 - 6.8756e-6 * h
        return theta, theta ** 5.2559
    return 0.75187, 0.22336 * math.exp(-4.80634e-5 * (h - 36089))


def airflow(n1c):
    return AIRFLOW * n1c / 100


def point(m, h, net):
    """N1c at full throttle and the mult that gives exactly the net thrust net."""
    theta, delta = atmosphere(h)
    losses = 1 - 0.075 * (m - 1) ** 1.35 if m >= 1 else 1.0
    d_tot = delta * (1 + 0.2 * m * m) ** 3.5 * losses
    t_tot = theta * (1 + 0.2 * m * m)
    n1c = 100 / math.sqrt(t_tot)
    ram = m * A0 * math.sqrt(theta) * airflow(n1c) * d_tot / math.sqrt(t_tot) / G
    return n1c, (net + ram) / (STATIC_THRUST * AB_SCALE * d_tot)


def interp(x, pts):
    """Linear interpolation in sorted (x, y) pairs, constant outside."""
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


root = sys.argv[1]
with open(os.path.join(root, "docs", "data", "nasa_d7137_thrust_maxab_lbf.csv"), encoding="utf-8") as f:
    rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
machs = [float(c[1:]) for c in rows[0][1:]]
data = [[float(v) for v in r] for r in rows[1:]]

columns = []
print("Mach: (N1c %, mult) per altitude 0 / 10 / 20 / 30 / 40 / 50 / 60k ft")
for j, m in enumerate(machs):
    pts = [point(m, r[0], r[j + 1]) for r in data]
    print(f"{m:3.1f}: " + "  ".join(f"({n:5.1f},{k:.3f})" for n, k in pts))
    # In the stratosphere N1c is the same -> average the values (scatter = model error)
    merged = {}
    for n, k in pts:
        merged.setdefault(round(n, 1), []).append(k)
    columns.append(sorted((n, sum(ks) / len(ks)) for n, ks in merged.items()))

# Idle point (Stoelinga: 67 % = 500 lbf uninstalled, sea level static). Installation loss as at full throttle:
# installed/uninstalled = NASA 11 200 / 15 800 = 0.709 -> mult(67 %, M 0) = 500 * 0.709 / (10 000 * AB factor 1)
IDLE_N1 = 67.0
IDLE_MULT = 500.0 * (11200.0 / 15800.0) / STATIC_THRUST
# Thrust table: filled from the data points. Linear between idle and the lowest data point; the Mach
# dependence at idle follows the ratio of the column to Mach 0 at the lowest data point [S].
lines = ["0.0:" + ":".join(f"{m:g}" for m in machs)]
lo_m0 = columns[0][0][1]
for n1 in N1_ROWS:
    vals = []
    for pts in columns:
        lo_n, lo_k = pts[0]
        idle_k = IDLE_MULT * lo_k / lo_m0
        if n1 <= IDLE_N1:
            v = idle_k * (n1 / IDLE_N1) ** 2
        elif n1 < lo_n:
            v = idle_k + (lo_k - idle_k) * (n1 - IDLE_N1) / (lo_n - IDLE_N1)
        else:
            v = interp(n1, pts)
        vals.append(v)
    lines.append(f"{n1}:" + ":".join(f"{v:.3f}" for v in vals))
print("\nn1_and_mach_on_thrust_table = " + ", ".join(lines))
air = [lines[0]] + [f"{n1}:" + ":".join(f"{airflow(n1) / INLET_AREA:.2f}" for _ in machs) for n1 in N1_ROWS]
print("\ncorrected_airflow_table = " + ", ".join(air))

# Check: sim net thrust from the finished table against NASA
print("\nCheck (sim - NASA) in %, rows = altitude 0..60k ft, columns = Mach")
for r in data:
    out = []
    for j, m in enumerate(machs):
        n1c, _ = point(m, r[0], r[j + 1])
        theta, delta = atmosphere(r[0])
        losses = 1 - 0.075 * (m - 1) ** 1.35 if m >= 1 else 1.0
        d_tot = delta * (1 + 0.2 * m * m) ** 3.5 * losses
        t_tot = theta * (1 + 0.2 * m * m)
        k = interp(n1c, columns[j])
        ram = m * A0 * math.sqrt(theta) * airflow(n1c) * d_tot / math.sqrt(t_tot) / G
        net = STATIC_THRUST * AB_SCALE * d_tot * k - ram
        out.append(100 * (net - r[j + 1]) / r[j + 1])
    print(f"{int(r[0]):6d}: " + " ".join(f"{e:+4.0f}" for e in out))
