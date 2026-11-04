"""C4 roll rate (test plan C4 / T3-K): aileron steps at a CR-2144 flight condition, steady roll rate vs. aileron deflection.

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE - never position from the ground):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\roll_test.py <output.csv> [steps=0.25,0.5] [alt=15000] [ias=465]
Reference (docs/data/nasa_cr2144_f104a.md): δa = SUM of both ailerons; p_ss = -L'δa δa / L'p: F/C 4 (15 000 ft, M 0.90,
465 KCAS) 9.56 1/s per rad of δa -> full gear-up aileron (±9.75°, δa 19.5°) ≈ 186°/s.
Sequence: set_pos, AP off, gear/flaps up, trim 2.5° (≈ level trim at 460 KIAS), throttle PI holds the IAS, elevator PI
holds the altitude; 15 s settle; per step: aileron step to the right (stick fraction x full), ELEVATOR FROZEN during the
roll, stop after 330° bank change (FM 5-14: full-deflection rolls ≤ 360°) or 3.5 s, then wings level 10 s.
Evaluation per step: actual aileron deflections (L/R), sum δa, peak and steady roll rate (mean where |p| > 0.85 peak).
End: wings level -> MCP `position` routine (AP verified). Abort: |pitch| > 25° outside a roll, IAS < 300.
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
STEPS = [float(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.25, 0.5]
ALT0 = float(sys.argv[3]) if len(sys.argv) > 3 else 15000.0
IAS0 = float(sys.argv[4]) if len(sys.argv) > 4 else 465.0
DEG = 57.29578
HDG, LAT, LON = 263.4, 48.36, 11.9
FULL = 16383

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
sm.set_pos(ALT0, LAT, LON, int(IAS0), -2.0, 0.0, HDG, 0)
time.sleep(1.0)
ev("GEAR_UP")
ev("FLAPS_UP")
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", 2.5 / DEG)
    time.sleep(0.2)
    if abs(g("ELEVATOR_TRIM_POSITION") * DEG - 2.5) < 0.3:
        break
print(f"roll test at {ALT0:.0f} ft / {IAS0:.0f} KIAS, weight {g('TOTAL_WEIGHT'):.0f} lb, steps {STEPS}")

st = {"integ": 0.0, "th": 9000.0, "vs_f": 0.0, "integ_b": 0.0}
rows, reason = [], "done"
t0 = prev_t = time.time()
prev_alt, prev_th, prev_bank = g("PLANE_ALTITUDE"), -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG
bank_unw = prev_bank
phase, k, phase_t, bank_start, el_frozen = "settle", 0, t0, 0.0, 0.0
while True:
    t = time.time()
    dt = max(t - prev_t, 0.03)
    prev_t = t
    alt, ias = g("PLANE_ALTITUDE") or prev_alt, g("AIRSPEED_INDICATED")
    theta, bank = -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG
    d_b = (bank - prev_bank + 180.0) % 360.0 - 180.0
    bank_unw += d_b
    p = d_b / dt                                   # raw bank rate, deg/s (raw bank: + = left)
    q = (theta - prev_th) / dt
    st["vs_f"] = 0.5 * st["vs_f"] + 0.5 * (alt - prev_alt) / dt * 60
    prev_alt, prev_th, prev_bank = alt, theta, bank
    el = t - phase_t
    ail = 0.0
    if phase == "settle":
        if el > 15:
            phase, phase_t, bank_start = "roll", t, bank_unw
            el_frozen = st.get("el_cmd", 0.0)
    elif phase == "roll":
        ail = -STEPS[k] * FULL                     # right roll (+axis = left)
        if abs(bank_unw - bank_start) > 330.0 or el > 3.5:
            phase, phase_t = "level", t
    elif phase == "level":
        if el > 10:
            k += 1
            if k >= len(STEPS):
                break
            phase, phase_t, bank_start = "roll", t, bank_unw
            el_frozen = st.get("el_cmd", 0.0)
    if phase in ("settle", "level"):
        e_b = bank                                 # wings level (landing_test aileron law)
        st["integ_b"] = clamp(st["integ_b"] + e_b * dt, -30.0, 30.0)
        ail = clamp(-(250.0 * e_b + 150.0 * p + 60.0 * st["integ_b"]), -8000, 8000)
        err = (st["vs_f"] - clamp(4.0 * (ALT0 - alt), -1500.0, 1500.0)) / 60.0
        st["integ"] = clamp(st["integ"] + err * dt, -200, 200)
        ks = clamp((185.0 / max(ias, 100.0)) ** 2, 0.25, 1.0)
        st["el_cmd"] = clamp(ks * (300.0 * err + 10.0 * st["integ"] + 150.0 * q), -8000, 6000)
        ev("AXIS_ELEVATOR_SET", int(st["el_cmd"]))
    else:
        ev("AXIS_ELEVATOR_SET", int(el_frozen))
    ev("AXIS_AILERONS_SET", int(ail))
    st["th"] = clamp(st["th"] + 40.0 * (IAS0 - ias) * dt, 3000.0, 11141.0)
    ev("THROTTLE1_SET", int(st["th"]))
    if (phase != "roll" and abs(theta) > 25) or ias < 300:
        reason = f"ABORT: pitch {theta:.0f}°, IAS {ias:.0f}, phase {phase}"
        break
    rows.append([round(t - t0, 3), phase, k, round(ias, 1), round(alt), round(bank, 1), round(bank_unw, 1), round(p, 1),
                 round(g("AILERON_LEFT_DEFLECTION") * DEG, 2), round(g("AILERON_RIGHT_DEFLECTION") * DEG, 2),
                 round(g("INCIDENCE_ALPHA") * DEG, 2), round(g("INCIDENCE_BETA") * DEG, 2), round(theta, 1)])
    time.sleep(0.02)

for n in ("AXIS_AILERONS_SET", "AXIS_ELEVATOR_SET"):
    ev(n, 0)
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "phase", "step", "ias", "alt", "bank", "bank_unw", "p_dps", "ail_l", "ail_r", "alpha", "beta", "pitch"])
    w.writerows(rows)
print(reason)
for i, frac in enumerate(STEPS):
    r = [x for x in rows if x[1] == "roll" and x[2] == i]
    if len(r) < 3:
        continue
    pk = max(abs(x[7]) for x in r)
    steady = [abs(x[7]) for x in r if abs(x[7]) > 0.85 * pk]
    dl = sum(abs(x[8]) for x in r[len(r) // 2:]) / len(r[len(r) // 2:])
    dr = sum(abs(x[9]) for x in r[len(r) // 2:]) / len(r[len(r) // 2:])
    da = dl + dr
    p_cr = 9.56 * da / DEG * DEG                  # F/C 4: p = 9.56 1/s x δa[rad] -> deg/s = 9.56 x δa[deg]
    print(f"step {frac:.2f}: aileron L {dl:.1f}° R {dr:.1f}° (sum δa {da:.1f}°), roll rate peak {pk:.0f}°/s, steady "
          f"{sum(steady) / len(steady):.0f}°/s; CR-2144 F/C 4 for this δa: {p_cr:.0f}°/s; bank change "
          f"{abs(r[-1][6] - r[0][6]):.0f}° in {r[-1][0] - r[0][0]:.1f} s, IAS {r[0][3]:.0f}")
print(f"{len(rows)} samples -> {out}")
pos = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "mcp_f104", "sim_actions.py"),
                      "position", "16500", "500", "263", "48.36", "11.9", "8000", "wl"],
                     capture_output=True, text=True, timeout=120)
print("End: position routine ->", (pos.stdout.strip().splitlines() or ["no output"])[-1][:140])

# postconditions (test process step 6, tools/post.py): jet in a safe, defined state after the script
post = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.py"), "air"],
                      capture_output=True, text=True, timeout=60)
print((post.stdout.strip().splitlines() or ["POST FAIL: no output"])[-1])
