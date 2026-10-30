"""Tests B5/B6 (docs/test-plan.md): landing configuration at Military - go-around climb at constant IAS (sawtooth climb,
FM Fig. 6-8) or level flight with speed brakes (flat final, FM 3-41). Test card:
docs/notes/test-cards/B5-B6-landing-config.md.

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\config_test.py <output.csv> <alt_ft MSL> climb|level|glide [ias=170] [sb|clean]
  glide: B4 (FM 3-38, Fig. 3-8) idle, gear up, TAKEOFF flaps at 245 KIAS (or "clean": flaps up, 275 KIAS), speed hold by
         elevator, down to alt - 9 000 ft -> glide ratio (energy) and aerodynamic L/D in NM per 10 000 ft
  climb: elevator holds IAS (default 170 KIAS) at Military -> mean rate of climb over the steady part (after 25 s)
  level: elevator holds the start altitude at Military -> IAS it settles at (mean of the last 30 s)
  slow:  B7 (FM Fig. 6-4) `slow <ias_start> clean|to|land <ias_stop> [alpha_stop=16]`: level 1 kt/s deceleration
         (throttle loop, ≤ Military), elevator holds the altitude; α/CL per 5 kt band; recovery: Maximum, descend to
         ias_stop + 40, then clean-up
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
GLIDE = mode == "glide"
CLEAN = "clean" in sys.argv[4:]
SLOW = mode == "slow"
if SLOW:
    # B7 (FM Fig. 6-4): level 1 kt/s deceleration (throttle loop, no AB) in clean / to / land configuration until
    # ias_stop or alpha_stop, then recovery (Maximum, descend until ias_stop + 40) and FM clean-up
    ias_tgt, CFG, IAS_STOP = float(sys.argv[4]), sys.argv[5], float(sys.argv[6])
    ALPHA_STOP = float(sys.argv[7]) if len(sys.argv) > 7 else 16.0
    TRIM_DEG = {"clean": 8.0, "to": 7.0, "land": 5.2}[CFG]          # [S] elevator does the rest (T3-G: tail ≈ 1.08 α)
if GLIDE:
    # B4 (FM 3-38/Fig. 3-8): idle, gear up, TAKEOFF flaps 245 KIAS (or flaps up 275 KIAS: "clean")
    ias_tgt = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] not in ("sb", "clean") else (275.0 if CLEAN else 245.0)
    TRIM_DEG = 3.0                                    # [S] CL ≈ 0.48 at 245 KIAS -> α ≈ 3° (T3-G: tail ≈ 1.08 α)
ap_master(False)
ev("SPOILERS_OFF")
# speed ≈ IAS, pitch negative = nose up (landing_test.py); glide: nose ≈ 5° down (L/D ≈ 6-7 -> γ ≈ -8.5°, α ≈ 3°)
sm.set_pos(alt0, LAT, LON, int(ias_tgt) if GLIDE or SLOW else 185, 5.0 if GLIDE else -3.0, 0.0, HDG, 0)
time.sleep(1.0)
if SLOW:
    ev("GEAR_DOWN" if CFG == "land" else "GEAR_UP")
    ev({"clean": "FLAPS_UP", "to": "FLAPS_1", "land": "FLAPS_DOWN"}[CFG])
elif GLIDE:
    ev("GEAR_UP")
    ev("FLAPS_UP" if CLEAN else "FLAPS_1")
else:
    ev("GEAR_DOWN")
    ev("FLAPS_DOWN")
ap_master(False)
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", TRIM_DEG / DEG)
    time.sleep(0.2)
    if abs(g("ELEVATOR_TRIM_POSITION") * DEG - TRIM_DEG) < 0.3:
        break
if SB:
    ev("SPOILERS_ON")
# 2026-10-30: set_pos does not reliably take the speed (after a fast flight B6 started at 223 instead of 185 KIAS -> +4 000
# ft/min command, pitch 23° abort) -> climb/level: idle pre-phase holding alt0 until IAS ≤ target + 5, then Military
PRE = mode in ("climb", "level") and (g("AIRSPEED_INDICATED") or 0) > ias_tgt + 10
ev("THROTTLE1_SET", 0 if GLIDE or PRE else 7000 if SLOW else 11141)   # glide: idle; slow: decel loop start; else Military
w = g("TOTAL_WEIGHT")
print(f"{mode} at {alt0:.0f} ft MSL, {'speed brakes OUT, ' if SB else ''}weight {w:.0f} lb, OAT {g('AMBIENT_TEMPERATURE'):.1f} °C, "
      f"trim {g('ELEVATOR_TRIM_POSITION') * DEG:.1f}°" + (f", IAS target {ias_tgt:.0f}" if mode == "climb" else ""))
log = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "simlog.py"),
                        out.replace(".csv", "_simlog.csv"), "300", "3"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

res = {"integ": 0.0, "integ_b": 0.0}
rows, phase, reason = [], "pre" if PRE else "test", ""
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

    if phase == "pre":
        vs_tgt = clamp(4.0 * (alt0 - alt), -1000.0, 1000.0)
        # level mode: end the pre-phase high (200 KIAS) - ending at the 170 target at idle let the speed decay to 150 while
        # the engine spooled up, onto the back side of the drag curve (B5 2026-10-31 run h5b aborted)
        if ias <= (200.0 if mode == "level" else ias_tgt + 5) or el > 120:
            phase = "test"
            ev("THROTTLE1_SET", 11141)
            print(f"pre-phase done after {el:.0f} s at {ias:.0f} KIAS")
            t0 = t                                                   # test time counts from here
    elif phase == "test":
        if mode == "climb":
            vs_tgt = clamp(150.0 * (ias - ias_tgt), -1500.0, 4000.0)   # faster than the target -> climb steeper
        elif GLIDE:
            # speed hold by elevator: integrate the descent-rate command from the speed error (faster -> sink less)
            # (glide run 1: started at -3 500 / -6 200 ft/min target while level -> full push, α < 0, pitch -21° abort ->
            # start at the current VS, slower integrator)
            res["vs_cmd"] = clamp(res.get("vs_cmd", res["vs_f"]) + 15.0 * (ias - ias_tgt) * dt, -9000.0, 0.0)
            vs_tgt = clamp(res["vs_cmd"] + 40.0 * (ias - ias_tgt), -9000.0, 500.0)
        else:
            vs_tgt = clamp(4.0 * (alt0 - alt), -1000.0, 1000.0)
        if SLOW:
            # throttle loop on the deceleration (target -1 kt/s; more throttle if decelerating faster), capped at Military
            res["ias_dot"] = 0.8 * res.get("ias_dot", 0.0) + 0.2 * (ias - res.get("prev_ias", ias)) / dt
            res["prev_ias"] = ias
            if el > 8:
                res["th"] = clamp(res.get("th", 7000.0) + 1500.0 * (-1.0 - res["ias_dot"]) * dt, 0.0, 11141.0)
                ev("THROTTLE1_SET", int(res["th"]))
            alpha = g("INCIDENCE_ALPHA") * DEG
            bad = abs(bank) > 30 or not -10 < theta < 25 or agl < 3000 or res["vs_f"] < -2000
            done = ias < IAS_STOP or alpha > ALPHA_STOP or el > 240
        else:
            bad = ias < 150 or abs(bank) > 30 or not (-20 if GLIDE else -10) < theta < 20 or agl < (3000 if GLIDE else 1500)
            # level: 180 s (2026-10-31 B5: after the idle pre-phase the jet started ≈ 35 ft low and was still accelerating
            # at 120 s - 177.5 KIAS rising vs. 182.8 steady on 2026-10-29)
            done = (el > 200 or alt < alt0 - 9000) if GLIDE else (el > (180 if mode == "level" else 120)
                                                                   or (mode == "climb" and alt > alt0 + 3000 and el > 40))
        if bad or done:
            reason = (f"ABORT: IAS {ias:.0f}, bank {bank:.0f}°, pitch {theta:.0f}°, AGL {agl:.0f}, VS {res['vs_f']:.0f}" if bad
                      else f"test done at {ias:.0f} KIAS, α {g('INCIDENCE_ALPHA') * DEG:.1f}°, {el:.0f} s")
            print(reason)
            phase = "recovery" if SLOW else "clean-up"
            ev("SPOILERS_OFF")
            ev("THROTTLE1_SET", 16383)
    elif phase == "recovery":
        # B7: unload and descend with Maximum until IAS_STOP + 40, then the FM clean-up (flaps only if extended)
        vs_tgt = clamp(-60.0 * (IAS_STOP + 40.0 - ias), -2000.0, 0.0)
        if ias >= IAS_STOP + 40:
            if CFG == "clean":
                break
            phase = "clean-up"
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
    # gains tuned at ~185 KIAS; scale with 1/q (glide run 1: pitch oscillation 0..15° at 250-380 KIAS)
    ks = clamp((185.0 / max(ias, 100.0)) ** 2, 0.25, 1.5)
    # B7 run 2 (2026-10-30): -12 000 = 12.45° elevator limited α to 16.3° -> full nose-up authority (17°) in the slow test
    ev("AXIS_ELEVATOR_SET", int(clamp(ks * (KP_VS * err_fps + KI_VS * res["integ"] + KQ * q), -16383 if SLOW else -12000, 6000)))
    bank_tgt = -clamp(2.0 * wrap(HDG - hdg), -15, 15)
    e_b = bank - bank_tgt
    res["integ_b"] = clamp(res["integ_b"] + e_b * dt, -30.0, 30.0)
    ev("AXIS_AILERONS_SET", int(clamp(-(KP_B * e_b + KD_B * p + KI_B * res["integ_b"]), -4000, 4000)))
    rows.append([round(el, 2), phase, round(alt), round(ias, 1), round(vs), round(vs_tgt), round(bank, 1), round(theta, 1),
                 round(g("INCIDENCE_ALPHA") * DEG, 2), round(g("TURB_ENG_N1:1"), 1), round(g("TURB_ENG_JET_THRUST:1")),
                 round(g("ENG_FUEL_FLOW_PPH:1")), round(g("TOTAL_WEIGHT")), round(g("AIRSPEED_TRUE"), 1),
                 round(g("GROUND_VELOCITY"), 1)])
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
    wr.writerow(["t", "phase", "alt", "ias", "vs_fpm", "vs_tgt", "bank", "pitch", "alpha", "n1", "thrust_lbf", "ff_pph", "weight",
                 "tas", "gs"])
    wr.writerows(rows)

# evaluation: steady part of the test phase
test = [r for r in rows if r[1] == "test"]
if GLIDE:
    st = [r for r in test if r[0] > 30]
    if len(st) > 10:
        dist = sum((st[i][14] * 1.68781) * (st[i][0] - st[i - 1][0]) for i in range(1, len(st)))   # ground speed, calm
        dh = st[0][2] - st[-1][2]
        v1, v2 = st[0][13] * 1.68781, st[-1][13] * 1.68781
        dh_e = dh + (v1 ** 2 - v2 ** 2) / (2 * 32.174)              # energy height loss (TAS change)
        w_m = sum(r[12] for r in st) / len(st)
        t_m = sum(r[10] for r in st) / len(st)                       # idle net thrust (windmilling would be ≈ 0..-)
        d_m = t_m + w_m * dh_e / dist                                # mean aerodynamic drag from the energy balance
        print(f"GLIDE {st[0][0]:.0f}-{st[-1][0]:.0f} s: {st[0][2]:.0f} -> {st[-1][2]:.0f} ft, IAS {sum(r[3] for r in st) / len(st):.0f} KIAS, "
              f"α {sum(r[8] for r in st) / len(st):.2f}°, idle net thrust {t_m:.0f} lbf")
        print(f"  glide ratio (energy) {dist / dh_e:.2f} = {dist / dh_e * 10000 / 6076.12:.1f} NM per 10 000 ft; "
              f"aerodynamic L/D (thrust removed) {w_m / d_m:.2f} = {w_m / d_m * 10000 / 6076.12:.1f} NM per 10 000 ft")
        print("  FM Fig. 3-8 (TAKEOFF flaps 245 KIAS / flaps up 275, gear up, windmilling, RAT out): 9 NM per 10 000 ft; "
              "without RAT ≈ +2 NM -> ≈ 11")
if SLOW:
    # B7: α and CL per 5 kt IAS band (q from IAS ≈ EAS at ≤ 10 000 ft; level flight, 1 g)
    print(f"SLOW {CFG}: IAS band, n, α, CL = W/(qS), pitch, VS, N1")
    for b in range(int(max(r[3] for r in test)) // 5 * 5, int(min(r[3] for r in test)) - 5, -5):
        s = [r for r in test if b <= r[3] < b + 5 and r[0] > 8]
        if s:
            m = lambda i: sum(r[i] for r in s) / len(s)
            qd = 0.5 * 0.0023769 * (m(3) * 1.68781) ** 2
            print(f"  {b:3d}-{b + 5:3d} KIAS n {len(s):2d}  α {m(8):5.2f}°  CL {m(12) / (qd * 196.1):.3f}  pitch {m(7):5.1f}°  "
                  f"VS {m(4):5.0f}  N1 {m(9):5.1f} %")
steady = [] if GLIDE or SLOW or not test else (
    [r for r in test if r[0] > 25] if mode == "climb" else [r for r in test if r[0] > test[-1][0] - 30])
if GLIDE or SLOW:
    pass
elif len(steady) > 5:
    t_a, t_b = steady[0][0], steady[-1][0]
    roc = (steady[-1][2] - steady[0][2]) / max(t_b - t_a, 1) * 60      # from altitude, not from the noisy VS samples
    mean = lambda i: sum(r[i] for r in steady) / len(steady)
    print(f"steady {t_a:.0f}-{t_b:.0f} s: rate of climb {roc:.0f} ft/min, IAS {mean(3):.1f} KIAS, alt {mean(2):.0f} ft, "
          f"α {mean(8):.2f}°, pitch {mean(7):.1f}°, N1 {mean(9):.1f} %, net thrust {mean(10):.0f} lbf, FF {mean(11):.0f} lb/h, "
          f"weight {mean(12):.0f} lb")
else:
    print("not enough steady data")
print(f"{len(rows)} samples -> {out}")
