"""A3 ground steering identification (2026-11-06; card docs/notes/test-cards/A3-ground-steering.md) - input for F9.

Usage (simconnect-mcp venv Python; jet standing on EDDM 26L after `sim_actions.py runway`, engine at idle):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\taxi_steer_test.py <output.csv>
      [speeds=80,120] [steps=400,800]
Sequence: trim 2° (no nose lift), flaps as set, brakes off, Military; closed-loop centreline law (rudder PI on a heading that
steers back to the centreline, 0.1°/ft, + axis = nose left: the F9 rollout law with the correct sign) and wings level;
at each test speed the throttle PI holds the speed, 6 s settle, then for each step size: rudder +step (open loop) 1.5 s,
6 s closed loop, -step 1.5 s, 6 s closed loop. Fast loop (heading, bank, IAS, lat/lon every pass). After the last speed:
idle, brakes, centreline law to a stop.
Abort (-> idle, brakes, centreline law): |cross-track| > 40 ft, heading error > 6°, IAS > 130 KIAS, pitch > 2.5° (nose lift),
not on the ground for 3 reads, or along-track > 9 000 ft.
Output: per step the peak yaw rate (°/s), the heading change after 1.5 s, the lateral drift, and the closed-loop recovery
(overshoot, time to ±0.5°).
"""
import csv
import math
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
opts = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
SPEEDS = [float(v) for v in opts.get("speeds", "80,120").split(",")]
STEPS = [float(v) for v in opts.get("steps", "400,800").split(",")]
# law=pi: the F9 rollout PI (run 1, oscillated); law=new (default since run 2): desk design on the run-1 model fit
# (yaw rate ≈ 1.8°/s per 1 000 counts x IAS/100, lag 0.6 s, dead time 0.45 s): kp 700 / kd 300 (yaw-rate damping) x
# min(1, 100/IAS), ki 50 (weather-vaning), centreline 0.04°/ft
LAW = opts.get("law", "new")
DEG = 57.29578
LAT0, LON0, HDG = 48.34472097713059, 11.803858844132039, 263.4
FT_PER_DEG = 60 * 6076.12
h = math.radians(HDG)
U, R = (math.sin(h), math.cos(h)), (math.cos(h), -math.sin(h))
MIL = 11141

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


def track(lat, lon):
    n = (lat - LAT0) * FT_PER_DEG
    e = (lon - LON0) * FT_PER_DEG * math.cos(math.radians(LAT0))
    return e * U[0] + n * U[1], e * R[0] + n * R[1]


if g("SIM_ON_GROUND") != 1 or g("TURB_ENG_N1:1") < 60 or g("GROUND_VELOCITY") > 2:
    sm.exit()
    sys.exit("ABORT: not standing on the ground with the engine running")
if g("AUTOPILOT_MASTER") == 1:
    ev("AP_MASTER")
aq.set("ELEVATOR_TRIM_POSITION", 2.0 / DEG)
ev("SPOILERS_OFF")
ev("AXIS_ELEVATOR_SET", 0)
if g("BRAKE_PARKING_POSITION") == 1:
    ev("PARKING_BRAKES")
ev("THROTTLE1_SET", MIL)
print(f"A3 steering test: speeds {SPEEDS} KIAS, steps {STEPS} counts, weight {g('TOTAL_WEIGHT'):.0f} lb, trim 2°")

rows, steps_out, reason = [], [], "done"
st = {"i_rud": 0.0, "th_i": 6000.0, "air": 0}
plan = []                                   # (speed, kind, value, duration)
for v in SPEEDS:
    plan.append((v, "settle", 0, 6.0))
    for s in STEPS:
        plan += [(v, "step", +s, 1.5), (v, "hold", 0, 6.0), (v, "step", -s, 1.5), (v, "hold", 0, 6.0)]
