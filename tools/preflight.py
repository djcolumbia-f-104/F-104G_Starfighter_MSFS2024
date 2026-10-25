"""Preflight check in the running sim (test level T2, see docs/flight-model-plan.md).

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\preflight.py
Checks that the test bed is loaded, the simulation is running and the engine is lit; prints the initial state.
Exit code 1 if a check fails.
"""
import sys
import time

from SimConnect import AircraftRequests, SimConnect

sys.stdout.reconfigure(encoding="utf-8")
sm = SimConnect()
aq = AircraftRequests(sm, _time=0)


def get(name):
    v = aq.get(name)
    return v.decode(errors="replace") if isinstance(v, bytes) else v


t1 = get("ABSOLUTE_TIME")
time.sleep(1.0)
t2 = get("ABSOLUTE_TIME")
checks = [
    ("Test bed loaded", "F-104G" in (get("TITLE") or ""), get("TITLE")),
    ("Simulation running (not paused)", t1 is not None and t2 is not None and t2 > t1, ""),
    ("Engine lit", get("GENERAL_ENG_COMBUSTION:1") == 1, ""),
    ("N1 >= 60 %", (get("TURB_ENG_N1:1") or 0) >= 60, f"{get('TURB_ENG_N1:1') or 0:.1f} %"),
    ("Fuel selector ALL", get("FUEL_TANK_SELECTOR:1") == 1, get("FUEL_TANK_SELECTOR:1")),
    ("Battery on", get("ELECTRICAL_MASTER_BATTERY") == 1, ""),
]
state = [
    ("On ground", get("SIM_ON_GROUND")), ("Altitude ft", get("PLANE_ALTITUDE")), ("IAS kt", get("AIRSPEED_INDICATED")),
    ("Weight lb", get("TOTAL_WEIGHT")), ("Fuel lb", get("FUEL_TOTAL_QUANTITY_WEIGHT")),
    ("CG % MAC", (get("CG_PERCENT") or 0) * 100), ("Gear lever", get("GEAR_HANDLE_POSITION")),
    ("Gear extended %", get("GEAR_TOTAL_PCT_EXTENDED")),
    ("Flap lever", get("FLAPS_HANDLE_INDEX")),
    ("Flaps trailing edge °", (get("TRAILING_EDGE_FLAPS_LEFT_ANGLE") or 0) * 57.29578),  # the lever alone is not enough (T3-D run 5)
    ("Parking brake", get("BRAKE_PARKING_POSITION")),
    ("Elevator °", (get("ELEVATOR_DEFLECTION") or 0) * 57.29578),
    ("Trim °", (get("ELEVATOR_TRIM_POSITION") or 0) * 57.29578), ("Autopilot", get("AUTOPILOT_MASTER")),
    ("Thrust lbf", get("TURB_ENG_JET_THRUST:1")),
]
sm.exit()
for text, ok, info in checks:
    print(f"{'OK' if ok else 'FAIL':7} {text:34} {info if info is not None else ''}")
print()
for text, v in state:
    print(f"        {text:34} {v:.2f}" if isinstance(v, float) else f"        {text:34} {v}")
sys.exit(0 if all(ok for _, ok, _ in checks) else 1)
