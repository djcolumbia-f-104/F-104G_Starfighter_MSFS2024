"""D7 maximum thrust climb at the FM schedule M 0.90 (FM Fig. A3-7, PDF 480): time from 10 000 to 35 000 ft.

Usage (with the Python of the simconnect-mcp venv; the jet must be AIRBORNE - never position from the ground):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\climb_test.py <output.csv> [mach=0.90] [alt_stop=37000] [mil]
  mil: Military thrust climb (FM Fig. A3-10, schedule M 0.85) instead of maximum thrust
Sequence: set_pos at 9 000 ft MSL (≈ 7 600 ft AGL east of EDDM) at ≈ M 0.9, gear/flaps up, AP off, full AB; elevator
holds the Mach through an integrated vertical-speed command (faster -> climb steeper; same structure as the glide mode of
config_test.py), ailerons hold the heading; from 33 000 ft the climb is rounded off (VS ≤ 6 x altitude to go),
Military at 35 000 ft, end at alt_stop or VS < 2 000 ft/min -> AP ALT hold. simlog (3 Hz) runs throughout.
Evaluation: crossing times of 10 000 ... 35 000 ft and the mean Mach -> compare with FM Fig. A3-7 (standard day).
Abort: pitch > 70°, |bank| > 45°, IAS < 250 KIAS, AGL < 3 000 ft.
"""
import csv
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
mach_tgt = float(sys.argv[2]) if len(sys.argv) > 2 else 0.90
alt_stop = float(sys.argv[3]) if len(sys.argv) > 3 else 37000.0
MIL = "mil" in sys.argv[4:]
THROTTLE = 11141 if MIL else 16383
RUN_S = 480 if MIL else 200
DEG = 57.29578
HDG = 263.4                                     # EDDM 26L direction (true), as config_test.py
LAT, LON = 48.36, 12.10
KP_VS, KI_VS, KQ = 300.0, 10.0, 150.0           # landing_test.py / config_test.py
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


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 2500:
    sm.exit()
    sys.exit("ABORT: on the ground (never position from the ground) or fuel < 2 500 lb")
ap_master(False)
ev("SPOILERS_OFF")
# speed ≈ IAS (520 gave M ≈ 0.91-0.95 at 9 000 ft), pitch negative = nose up
sm.set_pos(9000, LAT, LON, int(500 * mach_tgt / 0.90), -2.0, 0.0, HDG, 0)
# 2026-10-30: right after set_pos the sim reports transient attitudes (pitch 71-72° within 1.5 s -> false aborts; the
# runway respawn showed pitch 23° / bank -42°) -> wait until pitch and bank are plausible before controlling
t_w = time.time()
while time.time() - t_w < 8:
    time.sleep(0.5)
    if abs(g("PLANE_PITCH_DEGREES") * DEG) < 15 and abs(g("PLANE_BANK_DEGREES") * DEG) < 10:
        break
ev("GEAR_UP")
ev("FLAPS_UP")
ap_master(False)
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", 2.0 / DEG)
    time.sleep(0.2)
# 2026-10-30: set_pos does not reliably take the speed (after a high-altitude flight the jet appeared at M 1.27 /
# 735 KIAS at 9 000 ft -> pitch 72° abort) -> pre-phase: idle, hold ≈ 9 000 ft until the Mach is on the schedule
pre = (g("AIRSPEED_MACH") or 0) > mach_tgt + 0.02
ev("THROTTLE1_SET", 0 if pre else THROTTLE)
w0 = g("TOTAL_WEIGHT")
print(f"climb M {mach_tgt} from {g('PLANE_ALTITUDE'):.0f} ft, weight {w0:.0f} lb, OAT {g('AMBIENT_TEMPERATURE'):.1f} °C")
log = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "simlog.py"),
                        out.replace(".csv", "_simlog.csv"), str(RUN_S + 40), "3"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

