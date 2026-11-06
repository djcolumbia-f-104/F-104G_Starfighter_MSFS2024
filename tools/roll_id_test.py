"""Roll-response identification for the landing bank loop (S3 landing variants, 2026-11-06; card S3-bank-loop.md).

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE - never position from the ground):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\roll_id_test.py <output.csv>
      [cfg=to|land|up] [ias=210] [alt=12000] [steps=0.03,0.06,0.12,0.25]
Why: the landing_test bank PID (250/150/60 counts per deg, deg/s, deg s) limit-cycled at 210 KIAS with TAKEOFF flaps
(F6 dry runs, lesson 20). The plant is nonlinear in the cfg: aileron_scaling_table (template) 0:0.3, ±10°:0.5, ±20°:1
and aileron_elasticity_table 1 up to q 100 psf, 0.5 from 250 psf. This tool measures the OPEN-LOOP response
(axis counts -> roll rate) at the landing speed/configuration so that the loop can be designed at the desk.
Sequence: AP off, set_pos (speed argument ≈ IAS) nose 6° up, gear down, flaps per cfg, trim preset (as landing_test),
throttle PI on IAS, elevator PI on altitude (roll_test law, gain x (185/IAS)²), bank PID = the landing_test gains (they
flew level cleanly at 210 KIAS in F6 dry 1). Settle 20 s, then per step fraction f: aileron step +f (right roll) and later
-f (left roll) of full axis, ELEVATOR FROZEN, for 2.5 s or until the bank changed 40°, then 10 s wings level.
During a step ONLY the bank is read (fast; repeated values are dropped), the aileron deflections once at 1.5 s.
Fit per step: bank(t) = phi0 + p_ss [(t - td) - tau (1 - exp(-(t - td) / tau))] for t > td (first-order roll mode +
dead time). Output: p_ss (deg/s), p_ss per 1 000 counts, tau, td, measured aileron deflections, loop period.
Abort: IAS < V_MIN (cfg to 190 / land 170 / up 220) or > 255 (gear limit 260), |pitch| > 25°, |bank| > 60° outside a
step, altitude off by > 1 500 ft -> ailerons 0, wings-level, Military, then the position routine (unchanged).
End: MCP `position` routine (set_pos 16 500 ft / 500 kt retracts gear and flaps at speed) + tools/post.py air.
"""
import csv
import math
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
opts = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
CFG = opts.get("cfg", "to")
IAS0 = float(opts.get("ias", 210))
ALT0 = float(opts.get("alt", 12000))
STEPS = [float(v) for v in opts.get("steps", "0.03,0.06,0.12,0.25").split(",")]
DEG = 57.29578
HDG, LAT, LON = 263.4, 48.36, 11.9
FULL = 16383
KP_B, KD_B, KI_B = 250.0, 150.0, 60.0                   # landing_test bank PID (counts per deg, deg/s, deg s)
TRIM_DEG = {"land": 5.2, "to": 7.0, "up": 8.0}[CFG]     # landing_test presets
V_MIN = {"land": 170.0, "to": 190.0, "up": 220.0}[CFG]   # shaker TAKEOFF ≈ 182-185 KIAS (H2), LAND ≈ 144-149
STEP_S, STEP_BANK = 2.5, 40.0

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 2000:
    sm.exit()
    sys.exit("ABORT: on the ground or fuel < 2 000 lb")
for _ in range(3):
    if g("AUTOPILOT_MASTER") != 1:
        break
    ev("AP_MASTER")
    time.sleep(0.3)
ev("SPOILERS_OFF")
sm.set_pos(ALT0, LAT, LON, int(IAS0 - 10), -6.0, 0.0, HDG, 0)   # S9-ID run 1: speed argument 210 gave 223 KIAS
time.sleep(1.0)
ev("GEAR_DOWN")
ev({"land": "FLAPS_DOWN", "to": "FLAPS_1", "up": "FLAPS_UP"}[CFG])
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", TRIM_DEG / DEG)
    time.sleep(0.2)
    if abs(g("ELEVATOR_TRIM_POSITION") * DEG - TRIM_DEG) < 0.3:
        break
print(f"roll id cfg {CFG} at {ALT0:.0f} ft / {IAS0:.0f} KIAS, weight {g('TOTAL_WEIGHT'):.0f} lb, trim "
      f"{g('ELEVATOR_TRIM_POSITION') * DEG:.1f}°, steps {STEPS} (x {FULL} counts, both directions)")

