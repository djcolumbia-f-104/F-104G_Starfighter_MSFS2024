"""Sim watchdog (2026-11-03): protects the jet while Claude is busy or a tool call hangs.

Usage (with the Python of the simconnect-mcp venv, in the background for the whole session):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\watchdog.py [log=build/watchdog.log]
Every 2 s: fuel, height AGL, vertical speed, bank, on-ground.
- airborne and fuel < 1 500 lb -> refuel to the standard state (tools/refuel.py logic: main cells 4 080 lb, rest 0); logged
  as REFUEL (a test running at that moment sees a weight step - check the log against the test time).
- airborne and (AGL < 2 000 ft with sink > 6 000 ft/min, or |bank| > 90°) -> logged as ALERT only (pete 2026-11-04: the
  watchdog only refuels, it never pauses the sim).
One status line per minute. Background: msfs_save_flight blocked the sim for ≈ 20 min on 2026-11-03 (fuel 3 509 -> 1 280 lb).
Reconnects after SimConnect errors (sim restart) every 10 s.
"""
import os
import sys
import time

from SimConnect import AircraftRequests, SimConnect

LOG = sys.argv[1] if len(sys.argv) > 1 else os.path.join("build", "watchdog.log")
DEG = 57.29578
os.makedirs(os.path.dirname(LOG) or ".", exist_ok=True)


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def run():
    sm = SimConnect()
    aq = AircraftRequests(sm, _time=0)
    log("connected")
    last_status, alerted, misses, frozen, last_simt = 0.0, False, 0, 0, None
    while True:
        fuel = aq.get("FUEL_TOTAL_QUANTITY_WEIGHT")
        ground = aq.get("SIM_ON_GROUND")
        agl = aq.get("PLANE_ALT_ABOVE_GROUND")
        vs = aq.get("VERTICAL_SPEED")                      # ft/min in this library
        bank = (aq.get("PLANE_BANK_DEGREES") or 0) * DEG
        simt = aq.get("ABSOLUTE_TIME")                   # SIMULATION_TIME is not in the library catalog (None)
        # 2026-11-04: after a sim restart the old connection kept returning its last cached values (fuel 155 lb while the
        # new flight had 4 081) -> frozen simulation time for 30 s = stale (or paused) -> reconnect
        if simt is not None and simt == last_simt:
            frozen += 1
            if frozen >= 15:
                raise ConnectionError("simulation time frozen for 30 s (sim restarted or paused)")
        else:
            frozen = 0
        last_simt = simt
        if None in (fuel, ground, agl, vs):
            # 2026-11-04: after a sim restart the old connection returns None forever -> reconnect after 30 s
            misses += 1
            if misses >= 15:
                raise ConnectionError("no values for 30 s (sim restarted?)")
            time.sleep(2)
            continue
        misses = 0
        if ground < 0.5 and fuel < 1500:
            aq.set("FUEL_TANK_LEFT_TIP_QUANTITY", 0.0)
            aq.set("FUEL_TANK_RIGHT_TIP_QUANTITY", 0.0)
            aq.set("FUEL_TANK_CENTER2_QUANTITY", 0.0)
            aq.set("FUEL_TANK_CENTER_QUANTITY", 4080 / 6.5)
            log(f"REFUEL at {fuel:.0f} lb (AGL {agl:.0f} ft)")
        danger = ground < 0.5 and ((agl < 2000 and vs < -6000) or abs(bank) > 90)
        if danger and not alerted:
            log(f"ALERT: AGL {agl:.0f} ft, VS {vs:.0f} ft/min, bank {bank:.0f}°")
        alerted = danger
        if time.time() - last_status > 60:
            log(f"ok: fuel {fuel:.0f} lb, AGL {agl:.0f} ft, VS {vs:.0f}, bank {bank:.0f}, ground {ground:.0f}, simtime "
                f"{(simt or 0) % 86400:.0f} s")
            last_status = time.time()
        time.sleep(2)


while True:
    try:
        run()
    except Exception as e:                                 # sim restart / SimConnect gone
        log(f"error {type(e).__name__}: {e} - reconnect in 10 s")
        time.sleep(10)
