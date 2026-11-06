"""Refuel to the standard test state: 4 080 lb in the main cells (Center1), auxiliary cell (Center2) EMPTY as in flight
(it is transferred first), tip tanks EMPTY (clean, as the FM charts). Before 2026-10-30: Center2 full + 484.7 gal Center1.
Optional argument: main-cell fuel in lb (2026-11-06, F5 no-flap landing: FM 3-36 "fuel low, < 3 000 lb"); default 4 080.
Never below 1 600 lb (the watchdog refuels below 1 500 lb in the air)."""
import sys
import time

from SimConnect import AircraftRequests, SimConnect

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
print("before", {n: round(aq.get(f"FUEL_TANK_{n}_QUANTITY") or 0, 1) for n in ("CENTER", "CENTER2", "LEFT_TIP", "RIGHT_TIP")},
      round(aq.get("FUEL_TOTAL_QUANTITY_WEIGHT") or 0))
aq.set("FUEL_TANK_LEFT_TIP_QUANTITY", 0.0)
aq.set("FUEL_TANK_RIGHT_TIP_QUANTITY", 0.0)
aq.set("FUEL_TANK_CENTER2_QUANTITY", 0.0)
LB = max(1600.0, float(sys.argv[1])) if len(sys.argv) > 1 else 4080.0
aq.set("FUEL_TANK_CENTER_QUANTITY", LB / 6.5)
time.sleep(1.0)
print("after", {n: round(aq.get(f"FUEL_TANK_{n}_QUANTITY") or 0, 1) for n in ("CENTER", "CENTER2", "LEFT_TIP", "RIGHT_TIP")},
      round(aq.get("FUEL_TOTAL_QUANTITY_WEIGHT") or 0), "lb, weight", round(aq.get("TOTAL_WEIGHT") or 0))
sm.exit()
