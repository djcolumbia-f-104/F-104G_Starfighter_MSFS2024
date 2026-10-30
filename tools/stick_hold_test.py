"""Build-up for the stick-schedule rotation (takeoff_test.py option `srot`, 2026-10-31): fixed elevator in the takeoff
configuration IN THE AIR -> equilibrium α for that stick position (static stability: independent of speed).

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE - never position from the ground):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\stick_hold_test.py <output.csv> [stick=-6400] [ias=185] [alt=15000]
Sequence: set_pos at alt / ias, gear DOWN, flaps TAKEOFF, trim 5° (AP off, SimVar), elevator PI holds the altitude for 15 s
(settle), then the elevator ramps to `stick` over 1.2 s (the rotation ramp) and is HELD for 8 s while a throttle PI holds
the IAS -> α / pitch / pitch rate logged (≈ 5 Hz). Prediction (card T3-D rotation): stick -6 400 at trim 5° -> α ≈ 10.5 ± 1°.
End: elevator 0, Military, gear up, AP on with ALT hold + HDG (TAKEOFF flaps may stay: limit 370 KIAS).
Abort (-> end): pitch > 25° or < -10°, |bank| > 30°, IAS < 150.
"""
import csv
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
STICK = float(sys.argv[2]) if len(sys.argv) > 2 else -6400.0
IAS0 = float(sys.argv[3]) if len(sys.argv) > 3 else 185.0
ALT0 = float(sys.argv[4]) if len(sys.argv) > 4 else 15000.0
DEG = 57.29578
HDG = 263.4
LAT, LON = 48.36, 12.10                          # config_test.py: east of EDDM, flat terrain ≈ 1 400 ft
TRIM_DEG = 5.0                                   # FM takeoff trim

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
    sys.exit("ABORT: on the ground or fuel < 2 000 lb - take off / refuel first")
for _ in range(3):
    if g("AUTOPILOT_MASTER") != 1:
        break
    ev("AP_MASTER")
    time.sleep(0.3)
sm.set_pos(ALT0, LAT, LON, int(IAS0), -6.0, 0.0, HDG, 0)
time.sleep(1.0)
ev("GEAR_DOWN")
ev("FLAPS_1")
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", TRIM_DEG / DEG)
    time.sleep(0.2)
    if abs(g("ELEVATOR_TRIM_POSITION") * DEG - TRIM_DEG) < 0.3:
        break
ev("THROTTLE1_SET", 11141)
print(f"weight {g('TOTAL_WEIGHT'):.0f} lb, trim {g('ELEVATOR_TRIM_POSITION') * DEG:.1f}°, IAS {g('AIRSPEED_INDICATED'):.0f}, "
      f"stick {STICK:.0f} after the settle phase")

rows, phase, reason = [], "settle", "done"
st = {"integ": 0.0, "th": 11141.0}
t0 = prev_t = time.time()
prev_alt, prev_th = g("PLANE_ALTITUDE"), -g("PLANE_PITCH_DEGREES") * DEG
t_hold = None
while time.time() - t0 < 60:
    t = time.time()
    dt = max(t - prev_t, 0.05)
    prev_t = t
    alt, ias = g("PLANE_ALTITUDE") or prev_alt, g("AIRSPEED_INDICATED")
    theta, bank, alpha = -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG, g("INCIDENCE_ALPHA") * DEG
    q = (theta - prev_th) / dt
    vs = (alt - prev_alt) / dt * 60
    prev_alt, prev_th = alt, theta
    el = t - t0
    if phase == "settle":
        # elevator PI on the altitude (landing_test.py gains, simplified)
        err = (vs - 4.0 * (ALT0 - alt)) / 60.0
        st["integ"] = clamp(st["integ"] + err * dt, -200, 200)
        # pull limit -8 000 (2026-10-31 hold185: set_pos left 154 KIAS, the loop pulled -12 000 into the kicker)
        cmd = clamp(300.0 * err + 10.0 * st["integ"] + 150.0 * q, -8000, 6000)
        if (el > 15 and abs(ias - IAS0) < 5) or el > 45:
            phase, t_hold, cmd0 = "ramp", t, cmd
    if phase in ("ramp", "hold"):
        frac = clamp((t - t_hold) / 1.2, 0.0, 1.0)
        cmd = cmd0 + (STICK - cmd0) * frac
        if frac >= 1.0:
            phase = "hold"
        if t - t_hold > 9.2:
            break
    # throttle PI on the IAS (Military .. Maximum would change the trim by thrust line - keep ≤ Military)
    st["th"] = clamp(st["th"] + 400.0 * (IAS0 - ias) * dt, 0.0, 16383.0 if phase == "settle" else 11141.0)
    ev("THROTTLE1_SET", int(st["th"]))
    ev("AXIS_ELEVATOR_SET", int(cmd))
    ev("AXIS_AILERONS_SET", int(clamp(-(250.0 * bank), -4000, 4000)))
    if not -10 < theta < 25 or abs(bank) > 30 or ias < 150:
        reason = f"ABORT: pitch {theta:.0f}°, bank {bank:.0f}°, IAS {ias:.0f}"
        break
    rows.append([round(el, 2), phase, round(alt), round(ias, 1), round(vs), round(theta, 2), round(q, 2), round(alpha, 2),
                 int(cmd), round(g("ELEVATOR_POSITION"), 3)])
    time.sleep(0.03)

ev("AXIS_ELEVATOR_SET", 0)
ev("AXIS_AILERONS_SET", 0)
ev("THROTTLE1_SET", 11141)
ev("GEAR_UP")
ev("AP_MASTER")
time.sleep(0.3)
if g("AUTOPILOT_MASTER") != 1:
    ev("AP_MASTER")
ev("HEADING_BUG_SET", int(round(g("PLANE_HEADING_DEGREES_MAGNETIC") * DEG)) % 360)
ev("AP_HDG_HOLD_ON")
ev("AP_ALT_VAR_SET_ENGLISH", int(g("PLANE_ALTITUDE")))
ev("AP_ALT_HOLD_ON")
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "phase", "alt", "ias", "vs_fpm", "pitch", "q_dps", "alpha", "el_cmd", "elev_pos"])
    w.writerows(rows)
print(reason)
hold = [r for r in rows if r[1] == "hold"]
ramp = [r for r in rows if r[1] in ("ramp", "hold")]
if ramp:
    pk = max(ramp, key=lambda r: r[7])
    print(f"peak α {pk[7]:.1f}° at {pk[0] - ramp[0][0]:.1f} s after the ramp start, max pitch rate {max(r[6] for r in ramp):.1f}°/s")
late = [r for r in hold if r[0] - ramp[0][0] > 4]
if late:
    m = lambda i: sum(r[i] for r in late) / len(late)
    print(f"equilibrium (last {late[-1][0] - late[0][0]:.1f} s of the hold): α {m(7):.2f}°, IAS {m(3):.0f}, pitch {m(5):.1f}°, "
          f"elevator position {m(9):.3f} at stick {STICK:.0f}")
print(f"{len(rows)} samples -> {out}")
