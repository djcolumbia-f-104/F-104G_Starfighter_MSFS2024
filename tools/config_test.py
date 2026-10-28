"""Tests B5/B6 (docs/test-plan.md): landing configuration at Military - go-around climb at constant IAS (sawtooth climb,
FM Fig. 6-8) or level flight with speed brakes (flat final, FM 3-41). Test card:
docs/notes/test-cards/B5-B6-landing-config.md.

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\config_test.py <output.csv> <alt_ft MSL> climb|level [ias=170] [sb]
  climb: elevator holds IAS (default 170 KIAS) at Military -> mean rate of climb over the steady part (after 25 s)
  level: elevator holds the start altitude at Military -> IAS it settles at (mean of the last 30 s)
  sb:    speed brakes out (FM 3-41 flat final: speed brakes + LAND flaps + gear at Military ≈ 190-200 KIAS)
Hand flying as in landing_test.py (controllers and signs from there, dry runs 10-15): elevator PI on vertical speed +
pitch-rate damping, ailerons PID on a bank target from the heading error. Trim preset 5.2° with the AP off.
End: FM go-around clean-up (gear up when climbing, flaps TAKEOFF ≥ 180 KIAS, UP ≥ 260 KIAS after 30 s), AP ALT hold.
Abort: IAS < 150 KIAS, |bank| > 30°, pitch outside -10..+20°, AGL < 1 500 ft.
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
out, alt0, mode = sys.argv[1], float(sys.argv[2]), sys.argv[3]
ias_tgt = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "sb" else 170.0
SB = "sb" in sys.argv[4:]
DEG = 57.29578
HDG = 263.4                                     # EDDM 26L direction (true)
LAT, LON = 48.36, 12.10                         # ≈ 11 NM east of EDDM on the extended centreline, flat terrain ≈ 1 400 ft
TRIM_DEG = 5.2
KP_VS, KI_VS, KQ = 300.0, 10.0, 150.0           # landing_test.py
KP_B, KD_B, KI_B = 250.0, 150.0, 60.0

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def wrap(d):
    return (d + 180) % 360 - 180


def ap_master(on):
    for _ in range(3):
        if (g("AUTOPILOT_MASTER") == 1) == on:
            return
        ev("AP_MASTER")
        time.sleep(0.3)


fuel, n1 = g("FUEL_TOTAL_QUANTITY_WEIGHT"), g("TURB_ENG_N1:1")
if fuel < 2500 or n1 < 60:
    sm.exit()
    sys.exit(f"ABORT: fuel {fuel:.0f} lb, N1 {n1:.0f} % - refuel / start the engine first")
ap_master(False)
ev("SPOILERS_OFF")
sm.set_pos(alt0, LAT, LON, 185, -3.0, 0.0, HDG, 0)   # speed ≈ IAS, pitch negative = nose up (landing_test.py)
time.sleep(1.0)
ev("GEAR_DOWN")
ev("FLAPS_DOWN")
ap_master(False)
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", TRIM_DEG / DEG)
    time.sleep(0.2)
    if g("ELEVATOR_TRIM_POSITION") * DEG > TRIM_DEG - 0.3:
        break
if SB:
    ev("SPOILERS_ON")
ev("THROTTLE1_SET", 11141)                            # Military
w = g("TOTAL_WEIGHT")
print(f"{mode} at {alt0:.0f} ft MSL, {'speed brakes OUT, ' if SB else ''}weight {w:.0f} lb, OAT {g('AMBIENT_TEMPERATURE'):.1f} °C, "
      f"trim {g('ELEVATOR_TRIM_POSITION') * DEG:.1f}°" + (f", IAS target {ias_tgt:.0f}" if mode == "climb" else ""))
log = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "simlog.py"),
                        out.replace(".csv", "_simlog.csv"), "300", "3"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

res = {"integ": 0.0, "integ_b": 0.0}
rows, phase, reason = [], "test", ""
t0 = prev_t = time.time()
while time.time() - t0 < 300:
    t = time.time()
    dt = max(t - prev_t, 0.05)
    prev_t = t
    alt, ias, agl = g("PLANE_ALTITUDE"), g("AIRSPEED_INDICATED"), g("PLANE_ALT_ABOVE_GROUND")
    bank, theta = g("PLANE_BANK_DEGREES") * DEG, -g("PLANE_PITCH_DEGREES") * DEG
    hdg = g("PLANE_HEADING_DEGREES_TRUE") * DEG
    if alt == 0 and "prev_alt" in res:                               # failed read
        alt = res["prev_alt"]
    if ias == 0 and "last_ias" in res:
        ias = res["last_ias"]
    res["last_ias"] = ias
    if agl == 0 and "last_agl" in res:                               # B6 run 1: AGL read 0 -> false abort
        agl = res["last_agl"]
    res["last_agl"] = agl
    vs = (alt - res.get("prev_alt", alt)) / dt * 60
    res["prev_alt"] = alt
    res["vs_f"] = 0.5 * res.get("vs_f", vs) + 0.5 * vs
    q = (theta - res.get("prev_theta", theta)) / dt
    p = (bank - res.get("prev_bank", bank)) / dt
    res["prev_theta"], res["prev_bank"] = theta, bank
    el = t - t0

    if phase == "test":
        if mode == "climb":
            vs_tgt = clamp(150.0 * (ias - ias_tgt), -1500.0, 4000.0)   # faster than the target -> climb steeper
        else:
            vs_tgt = clamp(4.0 * (alt0 - alt), -1000.0, 1000.0)
        bad = ias < 150 or abs(bank) > 30 or not -10 < theta < 20 or agl < 1500
        done = el > 120 or (mode == "climb" and alt > alt0 + 3000 and el > 40)
        if bad or done:
            reason = (f"ABORT: IAS {ias:.0f}, bank {bank:.0f}°, pitch {theta:.0f}°, AGL {agl:.0f}" if bad else "test done")
            print(reason)
            phase = "clean-up"
            ev("SPOILERS_OFF")
            ev("THROTTLE1_SET", 16383)
    else:
        # FM go-around clean-up, hand-flown: +1 500 ft/min if the speed allows, gear/flaps per FM, Maximum to 300 KIAS
        vs_tgt = clamp(100.0 * (ias - 170.0), 0.0, 1500.0)
        ev("THROTTLE1_SET", 16383 if ias < 300 else 11141)
        if vs > 500 and not res.get("ga_gear"):
            res["ga_gear"] = True
            ev("GEAR_UP")
        if res.get("ga_gear") and ias >= 180 and not res.get("ga_flaps"):
            res["ga_flaps"] = t
            ev("FLAPS_1")
        if res.get("ga_flaps") and ((t - res["ga_flaps"] > 30 and ias >= 260) or ias >= 340) and not res.get("ga_clean"):
            res["ga_clean"] = True
            ev("FLAPS_UP")
        if res.get("ga_clean") and g("TRAILING_EDGE_FLAPS_LEFT_ANGLE") * DEG < 1:
            break
    # hand flying (landing_test.py fly(); heading hold instead of the localizer)
    err_fps = (res["vs_f"] - vs_tgt) / 60.0
    res["integ"] = clamp(res["integ"] + err_fps * dt, -200.0, 200.0)
    ev("AXIS_ELEVATOR_SET", int(clamp(KP_VS * err_fps + KI_VS * res["integ"] + KQ * q, -12000, 6000)))
    bank_tgt = -clamp(2.0 * wrap(HDG - hdg), -15, 15)
    e_b = bank - bank_tgt
    res["integ_b"] = clamp(res["integ_b"] + e_b * dt, -30.0, 30.0)
    ev("AXIS_AILERONS_SET", int(clamp(-(KP_B * e_b + KD_B * p + KI_B * res["integ_b"]), -4000, 4000)))
    rows.append([round(el, 2), phase, round(alt), round(ias, 1), round(vs), round(vs_tgt), round(bank, 1), round(theta, 1),
                 round(g("INCIDENCE_ALPHA") * DEG, 2), round(g("TURB_ENG_N1:1"), 1), round(g("TURB_ENG_JET_THRUST:1")),
                 round(g("ENG_FUEL_FLOW_PPH:1")), round(g("TOTAL_WEIGHT"))])
    time.sleep(0.05)

for n in ("AXIS_ELEVATOR_SET", "AXIS_AILERONS_SET"):
    ev(n, 0)
ap_master(True)
ev("HEADING_BUG_SET", int(round(g("PLANE_HEADING_DEGREES_MAGNETIC") * DEG)) % 360)
ev("AP_HDG_HOLD_ON")
clean = g("AIRSPEED_INDICATED") >= 260
if clean:
    ev("GEAR_UP")
    ev("FLAPS_UP")
ev("THROTTLE1_SET", 9000 if clean else 11141)
ev("AP_ALT_VAR_SET_ENGLISH", int(g("PLANE_ALTITUDE") + 500))
ev("AP_ALT_HOLD_ON")
sm.exit()
log.terminate()
with open(out, "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["t", "phase", "alt", "ias", "vs_fpm", "vs_tgt", "bank", "pitch", "alpha", "n1", "thrust_lbf", "ff_pph", "weight"])
    wr.writerows(rows)

# evaluation: steady part of the test phase
test = [r for r in rows if r[1] == "test"]
steady = [r for r in test if r[0] > 25] if mode == "climb" else [r for r in test if r[0] > test[-1][0] - 30]
if len(steady) > 5:
    t_a, t_b = steady[0][0], steady[-1][0]
    roc = (steady[-1][2] - steady[0][2]) / max(t_b - t_a, 1) * 60      # from altitude, not from the noisy VS samples
    mean = lambda i: sum(r[i] for r in steady) / len(steady)
    print(f"steady {t_a:.0f}-{t_b:.0f} s: rate of climb {roc:.0f} ft/min, IAS {mean(3):.1f} KIAS, alt {mean(2):.0f} ft, "
          f"α {mean(8):.2f}°, pitch {mean(7):.1f}°, N1 {mean(9):.1f} %, net thrust {mean(10):.0f} lbf, FF {mean(11):.0f} lb/h, "
          f"weight {mean(12):.0f} lb")
else:
    print("not enough steady data")
print(f"{len(rows)} samples -> {out}")
