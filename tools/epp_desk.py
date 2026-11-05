"""EPP desk analysis (work package docs/notes/workpackage-EPP-part-power-thrust.md, steps A0/A2; 2026-11-05).

Usage: tools\\.venv\\Scripts\\python.exe -I tools\\epp_desk.py <project folder> [engines cfg or ""] [fit | cand <knots>]
  fit (default): per FM Appendix Part 7 descent chart (docs/data/fm_a7_descent.csv, flight test, J79-GE-11A) and altitude
       band the required net thrust  T = D + W sin γ + (W/g) dV/dt  (constant IAS: TAS falls in the descent)
       with D = q S [CD_NASA(M, CL) + ΔCD flaps + ΔCD speed brakes] (D-7137 Table 2, sim T3-F = 1.00-1.04 x NASA;
       flap/speed-brake ΔCD = the sim's own validated values), against the sim net thrust from the engine formula
       (engine_calc.py / SDK): gross = static x mult(N1c, M) x δt, ram = W_corr(N1c) x inlet x δt/√θt x V/g,
       N1c = N1/√θt. Prints A_s = (T_sim - T_req)/q̄ [ft²] (part-power deficit per dynamic pressure) and the anchor report.
  cand "n1c:A,n1c:A,...": candidate table with Δmult = 0.148 M² A_s(N1c)/(1+0.2M²)^3.5 (= q̄ x A_s, altitude
       independent), anchor report with it, and the table line for engines.f104.cfg.
Desk gate A1 (2026-11-05): the formula reproduces the measured sim net thrust of D5 cruise/endurance, approach, idle and
Military within +2..+6 % (measurements.md).
"""
import csv
import math
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = sys.argv[1]
ENG = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else os.path.join(root, "source", "cfg", "engines.f104.cfg")
G, A0, S, P0 = 32.174, 1116.45, 196.1, 2116.2
STATIC, INLET, TSFC = 10000.0, 5.0, 0.69     # 0.72 until 2026-11-05 (D5 after EPP)
DCD_TO_FLAPS = 0.013      # [M] B4 2026-10-29: TAKEOFF flap ΔCD after the drag scalar 0.42
DCD_SB = 0.044            # [M] S11e: 0.042 (cfg) .. 0.046 (measured) at 52°


def table(name):
    txt = open(ENG, encoding="utf-8").read()
    m = re.search(rf"^{name}\s*=\s*(.+)$", txt, re.M)
    rows = [r.strip() for r in m.group(1).split(";")[0].split(",")]
    machs = [float(v) for v in rows[0].split(":")[1:]]
    return machs, [(float(r.split(":")[0]), [float(v) for v in r.split(":")[1:]]) for r in rows[1:]]


def lin(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            return ys[i] + (ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i])


def bilin(tab, n1, mach):
    machs, rows = tab
    return lin(n1, [r[0] for r in rows], [lin(mach, machs, r[1]) for r in rows])


THR, AIR = table("n1_and_mach_on_thrust_table"), table("corrected_airflow_table")
with open(os.path.join(root, "docs", "data", "nasa_d7137_cd_mach_cl.csv"), encoding="utf-8") as f:
    r = [x for x in csv.reader(f) if x and not x[0].startswith("#")]
CLS = [float(h[2:]) for h in r[0][1:]]
CDT = [[float(v) for v in x] for x in r[1:]]


def cd_nasa(mach, cl):
    return lin(mach, [x[0] for x in CDT], [lin(cl, CLS, x[1:]) for x in CDT])


def atm(h):
    if h <= 36089:
        th = 1 - 6.8756e-6 * h
        return th, th ** 5.2559
    return 0.75187, 0.22336 * math.exp(-4.80634e-5 * (h - 36089))


def mach_from_cas(kcas, h):
    th, de = atm(h)
    vc = kcas * 1.68781
    qc = P0 * ((1 + 0.2 * (vc / A0) ** 2) ** 3.5 - 1)
    return math.sqrt(5 * ((qc / (P0 * de) + 1) ** (2 / 7) - 1))


def eng(n1, h, mach, thr):
    th, de = atm(h)
    tt, dt = th * (1 + 0.2 * mach ** 2), de * (1 + 0.2 * mach ** 2) ** 3.5
    n1c = n1 / math.sqrt(tt)
    gross = STATIC * bilin(thr, n1c, mach) * dt
    ram = bilin(AIR, n1c, mach) * INLET * dt / math.sqrt(tt) * mach * A0 * math.sqrt(th) / G
    return n1c, gross, ram, dt


