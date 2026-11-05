"""Test T3-E2: steady heading sideslip with opposite aileron, closed loop (v2, 2026-11-05: rework after C4).

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE on the AP, e.g. after `position`):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\sideslip_test.py <output.csv> [rudder_s=15] [rudder_fraction=1.0] [alt=15000] [ias=460] [sas=on|off]
Why v2: v1 found the axis signs with probe inputs and used guessed bank gains; after C4 (roll power ≈ 3x) the probe rolled
the jet to 53°/57° (aborts 2026-11-03). v2 uses the KNOWN signs (spiral_test/roll_test: +aileron axis -> raw bank
increases, raw PLANE_BANK + = left; +elevator axis = nose down; +rudder axis = nose left) and the loops proven after C4 in
roll_test.py at 465 KIAS (aileron PID 250/150/60, elevator PI with q-scaled gains + pitch-rate damping, throttle PI on IAS).
Sequence: set_pos at alt / ias (CR-2144 F/C 4 ≈ 15 000 ft M 0.9), AP off, gear/flaps up, trim 2.5°, yaw damper ON by
default (FM: dampers at all times; 1 s washout -> steady β and aileron unchanged, sas_step_test 2026-11-03). 2026-11-05 S7-E2:
with the damper OFF (SAS-off reference of all earlier T3-E2 runs) the bank loop coupled into the lightly damped Dutch roll
(1.8 s, diverging to 27-37° bank) even with a 164 ms loop -> "sas=off" only for comparison runs. 15 s settle (phase 0); rudder ramps to the fraction
over 2 s ("r"), held rudder_s (phase 1); ramps out over 2 s and 8 s wings level (phase 2). Bank held at 0 by the aileron
loop throughout -> the aileron needed against the roll due to sideslip.
Evaluation (second half of phase 1, as the MCP wrapper): β/δr and δa/δr with δa = AILERON_LEFT_DEFLECTION (one aileron,
as rounds E / AP-11 / ISA 2026-10-29). Reference CR-2144 Table III-9: β/δr 0.32-0.42, δa/δr 0.27-0.47; before C4 (ISA,
2026-10-29) 0.34 / 0.43, AP-11 (M 0.9) 0.35 / 0.41. Prediction after C4 (aileron_effectiveness x1.17, roll_stability only
damping): β/δr unchanged ≈ 0.34, δa/δr ≈ 0.43/1.17 ≈ 0.37.
Abort (-> rudder 0, wings level, position): |bank| > 30°, pitch outside -10..+15°, altitude ±1 000 ft, IAS outside 380-540.
End: damper ON (FM default), MCP `position` routine, tools/post.py.
"""
import csv
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event
from SimConnect.RequestList import Request

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
num = [a for a in sys.argv[2:] if "=" not in a]
RUD_S = float(num[0]) if len(num) > 0 else 15.0
RUD_F = float(num[1]) if len(num) > 1 else 1.0
ALT0 = float(num[2]) if len(num) > 2 else 15000.0
IAS0 = float(num[3]) if len(num) > 3 else 460.0
SAS_OFF = "sas=off" in sys.argv[2:]
DEG = 57.29578
HDG, LAT, LON = 263.4, 48.36, 11.9
FULL = 16383

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)
sas_off = Request((b"L:F104_SAS_YAW_OFF", b"number"), sm, _time=0, _settable=True)


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
sas_off.value = 1.0 if SAS_OFF else 0.0
print(f"sideslip test at {ALT0:.0f} ft / {IAS0:.0f} KIAS, weight {g('TOTAL_WEIGHT'):.0f} lb, rudder {RUD_F:.2f} x full for "
      f"{RUD_S:.0f} s, yaw damper {'OFF' if SAS_OFF else 'ON'}")

