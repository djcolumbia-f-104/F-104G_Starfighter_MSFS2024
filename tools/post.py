"""Postconditions after a test script (test process step 6, docs/notes/test-process.md): is the jet in a safe, defined state?

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\post.py [air|ground]
or from a script: `from post import post_check; post_check(aq, "air")` (prints and returns True/False).
air (default): airborne, AP master on, |vertical speed| < 500 ft/min, |bank| < 5°, |pitch| < 10°, fuel ≥ 1 500 lb,
               gear and flaps up, yaw damper switch at the default (L:F104_SAS_YAW_OFF 0, L:F104_SAS_YAW_GAIN 0).
ground: on the ground, ground speed < 5 kt, throttle idle, damper switches at the default.
Prints "POST OK" or "POST FAIL: <items>"; exit code 0/1. The AP is read twice 1 s apart (a toggle event can leave it off).
2026-11-04: the checks are repeated every 3 s for up to `settle` s (default 45) - after `position` the AP still climbs back
to its altitude for ≈ 30 s; only the state after that counts.
"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

DEG = 57.29578


def post_check(aq, sm, mode="air", settle=45.0):
    t_end = time.time() + settle
    while True:
        bad = _failed_items(aq, sm, mode)
        if not bad or time.time() > t_end:
            break
        time.sleep(3.0)
    print("POST OK" if not bad else "POST FAIL: " + "; ".join(bad))
    return not bad


def _failed_items(aq, sm, mode):
    from SimConnect.RequestList import Request

    def g(n):
        return aq.get(n) or 0

    lv = {n: Request((n.encode(), b"number"), sm, _time=0, _attemps=10).value
          for n in ("L:F104_SAS_YAW_OFF", "L:F104_SAS_YAW_GAIN")}
    bad = []
    if mode == "air":
        ap1 = g("AUTOPILOT_MASTER")
        time.sleep(1.0)
        checks = [
            (g("SIM_ON_GROUND") < 0.5, "not airborne"),
            (ap1 == 1 and g("AUTOPILOT_MASTER") == 1, "AP off"),
            (abs(g("VERTICAL_SPEED")) < 500, f"VS {g('VERTICAL_SPEED'):.0f} ft/min"),
            (abs(g("PLANE_BANK_DEGREES") * DEG) < 5, f"bank {g('PLANE_BANK_DEGREES') * DEG:.1f}°"),
            (abs(g("PLANE_PITCH_DEGREES") * DEG) < 10, f"pitch {-g('PLANE_PITCH_DEGREES') * DEG:.1f}°"),
            (g("FUEL_TOTAL_QUANTITY_WEIGHT") >= 1500, f"fuel {g('FUEL_TOTAL_QUANTITY_WEIGHT'):.0f} lb"),
            (g("GEAR_TOTAL_PCT_EXTENDED") < 0.05, "gear not up"),
            (g("TRAILING_EDGE_FLAPS_LEFT_ANGLE") * DEG < 1, "flaps not up"),
        ]
    else:
        checks = [
            (g("SIM_ON_GROUND") > 0.5, "not on the ground"),
            (g("GROUND_VELOCITY") < 5, f"ground speed {g('GROUND_VELOCITY'):.0f} kt"),
            (g("GENERAL_ENG_THROTTLE_LEVER_POSITION:1") < 5, "throttle not idle"),
        ]
    checks += [((lv["L:F104_SAS_YAW_OFF"] or 0) == 0, "yaw damper switched OFF"),
               ((lv["L:F104_SAS_YAW_GAIN"] or 0) == 0, f"yaw damper gain {lv['L:F104_SAS_YAW_GAIN']} (not default)")]
    return [msg for ok, msg in checks if not ok]


if __name__ == "__main__":
    from SimConnect import AircraftRequests, SimConnect
    sm = SimConnect()
    ok = post_check(AircraftRequests(sm, _time=0), sm, sys.argv[1] if len(sys.argv) > 1 else "air")
    sm.exit()
    sys.exit(0 if ok else 1)
