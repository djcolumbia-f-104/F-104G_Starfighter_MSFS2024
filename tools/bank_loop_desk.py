"""Desk design of the landing bank loop (card docs/notes/test-cards/S3-bank-loop.md, 2026-11-06).

Usage: tools\\.venv\\Scripts\\python.exe -I tools\\bank_loop_desk.py <roll_id_steps.csv> [fracs=0.03,-0.03,...]
1) Fit of the open-loop roll response from tools/roll_id_test.py (_steps.csv, bank at ≈ 30 Hz during each aileron step):
     p' = (K(u) u - p) / tau + lam * phi,   phi' = p,   u applied after a dead time td
   K(u) = K0 (1 + c |u| / 1000) (aileron_scaling_table: deflection scale 0.3 at small inputs, rising), lam = slow
   bank-driven roll acceleration (sideslip/dihedral, spiral; rudder free, yaw damper ON).
2) Closed-loop simulation of a sampled PID (landing_test structure: one aileron update per pass, data read during the
   pass = one pass old) for a bank-target step and an initial bank disturbance; reports overshoot, settling, limit cycles.
"""
import csv
import math
import sys

STEPS_CSV = sys.argv[1]
FRACS = [0.03, -0.03, 0.06, -0.06, 0.12, -0.12, 0.25, -0.25]
FULL = 16383


def load():
    data = {}
    for x in csv.DictReader(open(STEPS_CSV)):
        data.setdefault(int(x["step"]), []).append((float(x["t_step"]), float(x["bank"])))
    out = []
    for k, s in sorted(data.items()):
        b0 = s[0][1]
        out.append((FRACS[k] * FULL, [(t, -(b - b0)) for t, b in s]))      # + fraction = right roll = - raw bank
    return out


def sim_open(u, ts, K0, c, tau, lam, td, dt=0.005):
    p = phi = 0.0
    t, i, res = 0.0, 0, []
    k = K0 * (1 + c * abs(u) / 1000.0)
    for T in ts:
        while t < T:
            uu = u if t >= td else 0.0
            dp = (k * uu / 1000.0 - p) / tau + lam * phi
            p += dp * dt
            phi += p * dt
            t += dt
        res.append(phi)
    return res


def cost(par, steps):
    e = n = 0
    for u, s in steps:
        ts = [x[0] for x in s]
        m = sim_open(u, ts, *par)
        e += sum((a - b[1]) ** 2 for a, b in zip(m, s))
        n += len(s)
    return math.sqrt(e / n)


steps = load()
best = None
for K0 in [2.0 + 0.25 * i for i in range(17)]:
    for c in [0.0, 0.05, 0.1, 0.15, 0.2]:
        for tau in [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6]:
            for lam in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]:
                for td in [0.0, 0.05, 0.1, 0.15]:
                    j = cost((K0, c, tau, lam, td), steps)
                    if best is None or j < best[0]:
                        best = (j, (K0, c, tau, lam, td))
rms, (K0, c, tau, lam, td) = best
print(f"fit: K0 {K0:.2f} °/s per 1 000 counts, c {c:.2f} per 1 000 counts (K at 500/1 000/2 000/4 000 counts "
      f"{K0*(1+c*0.5):.2f}/{K0*(1+c):.2f}/{K0*(1+c*2):.2f}/{K0*(1+c*4):.2f}), tau {tau:.2f} s, lam {lam:.2f} 1/s², "
      f"td {td:.2f} s, rms {rms:.2f}°")
for u, s in steps:
    m = sim_open(u, [x[0] for x in s], K0, c, tau, lam, td)
    print(f"  u {u:+6.0f}: bank end meas {s[-1][1]:+6.1f}° model {m[-1]:+6.1f}° (t {s[-1][0]:.1f} s)")


def closed(kp, kd, ki, period, delay_passes=1, tgt=10.0, phi0=0.0, t_end=30.0, lim=8000, dt=0.005, ka=1.0):
    """Sampled PID on bank (landing_test sign convention folded out: + command -> + roll). The aileron command is
    updated once per `period`; the bank/rate used were read `delay_passes` passes earlier (data age)."""
    p, phi, t = 0.0, phi0, 0.0
    integ, u, hist, next_t = 0.0, 0.0, [], 0.0
    prev_phi, pk, trace = phi0, 0.0, []
    applied = []                                         # (time it acts, value)
    while t < t_end:
        if t >= next_t:
            hist.append((phi, (phi - prev_phi) / period))
            prev_phi = phi
            ph, pr = hist[-1 - delay_passes] if len(hist) > delay_passes else hist[0]
            e = ph - tgt
            integ = max(-30.0, min(30.0, integ + e * period))
            u = max(-lim, min(lim, -ka * (kp * e + kd * pr + ki * integ)))
            applied.append((t + td, u))
            next_t += period
        uu = 0.0
        for ta, v in applied:
            if ta <= t:
                uu = v
        if len(applied) > 4:
            applied = applied[-4:]
        k = K0 * (1 + c * abs(uu) / 1000.0)
        dp = (k * uu / 1000.0 - p) / tau + lam * phi
        p += dp * dt
        phi += p * dt
        t += dt
        trace.append((t, phi))
    over = max(x[1] for x in trace) - tgt
    tail = [x[1] for x in trace if x[0] > t_end - 10]
    amp = (max(tail) - min(tail)) / 2
    settle = next((x[0] for x in reversed(trace) if abs(x[1] - tgt) > 1.0), 0.0)
    return over, amp, settle


print("\nclosed loop (bank-target step 0 -> 10°; overshoot, residual oscillation amplitude in the last 10 s, last time "
      "outside ±1°):")
cases = [("landing_test now 250/150/60 @ 0.55 s", 250, 150, 60, 0.55),
         ("landing_test now 250/150/60 @ 0.30 s", 250, 150, 60, 0.30),
         ("landing_test now 250/150/60 @ 0.16 s", 250, 150, 60, 0.16),
         ("dry2 scaled x0.77 @ 0.55 s", 192, 115, 60, 0.55)]
for kp in (100, 150, 200):
    for kd in (40, 80, 120):
        for ki in (0, 10, 20):
            cases.append((f"cand {kp}/{kd}/{ki} @ 0.55 s", kp, kd, ki, 0.55))
for name, kp, kd, ki, per in cases:
    o, a, s = closed(kp, kd, ki, per)
    o2, a2, s2 = closed(kp, kd, ki, per, tgt=0.0, phi0=20.0)
    print(f"  {name:38s} step: over {o:+5.1f}°, osc ±{a:4.1f}°, settle {s:5.1f} s | 20° upset: osc ±{a2:4.1f}°, "
          f"settle {s2:5.1f} s")