st = {"integ": 0.0, "th": 9000.0, "vs_f": 0.0, "integ_b": 0.0, "el_cmd": 0.0}
rows, reason = [], "done"
t0 = prev_t = time.time()
prev_alt, prev_th, prev_bank = g("PLANE_ALTITUDE"), -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG
T_SETTLE, T_RAMP, T_LEVEL = 15.0, 2.0, 8.0
t_end = T_SETTLE + 2 * T_RAMP + RUD_S + T_LEVEL
# 2026-11-05 (S7-E2 ss100): with all 13 reads per pass the loop ran at 0.41 s and the bank PID drove the lightly damped
# Dutch roll (damper off) into a divergent oscillation (bank ±15 -> -37°, abort). Every SimVar read costs ≈ 30 ms ->
# fast loop reads only bank / pitch / altitude; IAS every 5th pass, the logging channels every 4th pass.
n_pass, ias, log_ch = 0, IAS0, (0.0, 0.0, 0.0, 0.0)
loop_dt = []
while True:
    t = time.time()
    dt = max(t - prev_t, 0.03)
    loop_dt.append(t - prev_t)
    prev_t = t
    el = t - t0
    if el > t_end:
        break
    n_pass += 1
    alt = g("PLANE_ALTITUDE") or prev_alt
    if n_pass % 5 == 1:
        ias = g("AIRSPEED_INDICATED") or ias
    theta, bank = -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG
    p = ((bank - prev_bank + 180.0) % 360.0 - 180.0) / dt        # raw bank rate (+ = rolling left)
    q = (theta - prev_th) / dt
    st["vs_f"] = 0.5 * st["vs_f"] + 0.5 * (alt - prev_alt) / dt * 60
    prev_alt, prev_th, prev_bank = alt, theta, bank
    # rudder schedule
    if el < T_SETTLE:
        phase, frac = "0", 0.0
    elif el < T_SETTLE + T_RAMP:
        phase, frac = "r", (el - T_SETTLE) / T_RAMP
    elif el < T_SETTLE + T_RAMP + RUD_S:
        phase, frac = "1", 1.0
    elif el < T_SETTLE + 2 * T_RAMP + RUD_S:
        phase, frac = "2", 1.0 - (el - T_SETTLE - T_RAMP - RUD_S) / T_RAMP
    else:
        phase, frac = "2", 0.0
    cmd_rud = RUD_F * FULL * frac
    ev("AXIS_RUDDER_SET", int(cmd_rud))
    # aileron PID holds bank 0 + feed-forward against the roll due to sideslip. 2026-11-05 S7-E2: the roll_test gains
    # 250/150/60 diverged here (≈ 0.011 °/s per count at 460 KIAS, crossover ≈ 5.5 rad/s, roll mode + 0.16-0.39 s loop
    # delay leave ≈ 25° phase margin or less) -> 100/50/30: crossover ≈ 1 rad/s, ≈ 80° margin. Feed-forward 0.26 x rudder
    # command (ss50: ≈ 2 100 counts at 8 192); the measured aileron is whatever holds the bank, so it does not bias δa/δr.
    st["integ_b"] = clamp(st["integ_b"] + bank * dt, -60.0, 60.0)
    cmd_ail = clamp(0.26 * cmd_rud - (100.0 * bank + 50.0 * p + 30.0 * st["integ_b"]), -8000, 8000)
    ev("AXIS_AILERONS_SET", int(cmd_ail))
    # elevator PI on the vertical speed from the altitude error, q-scaled, pitch-rate damping (roll_test)
    err = (st["vs_f"] - clamp(4.0 * (ALT0 - alt), -1500.0, 1500.0)) / 60.0
    st["integ"] = clamp(st["integ"] + err * dt, -200, 200)
    ks = clamp((185.0 / max(ias, 100.0)) ** 2, 0.25, 1.0)
    st["el_cmd"] = clamp(ks * (300.0 * err + 10.0 * st["integ"] + 150.0 * q), -8000, 6000)
    ev("AXIS_ELEVATOR_SET", int(st["el_cmd"]))
    # throttle PI holds the IAS (rudder drag), no afterburner
    st["th"] = clamp(st["th"] + 40.0 * (IAS0 - ias) * dt, 3000.0, 11141.0)
    ev("THROTTLE1_SET", int(st["th"]))
    if n_pass % 4 == 0:
        rows.append([round(el, 2), phase, round(ias, 1), round(alt), round(bank, 2), round(g("INCIDENCE_BETA") * DEG, 2),
                     round(g("RUDDER_DEFLECTION") * DEG, 2), round(g("AILERON_LEFT_DEFLECTION") * DEG, 2),
                     round(g("ELEVATOR_DEFLECTION") * DEG, 2), int(cmd_ail), int(st["el_cmd"]), int(cmd_rud)])
    if abs(bank) > 30 or not -10 < theta < 15 or abs(alt - ALT0) > 1000 or not 380 < ias < 540:
        reason = f"ABORT: bank {bank:.0f}°, pitch {theta:.1f}°, alt {alt:.0f} ft, IAS {ias:.0f} (phase {phase})"
        break

ev("AXIS_RUDDER_SET", 0)
t_l = time.time()                                                  # wings level 6 s (also after an abort)
pb, pt = g("PLANE_BANK_DEGREES") * DEG, time.time()
while time.time() - t_l < 6:
    bank, tb = g("PLANE_BANK_DEGREES") * DEG, time.time()
    p = (bank - pb) / max(tb - pt, 0.03)
    pb, pt = bank, tb
    ev("AXIS_AILERONS_SET", int(clamp(-(100.0 * bank + 50.0 * p), -4000, 4000)))
    time.sleep(0.05)
for n in ("AXIS_AILERONS_SET", "AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET"):
    ev(n, 0)
sas_off.value = 0.0                                                # FM default: damper ON
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "phase", "ias", "alt", "bank", "beta", "rud", "ail", "elev", "cmd_ail", "cmd_elev", "cmd_rud"])
    w.writerows(rows)
ld = sorted(loop_dt[5:]) or [0.0]
print(f"{reason}; {len(rows)} samples -> {out}; control loop period median {ld[len(ld) // 2] * 1000:.0f} ms, "
      f"95 % {ld[int(len(ld) * 0.95)] * 1000:.0f} ms")
hold = [r for r in rows if r[1] == "1"]
late = hold[len(hold) // 2:]
if len(late) > 5:
    m = lambda i: sum(r[i] for r in late) / len(late)
    b_r, a_r = abs(m(5) / m(6)), abs(m(7) / m(6))
    ok = 0.32 <= b_r <= 0.42 and 0.27 <= a_r <= 0.47
    print(f"Result: full rudder (2nd half of the hold, {len(late)} samples): IAS {m(2):.0f} KIAS, β {m(5):.2f}°, rudder "
          f"{m(6):.2f}°, aileron {m(7):.2f}°, bank {m(4):.1f}° -> β/δr {b_r:.2f}, δa/δr {a_r:.2f} "
          f"(CR-2144 0.32-0.42 / 0.27-0.47; predicted 0.34 / 0.37) -> T3-E2 {'PASS' if ok and reason == 'done' else 'CHECK'}")
pos = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_f104", "sim_actions.py"),
                      "position", "16500", "520", "263", "48.36", "11.9", "8800", "wl"],
                     capture_output=True, text=True, timeout=120)
print("End: position routine ->", (pos.stdout.strip().splitlines() or ["no output"])[-1][:140])
post = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.py"), "air"],
                      capture_output=True, text=True, timeout=90)
print((post.stdout.strip().splitlines() or ["POST FAIL: no output"])[-1])
