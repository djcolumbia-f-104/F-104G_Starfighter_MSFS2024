"""H5 drag chute research: ground coast-down test - which drag acts on the ground with the speed brakes / "chute" out?

Usage (with the Python of the simconnect-mcp venv; after MCP runway_start, jet on EDDM 26L, aligned):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\coast_test.py <output.csv> [sb|clean]
Sequence: full AB against the parking brake, release at N1 ≥ 99 %, accelerate to 160 KIAS with the nose held at 0° (no
rotation), idle (+ SPOILERS_ON if "sb"), coast WITHOUT wheel brakes from 155 to 100 KIAS (deceleration logged), then
full wheel brakes to a stop. Nose held at 0° pitch actively all the time (takeoff trim 5° would lift the jet at
≈ 170 kt - 2026-10-30 taxi incident); rudder holds the runway heading. Abort (idle, brakes): airborne, heading error > 5°.
Evaluation: mean deceleration 150 -> 110 KIAS (ft/s²) with and without speed brakes.
"""
import csv
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
SB = "sb" in sys.argv[2:]
DEG = 57.29578
RWY_HDG = 263.4
FULL = 16383

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


def wrap(d):
    return (d + 180) % 360 - 180


if g("SIM_ON_GROUND") != 1 or abs(wrap(g("PLANE_HEADING_DEGREES_TRUE") * DEG - RWY_HDG)) > 2:
    sm.exit()
    sys.exit("ABORT: not on the ground aligned with 26L - run runway_start first")
ev("SPOILERS_OFF")
ev("AXIS_ELEVATOR_SET", 0)
if g("BRAKE_PARKING_POSITION") != 1:
    ev("PARKING_BRAKES")
ev("THROTTLE1_SET", FULL)
t_sp = time.time()
while time.time() - t_sp < 12 and g("TURB_ENG_N1:1") < 99:
    time.sleep(0.2)
ev("PARKING_BRAKES")
t0 = time.time()
phase, rows, reason = "accel", [], "done"
prev_t = t0
while time.time() - t0 < 120:
    t = time.time()
    dt = max(t - prev_t, 0.02)
    prev_t = t
    ias, gs, gnd = g("AIRSPEED_INDICATED"), g("GROUND_VELOCITY"), g("SIM_ON_GROUND") == 1
    theta = -g("PLANE_PITCH_DEGREES") * DEG
    herr = wrap(RWY_HDG - g("PLANE_HEADING_DEGREES_TRUE") * DEG)
    # nose held at 0° (push grows with pitch; +axis = nose down), rudder on the runway heading (+axis = nose left)
    ev("AXIS_ELEVATOR_SET", int(max(0.0, min(FULL, 3000.0 + 2500.0 * theta))))
    ev("AXIS_RUDDER_SET", int(max(-8000, min(8000, -700.0 * herr))))
    if (not gnd and g("PLANE_ALT_ABOVE_GROUND") > 3) or abs(herr) > 5:
        reason = f"ABORT: airborne or heading error {herr:.1f}° at {ias:.0f} KIAS"
        phase = "brake"
    if phase == "accel" and ias >= 160:
        phase = "coast"
        ev("THROTTLE1_SET", 0)
        if SB:
            ev("SPOILERS_ON")
    elif phase == "coast" and ias <= 100:
        phase = "brake"
    if phase == "brake":
        ev("THROTTLE1_SET", 0)
        ev("AXIS_LEFT_BRAKE_SET", FULL)
        ev("AXIS_RIGHT_BRAKE_SET", FULL)
        if gs < 3:
            break
    rows.append([round(t - t0, 2), phase, round(ias, 1), round(gs, 1), int(gnd), round(theta, 2), round(herr, 2),
                 round(g("TURB_ENG_N1:1"), 1), round(g("TURB_ENG_JET_THRUST:1")), round(g("SPOILERS_HANDLE_POSITION"), 2)])
    time.sleep(0.05)

ev("SPOILERS_OFF")
for n in ("AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET"):
    ev(n, 0)
ev("PARKING_BRAKES") if g("BRAKE_PARKING_POSITION") != 1 else None
for n in ("AXIS_LEFT_BRAKE_SET", "AXIS_RIGHT_BRAKE_SET"):
    ev(n, -FULL)
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "phase", "ias", "gs", "gnd", "pitch", "hdg_err", "n1", "thrust", "spoilers"])
    w.writerows(rows)
c = [r for r in rows if r[1] == "coast" and 110 <= r[2] <= 150]
print(reason)
if len(c) > 2:
    dec = (c[0][3] - c[-1][3]) * 1.68781 / max(c[-1][0] - c[0][0], 0.1)
    print(f"{'SPEED BRAKES OUT' if SB else 'clean'}: coast 150 -> 110 KIAS mean deceleration {dec:.2f} ft/s² "
          f"({len(c)} samples), mean thrust {sum(r[8] for r in c) / len(c):.0f} lbf, spoilers {c[-1][9]}")
print(f"{len(rows)} samples -> {out}")
