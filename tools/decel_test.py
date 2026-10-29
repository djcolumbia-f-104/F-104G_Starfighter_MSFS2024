"""T3-A / T3-F / T3-G deceleration run (docs/notes/test-procedures.md): lift, drag and trim gradient at idle.

Usage (with the Python of the simconnect-mcp venv; the jet is airborne, e.g. after MCP `position`):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\decel_test.py <output.csv> [alt_ft=16500] [ias_start=600]
Sequence: clean, AP ALT hold (current target alt_ft) + HDG -> full AB until ias_start (or M 1.15) -> idle -> deceleration
in ALT hold until ~215 KIAS (AP trim near its 11° stop) or sinking -> Military, end. simlog (3 Hz) runs throughout.
Evaluation: tools\\.venv\\Scripts\\python.exe -I tools\\analyse_lift.py . <csv> and analyse_drag.py . <csv> <t_idle+3> <t_end>
(the script prints both times).
"""
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
alt0 = float(sys.argv[2]) if len(sys.argv) > 2 else 16500.0
ias_start = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0
DEG = 57.29578

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 2000:
    sm.exit()
    sys.exit("ABORT: on the ground or fuel < 2 000 lb")
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
ev("AP_ALT_VAR_SET_ENGLISH", int(alt0))
ev("AP_ALT_HOLD_ON")
log = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(__file__), "simlog.py"), out, "330", "3"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
t0 = time.time()
print(f"start: {g('PLANE_ALTITUDE'):.0f} ft, {g('AIRSPEED_INDICATED'):.0f} KIAS, M {g('AIRSPEED_MACH'):.2f}, "
      f"OAT {g('AMBIENT_TEMPERATURE'):.1f} °C, weight {g('TOTAL_WEIGHT'):.0f} lb")
ev("THROTTLE1_SET", 16383)
while time.time() - t0 < 90 and g("AIRSPEED_INDICATED") < ias_start and g("AIRSPEED_MACH") < 1.15:
    time.sleep(1.0)
ev("THROTTLE1_SET", 0)
t_idle = time.time() - t0
# reference = altitude at idle start (2026-10-29: the jet had sunk to 15 000 ft after positioning, a fixed alt0 - 400
# criterion ended the run at once); hold that altitude
alt_ref = g("PLANE_ALTITUDE")
ev("AP_ALT_VAR_SET_ENGLISH", int(alt_ref))
ev("AP_ALT_HOLD_ON")
print(f"idle at t {t_idle:.0f} s: {g('AIRSPEED_INDICATED'):.0f} KIAS, M {g('AIRSPEED_MACH'):.2f}")
reason = "time"
while time.time() - t0 < 320:
    ias, trim, alt = g("AIRSPEED_INDICATED"), g("ELEVATOR_TRIM_POSITION") * DEG, g("PLANE_ALTITUDE")
    if ias < 215 or trim > 10.5 or alt < alt_ref - 400:
        reason = f"{ias:.0f} KIAS, trim {trim:.1f}°, alt {alt:.0f} ft"
        break
    time.sleep(1.0)
t_end = time.time() - t0
ev("THROTTLE1_SET", 11141)
print(f"end at t {t_end:.0f} s ({reason}) -> Military")
time.sleep(5)
log.terminate()
sm.exit()
print(f"log {out}; analyse_drag window: {t_idle + 3:.0f} {t_end:.0f}")
