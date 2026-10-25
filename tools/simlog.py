"""Zeichnet SimVars zeitgleich in eine CSV auf (für Flugtests).

Aufruf (mit dem Python der simconnect-mcp-venv, die das Paket SimConnect enthält):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\simlog.py <ausgabe.csv> <sekunden> [hz]
"""
import csv
import sys
import time

from SimConnect import AircraftRequests, SimConnect

VARS = [
    ("INCIDENCE_ALPHA", "deg"),          # rad -> deg umgerechnet
    ("AIRSPEED_INDICATED", "kt"),
    ("AIRSPEED_TRUE", "kt"),
    ("AIRSPEED_MACH", "mach"),
    ("PLANE_ALTITUDE", "ft"),
    ("VERTICAL_SPEED", "ft/min"),
    ("G_FORCE", "g"),
    ("TOTAL_WEIGHT", "lb"),
    ("AMBIENT_DENSITY", "slug/ft3"),
    ("PLANE_PITCH_DEGREES", "deg"),      # rad -> deg
    ("GENERAL_ENG_THROTTLE_LEVER_POSITION:1", "pct"),
    ("TURB_ENG_JET_THRUST:1", "lbf"),
    ("FLAPS_HANDLE_INDEX", "-"),
    ("GEAR_HANDLE_POSITION", "-"),
    ("SIM_ON_GROUND", "-"),
    ("ELEVATOR_DEFLECTION", "deg"),      # rad -> deg
    ("ELEVATOR_TRIM_POSITION", "deg"),   # rad -> deg
    ("AUTOPILOT_MASTER", "-"),
    ("TURB_ENG_N1:1", "pct"),
    ("ENG_FUEL_FLOW_PPH:1", "lb/h"),
    ("ENG_EXHAUST_GAS_TEMPERATURE:1", "degC"),   # Rankine -> °C umgerechnet
    ("INCIDENCE_BETA", "deg"),                   # rad -> deg
    ("RUDDER_DEFLECTION", "deg"),                # rad -> deg
    ("PLANE_BANK_DEGREES", "deg"),               # rad -> deg
]
RAD = {"INCIDENCE_ALPHA", "PLANE_PITCH_DEGREES", "ELEVATOR_DEFLECTION", "ELEVATOR_TRIM_POSITION",
       "INCIDENCE_BETA", "RUDDER_DEFLECTION", "PLANE_BANK_DEGREES"}
RANKINE = {"ENG_EXHAUST_GAS_TEMPERATURE:1"}

out, seconds = sys.argv[1], float(sys.argv[2])
hz = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
t0 = time.time()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t"] + [f"{n}[{u}]" for n, u in VARS])
    while time.time() - t0 < seconds:
        row = [round(time.time() - t0, 2)]
        for name, _ in VARS:
            v = aq.get(name)
            if v is not None and name in RAD:
                v = v * 57.29578
            elif v is not None and name in RANKINE:
                v = (v - 491.67) * 5 / 9
            row.append(v)
        w.writerow(row)
        f.flush()
        time.sleep(1 / hz)
sm.exit()
print("fertig:", out)
