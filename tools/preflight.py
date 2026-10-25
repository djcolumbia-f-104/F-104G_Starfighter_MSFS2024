"""Vorflugprüfung im laufenden Sim (Testebene T2, siehe docs/flight-model-plan.md).

Aufruf (mit dem Python der simconnect-mcp-venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\preflight.py
Prüft, ob der Prüfstand geladen ist, die Simulation läuft und das Triebwerk brennt; gibt den Ausgangszustand aus.
Rückgabewert 1, wenn eine Prüfung fehlschlägt.
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
    ("Prüfstand geladen", "F-104G" in (get("TITLE") or ""), get("TITLE")),
    ("Simulation läuft (nicht pausiert)", t1 is not None and t2 is not None and t2 > t1, ""),
    ("Triebwerk brennt", get("GENERAL_ENG_COMBUSTION:1") == 1, ""),
    ("N1 >= 60 %", (get("TURB_ENG_N1:1") or 0) >= 60, f"{get('TURB_ENG_N1:1') or 0:.1f} %"),
    ("Tankwahl ALL", get("FUEL_TANK_SELECTOR:1") == 1, get("FUEL_TANK_SELECTOR:1")),
    ("Batterie an", get("ELECTRICAL_MASTER_BATTERY") == 1, ""),
]
state = [
    ("Am Boden", get("SIM_ON_GROUND")), ("Höhe ft", get("PLANE_ALTITUDE")), ("IAS kt", get("AIRSPEED_INDICATED")),
    ("Gewicht lb", get("TOTAL_WEIGHT")), ("Kraftstoff lb", get("FUEL_TOTAL_QUANTITY_WEIGHT")),
    ("Schwerpunkt % MAC", (get("CG_PERCENT") or 0) * 100), ("Fahrwerkhebel", get("GEAR_HANDLE_POSITION")),
    ("Klappenstufe", get("FLAPS_HANDLE_INDEX")), ("Parkbremse", get("BRAKE_PARKING_POSITION")),
    ("Höhenruder °", (get("ELEVATOR_DEFLECTION") or 0) * 57.29578),
    ("Trimmung °", (get("ELEVATOR_TRIM_POSITION") or 0) * 57.29578), ("Autopilot", get("AUTOPILOT_MASTER")),
    ("Schub lbf", get("TURB_ENG_JET_THRUST:1")),
]
sm.exit()
for text, ok, info in checks:
    print(f"{'OK' if ok else 'FEHLER':7} {text:34} {info if info is not None else ''}")
print()
for text, v in state:
    print(f"        {text:34} {v:.2f}" if isinstance(v, float) else f"        {text:34} {v}")
sys.exit(0 if all(ok for _, ok, _ in checks) else 1)
