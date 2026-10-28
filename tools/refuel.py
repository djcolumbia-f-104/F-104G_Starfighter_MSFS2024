"""Refuel to the standard test state: 4 080 lb in the fuselage tanks, tip tanks EMPTY (clean, as the FM charts)."""
import time

from SimConnect import AircraftRequests, SimConnect

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
print("before", {n: round(aq.get(f"FUEL_TANK_{n}_QUANTITY") or 0, 1) for n in ("CENTER", "CENTER2", "LEFT_TIP", "RIGHT_TIP")},
      round(aq.get("FUEL_TOTAL_QUANTITY_WEIGHT") or 0))
aq.set("FUEL_TANK_LEFT_TIP_QUANTITY", 0.0)
aq.set("FUEL_TANK_RIGHT_TIP_QUANTITY", 0.0)
aq.set("FUEL_TANK_CENTER2_QUANTITY", 143.0)
aq.set("FUEL_TANK_CENTER_QUANTITY", 4080 / 6.5 - 143.0)
time.sleep(1.0)
print("after", {n: round(aq.get(f"FUEL_TANK_{n}_QUANTITY") or 0, 1) for n in ("CENTER", "CENTER2", "LEFT_TIP", "RIGHT_TIP")},
      round(aq.get("FUEL_TOTAL_QUANTITY_WEIGHT") or 0), "lb, weight", round(aq.get("TOTAL_WEIGHT") or 0))
sm.exit()
