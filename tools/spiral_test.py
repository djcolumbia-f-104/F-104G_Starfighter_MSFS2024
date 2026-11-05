"""C6 spiral stability (test plan C6, sortie S2; 2026-11-04): release from 30° bank, ailerons and rudder free.

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE in level flight on the AP, e.g. after `position`):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\spiral_test.py <output.csv> [bank=30] [free_s=40]
Sequence per side (right, then left): AP off; aileron PID rolls to the bank and an elevator PI holds the altitude (10 s
settle); then ailerons and rudder released (axes 0), the elevator loop keeps holding the altitude (classic spiral test); bank
logged for free_s. Evaluation: fit |bank|(t) = b0 exp(t / T) over the free phase -> time to double (T ln 2, divergent) or to
halve (convergent). Reference: MSFS "Testing the aircraft": spiral - doubling of a 30° bank in more than 20 s; the F-104
(anhedral, FM 6-2) is expected near neutral. Yaw damper at its default (ON, as in the FM).
Signs (landing_test.py): +aileron axis -> raw bank increases, raw PLANE_BANK positive = left bank, +elevator axis = nose down.
Abort: |bank| > 60°, pitch outside -15..+20°, altitude loss > 2 000 ft. End: wings level by the aileron loop (8 s), MCP
`position` routine, tools/post.py.
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
BANK = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
FREE = float(sys.argv[3]) if len(sys.argv) > 3 else 40.0
DEG = 57.29578

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def g(name):
    return aq.get(name) or 0


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 1800:
    sm.exit()
    sys.exit("ABORT: on the ground or fuel < 1 800 lb")
for _ in range(3):
    if g("AUTOPILOT_MASTER") != 1:
        break
    ev("AP_MASTER")
    time.sleep(0.3)
alt0 = g("PLANE_ALTITUDE")
print(f"spiral test at {alt0:.0f} ft / {g('AIRSPEED_INDICATED'):.0f} KIAS / M {g('AIRSPEED_MACH'):.2f}, "
      f"weight {g('TOTAL_WEIGHT'):.0f} lb, bank {BANK}°, free {FREE} s, AP {g('AUTOPILOT_MASTER'):.0f}")

rows, reason, integ = [], "done", 0.0
results = []
t_start = time.time()
prev = (time.time(), g("PLANE_BANK_DEGREES") * DEG)
prev_theta = -g("PLANE_PITCH_DEGREES") * DEG
for side in (+1, -1):                                       # +1 = right bank (raw bank negative), -1 = left
    target_raw = -side * BANK
    t0 = time.time()
    phase = "roll"
    while True:
        t = time.time()
        dt = max(t - prev[0], 0.02)
        bank = g("PLANE_BANK_DEGREES") * DEG
        p = (bank - prev[1]) / dt
        prev = (t, bank)
        alt, vs = g("PLANE_ALTITUDE"), g("VERTICAL_SPEED")
        theta = -g("PLANE_PITCH_DEGREES") * DEG
        el = t - t0
        q = (theta - prev_theta) / dt                       # pitch rate, nose up positive
        prev_theta = theta
        # elevator PI on the vertical speed from the altitude error + pitch-rate damping (+axis = nose down; landing_test
        # gains 300 per ft/s and KQ 150 at ≈ 180 kt, here scaled to ≈ 460 KIAS: q̄ ≈ 6.5x)
        vs_cmd = clamp(3.0 * (alt0 - alt), -1500.0, 1500.0)
        integ = clamp(integ + (vs_cmd - vs) * dt, -3000.0, 3000.0)
        ev("AXIS_ELEVATOR_SET", int(clamp(-(1.2 * (vs_cmd - vs) + 0.15 * integ) + 25.0 * q, -8000, 4000)))
        if phase == "roll":
            ev("AXIS_AILERONS_SET", int(clamp(250.0 * (target_raw - bank) - 150.0 * p, -4000, 4000)))
            if el > 10.0:
                phase = "free"
                t_free = t
                ev("AXIS_AILERONS_SET", 0)
                ev("AXIS_RUDDER_SET", 0)
        rows.append((round(t - t_start, 2), side, phase, round(bank, 2), round(alt), round(vs), round(theta, 2)))
        if abs(bank) > 60 or not -15 < theta < 20 or alt < alt0 - 2000:
            reason = f"ABORT: bank {bank:.0f}°, pitch {theta:.1f}°, alt {alt:.0f} ft"
            break
        if phase == "free" and t - t_free > FREE:
            break
        time.sleep(0.15)
    free = [(r[0], abs(r[3])) for r in rows if r[1] == side and r[2] == "free" and abs(r[3]) > 0.5]
    if len(free) > 10:
        n = len(free)
        mt = sum(x for x, _ in free) / n
        ml = sum(math.log(b) for _, b in free) / n
        k = sum((x - mt) * (math.log(b) - ml) for x, b in free) / sum((x - mt) ** 2 for x, _ in free)
        tc = (f"doubles in {math.log(2) / k:.0f} s" if k > 1e-4 else f"halves in {-math.log(2) / k:.0f} s" if k < -1e-4
              else "neutral")
        results.append((side, free[0][1], free[-1][1], free[-1][0] - free[0][0], tc, k))
        print(f"{'right' if side > 0 else 'left'}: bank {free[0][1]:.1f}° -> {free[-1][1]:.1f}° in "
              f"{free[-1][0] - free[0][0]:.0f} s -> {tc} (criterion: doubling time > 20 s)")
    if reason != "done":
        break
# wings level (8 s), then the proven position routine
t_l = time.time()
while time.time() - t_l < 8:
    bank = g("PLANE_BANK_DEGREES") * DEG
    ev("AXIS_AILERONS_SET", int(clamp(-250.0 * bank, -4000, 4000)))
    time.sleep(0.15)
for n in ("AXIS_AILERONS_SET", "AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET"):
    ev(n, 0)
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "side", "phase", "bank_raw_deg", "alt", "vs_fpm", "pitch"])
    w.writerows(rows)
print(f"{reason}; {len(rows)} samples -> {out}")
ok = reason == "done" and all(k <= math.log(2) / 20 for *_, k in results)
print(f"C6 spiral: {'PASS' if ok else 'CHECK'} " + "; ".join(f"{'R' if s > 0 else 'L'} {tc}" for s, _, _, _, tc, _ in results))
pos = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "mcp_f104", "sim_actions.py"),
                      "position", "16500", "520", "263", "48.36", "11.9", "8800", "wl"],
                     capture_output=True, text=True, timeout=120)
print("End: position routine ->", (pos.stdout.strip().splitlines() or ["no output"])[-1][:140])

# postconditions (test process step 6, tools/post.py): jet in a safe, defined state after the script
post = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.py"), "air"],
                      capture_output=True, text=True, timeout=90)
print((post.stdout.strip().splitlines() or ["POST FAIL: no output"])[-1])