def n1_for(net, h, mach, thr):
    """mechanical N1 that gives the net thrust (bisection 60-105 %)"""
    lo, hi = 60.0, 105.0
    for _ in range(40):
        mid = (lo + hi) / 2
        _, g_, r_, _ = eng(mid, h, mach, thr)
        lo, hi = (mid, hi) if g_ - r_ < net else (lo, mid)
    return (lo + hi) / 2


def q_of(h, mach):
    return 0.7 * P0 * atm(h)[1] * mach * mach


CHARTS = {   # chart: (rpm %, KIAS, weight lb, ΔCD config, FM fuel lb from top_kft, top_kft, FM time min)
    "A7-1R": (67.0, 300, 15200, 0.0, 33, 29, None),
    "A7-2": (85.0, 275, 20500, DCD_TO_FLAPS + DCD_SB, 140, 30, 5.1),
    "A7-2b": (85.0, 275, 20500, DCD_TO_FLAPS + 0.033, 140, 30, 5.1),     # speed-brake ΔCD estimated from A7-1 (extended)
    "A7-3": (85.0, 300, 15650, 0.0, 500, 37, 17.5),
}
pts = {}
with open(os.path.join(root, "docs", "data", "fm_a7_descent.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(x for x in f if not x.startswith("#")):
        pts.setdefault(row["chart"], []).append((float(row["alt_kft"]) * 1000, float(row["dist_nm"]) * 6076.12))
pts["A7-2b"] = pts["A7-2"]


def chart_points(chart, thr):
    import numpy as np
    n1, kias, w, dcd, *_ = CHARTS[chart]
    p = sorted(pts[chart])
    # smooth: least-squares cubic s(h) (the tracer alternates dense/sparse rows -> raw differences scatter ±40 %)
    lo = 7500.0 if chart == "A7-3" else 0.0                  # A7-3: no traced points below 7 500 ft (axis)
    c = np.polyfit([h for h, _ in p if h >= lo or h == 0], [s for h, s in p if h >= lo or h == 0], 3)
    p = [(h, float(np.polyval(c, h))) for h, _ in p if h >= lo]
    out = []
    for (h0, s0), (h1, s1) in zip(p, p[1:]):
        h = (h0 + h1) / 2
        gam = math.atan((h1 - h0) / (s1 - s0))
        th, de = atm(h)
        m = mach_from_cas(kias, h)
        v = m * A0 * math.sqrt(th)
        vt = lambda hh: mach_from_cas(kias, hh) * A0 * math.sqrt(atm(hh)[0])
        acc = w / G * (vt(h1) - vt(h0)) / (h1 - h0) * (-v * math.sin(gam))
        q = q_of(h, m)
        cl = w * math.cos(gam) / (q * S)
        d = q * S * (cd_nasa(m, cl) + dcd)
        t_req = d - w * math.sin(gam) + acc
        n1c, gross, ram, dt = eng(n1, h, m, thr)
        out.append(dict(h=h, m=m, q=q, gam=gam, cl=cl, d=d, t_req=t_req, t_sim=gross - ram, n1c=n1c, gross=gross,
                        ram=ram, dt=dt, dtime=(s1 - s0) / v / math.cos(gam), m_req=(t_req + ram) / (STATIC * dt),
                        mult=gross / (STATIC * dt)))
    return out


def candidate(knots):
    """THR with rows reduced by Δmult = 0.148 M² A_s(N1c) / (1 + 0.2 M²)^3.5 (= q̄ x A_s / (static x δt), altitude
    independent); A_s from knots [(N1c, ft²)], linear between them, 0 outside. Δmult above M_CAP (the data limit of
    FM A7-2/A7-3, M 0.85) is held at the M_CAP value (no data); every Mach column is made monotonic in N1 (each row at
    least the row below + 0.01 above idle) so that more throttle never gives less thrust"""
    machs, rows = THR
    ks = sorted(knots)
    new = []
    for n1c, vals in rows:
        a = lin(n1c, [k[0] for k in ks], [k[1] for k in ks]) if ks[0][0] <= n1c <= ks[-1][0] else 0.0
        mc = lambda m: min(m, M_CAP)
        new.append([n1c, [v - 0.148 * mc(m) ** 2 * a / (1 + 0.2 * mc(m) ** 2) ** 3.5 for m, v in zip(machs, vals)]])
    for i in range(1, len(new)):
        if 67 < new[i][0] <= 90:                             # rows >= 95 (Military/AB, validated) stay untouched
            new[i][1] = [max(v, below + 0.01) for v, below in zip(new[i][1], new[i - 1][1])]
    return machs, [(n, [round(v, 3) for v in vals]) for n, vals in new]


M_CAP = 0.85


def table_text(thr):
    machs, rows = thr
    return "n1_and_mach_on_thrust_table = 0.0:" + ":".join(f"{m:g}" for m in machs) + ", " + ", ".join(
        f"{n:g}:" + ":".join(f"{v:.3f}" for v in vals) for n, vals in rows)


def report(thr, label):
    print(f"\n===== {label} =====")
    for chart in ("A7-1R", "A7-2", "A7-2b", "A7-3"):
        P = chart_points(chart, thr)
        t = sum(x["dtime"] for x in P) / 60
        rat = [x["t_sim"] / x["t_req"] for x in P if abs(x["t_req"]) > 200]
        txt = f"{chart:6} sim/req net thrust {min(rat):.2f}-{max(rat):.2f} (mean {sum(rat) / len(rat):.2f})"
        if CHARTS[chart][6]:
            fuel = sum(TSFC * x["gross"] * x["dtime"] / 3600 for x in P)
            txt += f"; fuel {fuel / t:.1f} lb/min (FM average {CHARTS[chart][4] / CHARTS[chart][6]:.1f})"
        print(txt)
    # anchors (measured sim states; the formula reproduces them within +2..+6 %)
    ap = n1_for(4546, 2100, 0.29, thr)
    ap16 = n1_for(3870, 1000, 0.265, thr)
    print(f"approach: N1 {ap:.1f} % at 18 900 lb / 190 KIAS (measured 89.5 with the old table); at FM 16 100 lb / 175 KIAS "
          f"(net ≈ 3 870) {ap16:.1f} % (FM Fig. 2-7: 87-90 %)")
    for name, h, m, net, ff_fm, n1_old in (("D5 A", 11898, 0.700, 2156, 3427, 83.8), ("D5 B", 19602, 0.801, 2081, 3180, 84.7),
                                            ("D5 C", 29499, 0.853, 1906, 2725, 85.4), ("E1 5k", 5000, 0.500, 1998, 3112, 80.9),
                                            ("E1 10k", 10000, 0.556, 1968, 3000, 81.5)):
        n1 = n1_for(net, h, m, thr)
        g_ = eng(n1, h, m, thr)[1]
        g0 = eng(n1_old, h, m, THR)[1]
        print(f"{name:6} cruise N1 {n1:5.1f} % (old {n1_old}); FF {TSFC * g_:5.0f} lb/h = {TSFC * g_ / ff_fm:.2f} x FM "
              f"(old table {TSFC * g0 / ff_fm:.2f})")
    # FM 3-33 simulated flameout: 83 % + speed brakes + TAKEOFF flaps ≈ dead-engine glide (RAT out); sim proxy for the
    # dead engine = idle (A7-1 idle matches); 84 % / 275 KIAS clean + full speed brakes ≈ clean dead-engine glide (RAT in)
    for n1, kias, h, rat_d, txt in ((83, 260, 8000, 550, "SFO 83 %/260 KIAS TO+SB vs. idle+RAT"),
                                    (84, 275, 8000, 0, "SFO 84 %/275 KIAS clean+SB vs. idle   ")):
        m = mach_from_cas(kias, h)
        _, g_, r_, _ = eng(n1, h, m, thr)
        _, gi, ri, _ = eng(67, h, m, thr)
        dsb = DCD_SB * q_of(h, m) * S
        print(f"{txt}: net {g_ - r_:5.0f} - ΔD_SB {dsb:4.0f} = {g_ - r_ - dsb:5.0f} vs. idle {gi - ri:5.0f} - RAT {rat_d} = "
              f"{gi - ri - rat_d:5.0f} lbf -> excess {g_ - r_ - dsb - (gi - ri - rat_d):+5.0f} lbf")
    # FM 3-41 partial-power pattern: 83 %, TAKEOFF flaps, 260 KIAS, 1 800-2 000 ft/min, speed brakes "as necessary"
    m = mach_from_cas(260, 6500)
    _, g_, r_, _ = eng(83, 6500, m, thr)
    dsb = DCD_SB * q_of(6500, m) * S
    print(f"FM 3-41 at 6 500 ft: net {g_ - r_:.0f} lbf; needs 1 460 (brakes in) .. {1460 + dsb:.0f} (brakes full) -> "
          f"speed-brake fraction {(g_ - r_ - 1460) / dsb:.2f}")
    # level-flight equilibrium speed (clean, NASA polar, 18 500 lb) at the `position` routine state (16 500 ft) for
    # mechanical N1 88/90/93 %
    for n1 in (88.0, 90.0, 93.0):
        best = None
        for kias in range(250, 601, 5):
            m = mach_from_cas(kias, 16500)
            q = q_of(16500, m)
            d = q * S * cd_nasa(m, 18500 / (q * S))
            _, g_, r_, _ = eng(n1, 16500, m, thr)
            if g_ - r_ >= d:
                best = kias
        print(f"level flight 16 500 ft at N1 {n1:.0f} %: equilibrium ≈ {best} KIAS" if best else
              f"level flight 16 500 ft at N1 {n1:.0f} %: no equilibrium above 250 KIAS")


if __name__ == "__main__":
    mode = sys.argv[3] if len(sys.argv) > 3 else "fit"
    if mode == "fit":
        for chart in ("A7-3", "A7-2", "A7-2b", "A7-1R"):
            print(f"\n{chart}: alt, M, q, N1c, T_req, T_sim, mult, m_req, A_s = (T_sim - T_req)/q [ft²]")
            for x in chart_points(chart, THR):
                print(f"{x['h']:7.0f} {x['m']:5.2f} {x['q']:5.0f} {x['n1c']:5.1f} {x['t_req']:6.0f} {x['t_sim']:6.0f} "
                      f"{x['mult']:6.3f} {x['m_req']:6.3f} {(x['t_sim'] - x['t_req']) / x['q']:6.2f}")
        report(THR, "current table")
    elif mode == "flight":     # flight <config_test descent csv> <chart>: evaluation of a flown FM A7 replica
        log, chart = sys.argv[4], sys.argv[5]
        rows = [x for x in csv.DictReader(open(log, encoding="utf-8")) if x["phase"] == "test" and float(x["t"]) > 40]
        f = lambda k: sum(float(x[k]) for x in rows) / len(rows)
        h, ias, w, vs, tn = f("alt"), f("ias"), f("weight"), f("vs_fpm"), f("thrust_lbf")
        m = mach_from_cas(ias, h)
        v = m * A0 * math.sqrt(atm(h)[0])
        q = q_of(h, m)
        gam = math.asin(vs / 60 / v)                         # negative descending
        dvdh = (mach_from_cas(ias, h + 500) * A0 * math.sqrt(atm(h + 500)[0]) - mach_from_cas(ias, h - 500) * A0
                * math.sqrt(atm(h - 500)[0])) / 1000
        acc = w / G * dvdh * v * math.sin(gam)
        d_meas = tn - w * math.sin(gam) - acc                 # energy balance: T - D = W sin γ + W/g dV/dt
        dcd = CHARTS[chart][3]
        d_nasa = q * S * (cd_nasa(m, w / (q * S)) + dcd)
        P = chart_points(chart, THR)
        t_fm = lin(h, [x["h"] for x in P], [x["t_req"] for x in P])
        # FM-equivalent rate of descent at the SIM weight: same engine (T_FM), drag at the sim weight (NASA)
        vs_fm = 60 * v * (t_fm - d_nasa) / (w + w / G * dvdh * v)     # acc term solved together with sin γ
        print(f"{chart} flown: {h:.0f} ft mean, {ias:.0f} KIAS, M {m:.2f}, {w:.0f} lb: rate of descent {-vs:.0f} ft/min, "
              f"net thrust {tn:.0f} lbf")
        print(f"  FM engine at this altitude: net {t_fm:.0f} lbf (sim - FM {tn - t_fm:+.0f} lbf); drag from the energy balance "
              f"{d_meas:.0f} vs. NASA + config {d_nasa:.0f} lbf ({d_meas / d_nasa:.2f}); FM-equivalent rate of descent at "
              f"{w:.0f} lb: {-vs_fm:.0f} ft/min -> sim/FM {vs / vs_fm:.2f}")
    else:          # cand "n1c:A,n1c:A,..."
        knots = [tuple(float(v) for v in k.split(":")) for k in sys.argv[4].split(",")]
        C = candidate(knots)
        report(C, f"candidate A_s knots {knots}")
        print("\n" + table_text(C))