res = {"integ": 0.0, "integ_b": 0.0, "vs_cmd": 0.0}
rows, reason, mil = [], "time", False
t0 = prev_t = time.time()
while time.time() - t0 < RUN_S:
    t = time.time()
    dt = max(t - prev_t, 0.05)
    prev_t = t
    alt, m, ias, agl = g("PLANE_ALTITUDE"), g("AIRSPEED_MACH"), g("AIRSPEED_INDICATED"), g("PLANE_ALT_ABOVE_GROUND")
    if alt == 0 or m == 0:                                        # failed read
        time.sleep(0.05)
        continue
    bank, theta = g("PLANE_BANK_DEGREES") * DEG, -g("PLANE_PITCH_DEGREES") * DEG
    hdg = g("PLANE_HEADING_DEGREES_TRUE") * DEG
    vs = (alt - res.get("prev_alt", alt)) / dt * 60
    res["prev_alt"] = alt
    res["vs_f"] = 0.5 * res.get("vs_f", vs) + 0.5 * vs
    q = (theta - res.get("prev_theta", theta)) / dt
    p = (bank - res.get("prev_bank", bank)) / dt
    res["prev_theta"], res["prev_bank"] = theta, bank
    el = t - t0
    # Mach hold by elevator: faster than the schedule -> climb steeper (integrated VS command + proportional part)
    err_m = m - mach_tgt
    if pre:
        if m <= mach_tgt + 0.01 or el > 90:
            pre = False
            ev("THROTTLE1_SET", THROTTLE)
            print(f"pre-phase done after {el:.0f} s at M {m:.3f}, {alt:.0f} ft")
        err_m = 0.0
    # [S] gains: the AB accelerates ≈ 0.02 M/s at 9 000 ft and the schedule needs 20 000-30 000 ft/min -> the VS command
    # must build up within ≈ 10 s (ft/min per Mach per s, ft/min per Mach)
    res["vs_cmd"] = clamp(res["vs_cmd"] + 60000.0 * err_m * dt, 0.0, 60000.0)
    # proportional part limited (2026-10-30 military run 1: start at M ≈ 1.1 -> +37 000 ft/min command -> pitch 71°)
    vs_tgt = clamp(res["vs_cmd"] + clamp(150000.0 * err_m, -8000.0, 8000.0), -2000.0, 60000.0)
    if theta > 55:
        vs_tgt = min(vs_tgt, res["vs_f"] - 2000.0)
    if pre:
        vs_tgt = clamp(3.0 * (9000.0 - alt), -1500.0, 1500.0)
    if alt > 33000:                                               # round off the climb
        vs_tgt = min(vs_tgt, 6.0 * (alt_stop + 1000 - alt))
    if alt > 35000 and not mil:
        ev("THROTTLE1_SET", 11141)
        mil = True
    if theta > 70 or abs(bank) > 45 or ias < 250 or (agl and agl < 3000):
        reason = f"ABORT: pitch {theta:.0f}°, bank {bank:.0f}°, IAS {ias:.0f}, AGL {agl:.0f}"
        break
    if alt > alt_stop or (alt > 35000 and res["vs_f"] < 2000):
        reason = "done"
        break
    err_fps = (res["vs_f"] - vs_tgt) / 60.0
    res["integ"] = clamp(res["integ"] + err_fps * dt, -200.0, 200.0)
    ks = clamp((185.0 / max(ias, 100.0)) ** 2, 0.25, 1.5)
    ev("AXIS_ELEVATOR_SET", int(clamp(ks * (KP_VS * err_fps + KI_VS * res["integ"] + KQ * q), -12000, 6000)))
    bank_tgt = -clamp(2.0 * wrap(HDG - hdg), -15, 15)
    e_b = bank - bank_tgt
    res["integ_b"] = clamp(res["integ_b"] + e_b * dt, -30.0, 30.0)
    ev("AXIS_AILERONS_SET", int(clamp(-(KP_B * e_b + KD_B * p + KI_B * res["integ_b"]), -8000, 8000)))
    rows.append([round(el, 2), round(alt), round(m, 3), round(ias, 1), round(res["vs_f"]), round(vs_tgt), round(theta, 1),
                 round(bank, 1), round(g("TURB_ENG_JET_THRUST:1")), round(g("ENG_FUEL_FLOW_PPH:1")), round(g("TOTAL_WEIGHT")),
                 round(g("AMBIENT_TEMPERATURE"), 1)])
    time.sleep(0.05)

for n in ("AXIS_ELEVATOR_SET", "AXIS_AILERONS_SET"):
    ev(n, 0)
ev("THROTTLE1_SET", 11141)
ap_master(True)
ev("HEADING_BUG_SET", int(round(g("PLANE_HEADING_DEGREES_MAGNETIC") * DEG)) % 360)
ev("AP_HDG_HOLD_ON")
ev("AP_ALT_VAR_SET_ENGLISH", int(g("PLANE_ALTITUDE")))
ev("AP_ALT_HOLD_ON")
sm.exit()
log.terminate()
print(reason)
with open(out, "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["t", "alt", "mach", "ias", "vs_fpm", "vs_tgt", "pitch", "bank", "thrust_lbf", "ff_pph", "weight", "oat_c"])
    wr.writerows(rows)

cross = {}
for a, b in zip(rows, rows[1:]):
    for h in range(10000, 40000, 5000):
        if a[1] < h <= b[1] and h not in cross:
            cross[h] = a[0] + (h - a[1]) / max(b[1] - a[1], 1) * (b[0] - a[0])
if 10000 in cross:
    for h in sorted(cross):
        seg = [r for r in rows if 10000 <= r[1] <= h]
        print(f"  {h:6d} ft at {cross[h] - cross[10000]:6.1f} s after 10 000 ft  ({(cross[h] - cross[10000]) / 60:.2f} min), "
              f"mean M {sum(r[2] for r in seg) / max(len(seg), 1):.3f}, pitch max {max((r[6] for r in seg), default=0):.0f}°")
print(f"{len(rows)} samples -> {out}")