st = {"integ": 0.0, "th": 8500.0, "th_i": 8500.0, "vs_f": 0.0, "integ_b": 0.0, "el_cmd": 0.0}
rows, fast, steps_info, reason = [], [], [], "done"
t0 = prev_t = time.time()
prev_alt, prev_th, prev_bank = g("PLANE_ALTITUDE"), -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG
plan = [s for f in STEPS for s in (f, -f)]               # + = right roll
k, phase, phase_t, n_pass, ias = 0, "settle", t0, 0, IAS0


def wings_level(bank, p, dt):
    st["integ_b"] = clamp(st["integ_b"] + bank * dt, -30.0, 30.0)
    return clamp(-(KP_B * bank + KD_B * p + KI_B * st["integ_b"]), -8000, 8000)


while True:
    t = time.time()
    dt = max(t - prev_t, 0.03)
    prev_t = t
    if phase == "step":
        # fast part: only the bank (and the clock); commanded aileron constant, elevator frozen
        b = g("PLANE_BANK_DEGREES") * DEG
        if b and (not fast or b != fast[-1][2]):
            fast.append((k, t - phase_t, b))
        if not info.get("ail") and t - phase_t > 1.5:
            info["ail"] = (g("AILERON_LEFT_DEFLECTION") * DEG, g("AILERON_RIGHT_DEFLECTION") * DEG)
            info["ias"] = g("AIRSPEED_INDICATED")
        if abs(b - info["b0"]) > STEP_BANK or t - phase_t > STEP_S:
            ev("AXIS_AILERONS_SET", 0)
            st["integ_b"] = 0.0
            # refresh ALL rate references (stale altitude/pitch over a tiny dt would spike the VS and the elevator)
            prev_alt, prev_th = g("PLANE_ALTITUDE") or prev_alt, -g("PLANE_PITCH_DEGREES") * DEG
            st["vs_f"] = 0.0
            prev_bank, prev_t = b, time.time()
            phase, phase_t = "level", time.time()
            k += 1
        continue
    n_pass += 1
    alt, ias = g("PLANE_ALTITUDE") or prev_alt, g("AIRSPEED_INDICATED") or ias
    theta, bank = -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG
    p = (bank - prev_bank) / dt                          # raw bank rate (raw bank: + = left)
    q = (theta - prev_th) / dt
    st["vs_f"] = 0.5 * st["vs_f"] + 0.5 * (alt - prev_alt) / dt * 60
    prev_alt, prev_th, prev_bank = alt, theta, bank
    el = t - phase_t
    ail = wings_level(bank, p, dt)
    err = (st["vs_f"] - clamp(4.0 * (ALT0 - alt), -1500.0, 1500.0)) / 60.0
    st["integ"] = clamp(st["integ"] + err * dt, -200, 200)
    ks = clamp((185.0 / max(ias, 100.0)) ** 2, 0.25, 1.0)
    st["el_cmd"] = clamp(ks * (300.0 * err + 10.0 * st["integ"] + 150.0 * q), -8000, 6000)
    ev("AXIS_ELEVATOR_SET", int(st["el_cmd"]))
    # S9-ID run 1: a pure integrator (40/kt/s) wound down to 3 000 after the set_pos overshoot (223 KIAS), the J79 spooled
    # down and the speed fell to 190 (abort) -> PI with a base near the level-flight setting and a floor above idle
    st["th_i"] = clamp(st["th_i"] + 15.0 * (IAS0 - ias) * dt, 6000.0, 11141.0)
    st["th"] = clamp(st["th_i"] + 200.0 * (IAS0 - ias), 5000.0, 11141.0)
    ev("THROTTLE1_SET", int(st["th"]))
    ev("AXIS_AILERONS_SET", int(ail))
    rows.append([round(t - t0, 3), phase, k, round(ias, 1), round(alt), round(bank, 1), round(p, 1), round(theta, 1),
                 int(ail), int(st["el_cmd"]), int(st["th"])])
    if ias < V_MIN or ias > 255 or abs(theta) > 25 or abs(bank) > 60 or abs(alt - ALT0) > 1500:
        reason = f"ABORT: IAS {ias:.0f}, pitch {theta:.0f}°, bank {bank:.0f}°, alt {alt:.0f}, phase {phase}"
        break
    # next step only when wings level and quiet (|bank| < 2°, |p| < 2°/s)
    ready = abs(bank) < 2.0 and abs(p) < 2.0
    if (phase == "settle" and el > 20 and ready) or (phase == "level" and el > 10 and ready):
        if k >= len(plan):
            break
        info = {"f": plan[k], "b0": bank, "t_abs": t - t0}
        steps_info.append(info)
        ev("AXIS_ELEVATOR_SET", int(st["el_cmd"]))
        ev("AXIS_AILERONS_SET", int(-plan[k] * FULL))     # right roll = negative axis
        phase, phase_t = "step", time.time()
        fast.append((k, 0.0, bank))
    elif el > 40:
        reason = f"ABORT: not wings-level within 40 s (bank {bank:.1f}°, p {p:.1f}°/s, phase {phase})"
        break
    time.sleep(0.02)