plan.append((0, "stop", 0, 60.0))
k, seg_t, phase = 0, None, "accel"
t0 = prev_t = time.time()
prev_hdg = None
while True:
    t = time.time()
    dt = max(t - prev_t, 0.02)
    prev_t = t
    hdg = g("PLANE_HEADING_DEGREES_TRUE") * DEG % 360
    ias, bank = g("AIRSPEED_INDICATED"), g("PLANE_BANK_DEGREES") * DEG
    lat, lon = g("PLANE_LATITUDE"), g("PLANE_LONGITUDE")
    if abs(lat) < 1.6:
        lat, lon = lat * DEG, lon * DEG
    s_al, c = track(lat, lon)
    theta = -g("PLANE_PITCH_DEGREES") * DEG
    gnd = g("SIM_ON_GROUND") == 1
    r = wrap(hdg - prev_hdg) / dt if prev_hdg is not None else 0.0
    prev_hdg = hdg
    st["air"] = 0 if gnd else st["air"] + 1
    e_r = wrap((HDG - clamp(0.1 * c, -5.0, 5.0)) - hdg)
    # closed-loop centreline law (F9 rollout law, correct sign): + axis = nose left
    if LAW != "pi":
        e_r = wrap((HDG - clamp(0.04 * c, -5.0, 5.0)) - hdg)     # integrate the error of the law in use
    st["i_rud"] = clamp(st["i_rud"] + e_r * dt, -20.0, 20.0)
    if LAW == "pi":
        rud = clamp(-700 * e_r - 100 * st["i_rud"], -12000, 12000)
    else:
        ks = min(1.0, 100.0 / max(ias, 30.0))
        # r = d(hdg)/dt (+ = nose right); + counts = nose left -> damping adds + counts for + r
        rud = clamp(-ks * 700 * e_r + ks * 300 * r - 50 * st["i_rud"], -12000, 12000)
    v_tgt, kind, val, dur = plan[k] if phase != "accel" else (SPEEDS[0], "accel", 0, 0)
    if phase == "accel":
        if ias >= SPEEDS[0] - 3:
            phase, seg_t = "plan", t
    elif kind == "step":
        rud = val                                                    # open loop
        st["i_rud"] = st["i_rud"]                                    # integrator frozen during the step
    if phase == "plan" and kind != "stop":
        if seg_t is not None and t - seg_t >= dur:
            k += 1
            seg_t = t
            v_tgt, kind, val, dur = plan[k]
            if kind == "step":
                steps_out.append(dict(v=v_tgt, val=val, t=t - t0, rows0=len(rows)))
            if kind == "settle" and v_tgt != plan[k - 1][0]:
                seg_t = None                                         # wait for the new speed first
        if seg_t is None and ias >= v_tgt - 3:
            seg_t = t
    if kind == "stop" or reason != "done":
        ev("THROTTLE1_SET", 0)
        ev("AXIS_LEFT_BRAKE_SET", 16383)
        ev("AXIS_RIGHT_BRAKE_SET", 16383)
        if g("GROUND_VELOCITY") < 2:
            break
    else:
        tgt = v_tgt if phase == "plan" else SPEEDS[0] + 5
        st["th_i"] = clamp(st["th_i"] + 60.0 * (tgt - ias) * dt, 0.0, MIL)
        # run 1: the speed overshot to 110 KIAS (target 80) -> stronger PI, idle when 4 kt fast
        thr = 0 if ias > tgt + 4 else clamp(st["th_i"] + 600.0 * (tgt - ias), 0, MIL)
        ev("THROTTLE1_SET", int(thr))
    ev("AXIS_RUDDER_SET", int(rud))
    ev("AXIS_AILERONS_SET", int(clamp(-(250.0 * bank), -6000, 6000)))
    ev("AXIS_ELEVATOR_SET", 2000 if theta > 1.0 else 0)              # keep the nose wheel down
    rows.append([round(t - t0, 3), phase if phase != "plan" else kind, k, round(ias, 1), round(s_al), round(c, 1),
                 round(wrap(hdg - HDG), 2), round(r, 2), round(bank, 2), round(theta, 2), int(rud)])
    if reason == "done":
        bad = None
        if abs(c) > 40:
            bad = f"cross-track {c:.0f} ft"
        elif abs(wrap(hdg - HDG)) > 6:
            bad = f"heading error {wrap(hdg - HDG):.1f}°"
        elif ias > 130:
            bad = f"IAS {ias:.0f}"
        elif theta > 2.5:
            bad = f"pitch {theta:.1f}° (nose lift)"
        elif st["air"] >= 3:
            bad = "not on the ground"
        elif s_al > 9000:
            bad = f"along-track {s_al:.0f} ft"
        if bad:
            reason = "ABORT: " + bad
            print(reason, f"at {ias:.0f} KIAS, {s_al:.0f} ft")
    if t - t0 > 240:
        reason = reason if reason != "done" else "ABORT: time"
        break
    time.sleep(0.01)

ev("AXIS_RUDDER_SET", 0)
ev("AXIS_AILERONS_SET", 0)
ev("AXIS_ELEVATOR_SET", 0)
if g("BRAKE_PARKING_POSITION") != 1:
    ev("PARKING_BRAKES")
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "phase", "k", "ias", "along_ft", "cross_ft", "hdg_err", "yaw_rate_dps", "bank", "pitch", "rud_cmd"])
    w.writerows(rows)
dur = rows[-1][0] if rows else 1
print(f"{reason}; {len(rows)} samples ({len(rows) / max(dur, 1):.1f} Hz); stop at {rows[-1][4] if rows else 0} ft past the threshold")
for sp in steps_out:
    seg = [x for x in rows[sp["rows0"]:] if x[1] == "step" and x[2] == rows[sp["rows0"]][2]] if sp["rows0"] < len(rows) else []
    if len(seg) < 3:
        continue
    pk = max(seg, key=lambda x: abs(x[7]))[7]
    dh = seg[-1][6] - seg[0][6]
    dc = seg[-1][5] - seg[0][5]
    print(f"step {sp['val']:+.0f} counts at {seg[0][3]:.0f} KIAS: peak yaw rate {pk:+.1f}°/s, heading change {dh:+.2f}° in "
          f"{seg[-1][0] - seg[0][0]:.1f} s ({dh / max(seg[-1][0] - seg[0][0], 0.1) / sp['val'] * 1000:+.2f}°/s per 1 000 "
          f"counts), drift {dc:+.1f} ft")
