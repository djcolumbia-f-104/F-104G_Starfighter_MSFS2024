"""D5 cruise fuel flow (docs/notes/test-cards/D5-fuel-flow.md): stabilised level cruise at part power vs. FM Fig. A6-1.

Usage (with the Python of the simconnect-mcp venv; jet airborne near the point, e.g. after MCP `position`):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\cruise_test.py <output.csv> <alt_ft> <mach> <fm_nmpp_delta> <wd_ref> [slope=-0.8] [avg_s=60]
  fm_nmpp_delta: chart value (NM per 1 000 lb x δ) read at W/δ = wd_ref; slope: change per 1 000 lb of W/δ.
Sequence: clean, AP ALT hold at alt_ft + HDG hold; throttle PI (idle .. Military, no AB) holds the Mach; steady state
(|dM| < 0.005, |VS| < 150 ft/min for 20 s), then averages avg_s. simlog (3 Hz) runs throughout.
Abort: not steady after 240 s, altitude error > 500 ft, IAS < 250 KIAS, AP off.
"""
import math
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out, alt_t, mach_t, fm_val, wd_ref = sys.argv[1], *(float(a) for a in sys.argv[2:6])
slope = float(sys.argv[6]) if len(sys.argv) > 6 else -0.8
avg_s = float(sys.argv[7]) if len(sys.argv) > 7 else 60.0
DEG = 57.29578
MIL = 11141                                          # throttle position for Military (AB lights above ~100 % lever)
KP, KI = 60000.0, 2500.0                             # throttle units per Mach error / per Mach error x s

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 1500:
    sm.exit()
    sys.exit("ABORT: on the ground or fuel < 1 500 lb")
for _ in range(3):                                   # AP_MASTER is a toggle: read, toggle, verify
    if g("AUTOPILOT_MASTER") == 1:
        break
    ev("AP_MASTER")
    time.sleep(0.5)
ev("GEAR_UP")
ev("FLAPS_UP")
ev("SPOILERS_OFF")
ev("HEADING_BUG_SET", int(round(g("PLANE_HEADING_DEGREES_MAGNETIC") * DEG)) % 360)
ev("AP_HDG_HOLD_ON")
ev("AP_ALT_VAR_SET_ENGLISH", int(alt_t))
ev("AP_ALT_HOLD_ON")
log = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "simlog.py"), out, "420", "3"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
t0 = time.time()
print(f"start: {g('PLANE_ALTITUDE'):.0f} ft, M {g('AIRSPEED_MACH'):.3f}, {g('AIRSPEED_INDICATED'):.0f} KIAS, "
      f"OAT {g('AMBIENT_TEMPERATURE'):.1f} °C, weight {g('TOTAL_WEIGHT'):.0f} lb; target {alt_t:.0f} ft M {mach_t}")
th, integ, steady_since, samples, reason = 7000.0, 0.0, None, [], None
t_prev = time.time()
while True:
    now = time.time()
    dt, t_prev = now - t_prev, now
    m, alt, ias = g("AIRSPEED_MACH"), g("PLANE_ALTITUDE"), g("AIRSPEED_INDICATED")
    vs = g("VERTICAL_SPEED")                        # Python-SimConnect returns ft/min here (2026-10-29)
    if m == 0 or alt == 0 or ias == 0:              # failed read returns 0 -> skip the cycle
        time.sleep(0.5)
        continue
    err = mach_t - m
    if 0 < th < MIL or err * (th - MIL / 2) < 0:     # anti-windup at the throttle limits
        integ += err * dt
    th = min(MIL, max(0.0, 7000.0 + KP * err + KI * integ))
    ev("THROTTLE1_SET", int(th))
    if g("AUTOPILOT_MASTER") != 1:
        reason = "AP off"
    elif abs(alt - alt_t) > 500:
        reason = f"altitude {alt:.0f} ft"
    elif ias < 250:
        reason = f"IAS {ias:.0f} KIAS"
    if reason:
        break
    if abs(err) < 0.005 and abs(vs) < 150:
        steady_since = steady_since or now
    elif not samples:
        steady_since = None
    if steady_since and now - steady_since >= 20:
        samples.append((m, alt, g("AIRSPEED_TRUE"), ias, g("ENG_FUEL_FLOW_PPH:1"), g("TURB_ENG_JET_THRUST:1"),
                        g("TURB_ENG_N1:1"), g("TOTAL_WEIGHT"), g("AMBIENT_PRESSURE"), g("AMBIENT_TEMPERATURE"), th))
        if now - steady_since >= 20 + avg_s:
            break
    elif now - t0 > 240:
        reason = f"not steady after 240 s (M {m:.3f}, VS {vs:.0f})"
        break
    time.sleep(max(0.0, 1.0 - (time.time() - now)))
t_end = time.time() - t0
time.sleep(3)
log.terminate()
sm.exit()
if reason:
    sys.exit(f"ABORT at t {t_end:.0f} s: {reason}")

n = len(samples)
mean = [sum(s[i] for s in samples) / n for i in range(len(samples[0]))]
m, alt, tas, ias, ff, fn, n1, w, p_inhg, oat, th = mean
delta = p_inhg / 29.921
wd = w / delta
nmpp_delta = fm_val + slope * (wd - wd_ref) / 1000.0
ff_fm = tas / (nmpp_delta / delta) * 1000.0
ff_sd = math.sqrt(sum((s[4] - ff) ** 2 for s in samples) / n)
print(f"steady {n} samples, t {t_end - avg_s:.0f}-{t_end:.0f} s: {alt:.0f} ft, M {m:.3f}, {tas:.0f} KTAS, "
      f"{ias:.0f} KIAS, OAT {oat:.1f} °C, weight {w:.0f} lb, δ {delta:.4f}, W/δ {wd:.0f}")
print(f"  N1 {n1:.1f} %, throttle {th / 16383 * 100:.0f} %, net thrust {fn:.0f} lbf, gross (FF/TSFC 0.72) "
      f"{ff / 0.72:.0f} lbf, FF {ff:.0f} ± {ff_sd:.0f} lb/h")
print(f"  FM Fig. A6-1 (DI 0): NMPP x δ {nmpp_delta:.1f} -> {nmpp_delta / delta:.0f} NM per 1 000 lb -> "
      f"FF {ff_fm:.0f} lb/h; sim/FM {ff / ff_fm:.2f}; sim NM per 1 000 lb {tas / ff * 1000:.0f}")
print(f"log {out}")