ev("AXIS_AILERONS_SET", 0)
if reason != "done":                                       # recovery: wings level for 4 s at Military, then position
    ev("THROTTLE1_SET", 11141)
    t_r = prev_t = time.time()
    prev_bank = g("PLANE_BANK_DEGREES") * DEG
    while time.time() - t_r < 4:
        bank = g("PLANE_BANK_DEGREES") * DEG
        dt = max(time.time() - prev_t, 0.03)
        prev_t = time.time()
        ev("AXIS_AILERONS_SET", int(wings_level(bank, (bank - prev_bank) / dt, dt)))
        prev_bank = bank
    ev("AXIS_AILERONS_SET", 0)
ev("AXIS_ELEVATOR_SET", 0)
sm.exit()
dur = rows[-1][0] if rows else 1
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "phase", "step", "ias", "alt", "bank", "p_dps", "pitch", "ail_cmd", "el_cmd", "throttle"])
    w.writerows(rows)
with open(out.replace(".csv", "_steps.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["step", "t_step", "bank"])
    w.writerows(fast)
print(reason)
print(f"main loop {n_pass / max(dur, 1):.1f} Hz outside the steps; logs {out} + _steps.csv")


def fit(ts, bs):
    """Grid over tau 0.05..2.0 s and td 0..0.5 s; linear least squares for phi0 and p_ss."""
    best = None
    for ti in range(1, 41):
        tau = ti * 0.05
        for di in range(0, 26):
            td = di * 0.02
            basis = []
            for t in ts:
                x = max(t - td, 0.0)
                basis.append((1.0, x - tau * (1 - math.exp(-x / tau))))
            s11 = sum(b[0] * b[0] for b in basis)
            s12 = sum(b[0] * b[1] for b in basis)
            s22 = sum(b[1] * b[1] for b in basis)
            v1 = sum(b[0] * y for b, y in zip(basis, bs))
            v2 = sum(b[1] * y for b, y in zip(basis, bs))
            det = s11 * s22 - s12 * s12
            if abs(det) < 1e-12:
                continue
            c0, c1 = (v1 * s22 - v2 * s12) / det, (s11 * v2 - s12 * v1) / det
            res = sum((y - c0 - c1 * b[1]) ** 2 for b, y in zip(basis, bs))
            if best is None or res < best[0]:
                best = (res, tau, td, c0, c1)
    return best


for i, info in enumerate(steps_info):
    s = [(t, b) for kk, t, b in fast if kk == i]
    if len(s) < 6:
        print(f"step {info['f']:+.2f}: too few samples ({len(s)})")
        continue
    res, tau, td, c0, c1 = fit([x[0] for x in s], [x[1] for x in s])
    counts = info["f"] * FULL
    p_ss = -c1                                              # raw bank + = left; report + = right roll for +f
    al, ar = info.get("ail", (float("nan"), float("nan")))
    rate = len(s) / max(s[-1][0], 0.1)
    print(f"step {info['f']:+.2f} ({counts:+.0f} counts) at {info.get('ias', 0):.0f} KIAS: p_ss {p_ss:+.1f}°/s "
          f"({p_ss / counts * 1000:.2f}°/s per 1 000 counts), tau {tau:.2f} s, td {td:.2f} s, fit rms "
          f"{math.sqrt(res / len(s)):.2f}°, {len(s)} samples ({rate:.0f} Hz), aileron L {al:.2f}° R {ar:.2f}° "
          f"(sum {abs(al) + abs(ar):.2f}°), bank change {s[-1][1] - s[0][1]:+.1f}° in {s[-1][0]:.1f} s")

pos = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "mcp_f104", "sim_actions.py"),
                      "position", "16500", "500", "263", "48.36", "11.9", "8800", "wl"],
                     capture_output=True, text=True, timeout=120)
print("End: position routine ->", (pos.stdout.strip().splitlines() or ["no output"])[-1][:140])
post = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.py"), "air"],
                      capture_output=True, text=True, timeout=90)
print((post.stdout.strip().splitlines() or ["POST FAIL: no output"])[-1])
