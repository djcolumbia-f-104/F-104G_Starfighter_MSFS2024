"""Session-start self test (test process step 0, docs/notes/test-process.md) - run before the first flight of a session
and after every Build All / sim restart.

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\selftest.py [nounits]
Checks: SimConnect + aircraft title; systems module running with the version of the source (L:F104_SYS_VERSION vs.
SYS_VERSION in F104Systems.cpp); every SimVar/unit pair of the module valid (tools/probe_units.py, ≈ 6 s; skip with
"nounits"); watchdog alive (build/watchdog.log written < 120 s ago); calm ISA weather (wind < 3 kt, QNH 1013.25 ± 1, OAT
within ± 5 °C of ISA); damper switches at the default; build current (tools/check_cfg.py T1, tools venv); plus the
preflight state (engine, fuel, flaps, trim, AP) for the record. Prints one line per check and "SELFTEST ALL OK" or
"SELFTEST FAIL (n)"; exit code 0/1.
"""
import os
import re
import subprocess
import sys
import time

from SimConnect import AircraftRequests, SimConnect
from SimConnect.RequestList import Request

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DEG = 57.29578
results = []


def check(ok, name, detail=""):
    results.append(ok)
    print(f"{'OK  ' if ok else 'FAIL'}  {name:38} {detail}")


try:
    sm = SimConnect()
except Exception as e:
    print(f"FAIL  SimConnect                             {e}")
    sys.exit(1)
aq = AircraftRequests(sm, _time=0)


def g(n):
    return aq.get(n)


def lvar(n):
    return Request((n.encode(), b"number"), sm, _time=0, _attemps=20).value


title = (aq.get("TITLE") or b"")
title = title.decode(errors="ignore") if isinstance(title, bytes) else str(title)
check("F-104G" in title, "aircraft", title)
src = open(os.path.join(ROOT, "source", "wasm", "f104_systems", "F104Systems.cpp"), encoding="utf-8").read()
want = float(re.search(r"SYS_VERSION\s*=\s*([\d.]+)", src).group(1))
have = lvar("L:F104_SYS_VERSION")
check(have is not None and abs(have - want) < 1e-6, "module version (sim vs. source)", f"{have} / {want}")
off, gain = lvar("L:F104_SAS_YAW_OFF"), lvar("L:F104_SAS_YAW_GAIN")
check((off or 0) == 0 and (gain or 0) == 0, "yaw damper switch default (ON, gain 1)", f"OFF {off}, GAIN {gain}")
wind, qnh, oat, alt = g("AMBIENT_WIND_VELOCITY"), g("SEA_LEVEL_PRESSURE"), g("AMBIENT_TEMPERATURE"), g("PLANE_ALTITUDE")
isa = 15.0 - 1.98 * (alt or 0) / 1000.0
# 2026-11-06 (F9): `wind=<dir>:<kt>` = a crosswind weather preset (tools/make_wpr.py) is expected instead of calm air; the
# sim reduces the ground wind (preset 350/10 -> 5 kt at the runway, 10 kt at 2 km) -> accept 30 % .. 100 % + 3 kt, ± 30°
WEXP = next(([float(v) for v in a.split("=")[1].split(":")] for a in sys.argv[1:] if a.startswith("wind=")), None)
wdir = g("AMBIENT_WIND_DIRECTION")
if WEXP:
    ddir = abs(((wdir or 0) - WEXP[0] + 180) % 360 - 180)
    check(wind is not None and 0.3 * WEXP[1] <= wind <= WEXP[1] + 3 and ddir <= 30,
          f"wind preset {WEXP[0]:.0f}°/{WEXP[1]:.0f} kt", f"{wdir:.0f}° / {wind:.1f} kt at the aircraft")
else:
    check(wind is not None and wind < 3, "wind < 3 kt", f"{wind:.1f} kt" if wind is not None else "no value")
check(qnh is not None and abs(qnh - 1013.25) <= 1, "QNH 1013.25 ± 1", f"{qnh:.2f}" if qnh is not None else "no value")
check(oat is not None and abs(oat - isa) <= 5, "OAT within ± 5 °C of ISA", f"{oat:.1f} °C (ISA {isa:.1f})"
      if oat is not None else "no value")
fuel_now = g("FUEL_TOTAL_QUANTITY_WEIGHT") or 0
state = (f"ground {g('SIM_ON_GROUND'):.0f}, N1 {g('TURB_ENG_N1:1'):.1f} %, fuel {g('FUEL_TOTAL_QUANTITY_WEIGHT'):.0f} lb, "
         f"flaps {g('TRAILING_EDGE_FLAPS_LEFT_ANGLE') * DEG:.1f}°, trim {g('ELEVATOR_TRIM_POSITION') * DEG:.2f}°, AP "
         f"{g('AUTOPILOT_MASTER'):.0f}")
sm.exit()

log = os.path.join(ROOT, "build", "watchdog.log")
age = time.time() - os.path.getmtime(log) if os.path.exists(log) else None
check(age is not None and age < 120, "watchdog alive (log < 120 s)", f"log age {age:.0f} s" if age is not None else
      "no log - start tools/watchdog.py")
# 2026-11-04: a watchdog on a dead connection kept logging stale values -> its last fuel must match the sim
wd_fuel = None


def last_ok():
    oks = [ln for ln in open(log, encoding="utf-8").read().splitlines() if " ok: fuel " in ln]
    return (oks[-1], float(oks[-1].split("fuel ")[1].split(" lb")[0])) if oks else (None, None)


if age is not None:
    line, wd_fuel = last_ok()
    # 2026-11-05 + 2026-11-06: a refuel between two watchdog status lines (one per minute) looked like a stale watchdog
    # -> on a mismatch wait for the NEXT status line (≤ 75 s) and compare it with a fresh sim reading
    if wd_fuel is not None and abs(wd_fuel - fuel_now) >= 100:
        t_w = time.time()
        while time.time() - t_w < 75 and last_ok()[0] == line:
            time.sleep(2)
        line2, wd_fuel = last_ok()
        if line2 != line:
            sm2 = SimConnect()
            fuel_now = AircraftRequests(sm2, _time=0).get("FUEL_TOTAL_QUANTITY_WEIGHT") or 0
            sm2.exit()
check(wd_fuel is not None and abs(wd_fuel - fuel_now) < 100, "watchdog sees the live sim (fuel ± 100 lb)",
      f"watchdog {wd_fuel} lb, sim {fuel_now:.0f} lb")
if "nounits" not in sys.argv[1:]:
    r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "probe_units.py")], capture_output=True,
                       text=True, timeout=180)
    check(r.returncode == 0, "module SimVar/unit pairs", (r.stdout.strip().splitlines() or ["no output"])[-1])
venv = os.path.join(ROOT, "tools", ".venv", "Scripts", "python.exe")
r = subprocess.run([venv, "-I", os.path.join(ROOT, "tools", "check_cfg.py"), ROOT], capture_output=True, text=True,
                   timeout=120)
check(r.returncode == 0 and " 0 ERRORS" in r.stdout, "build current (check_cfg T0/T1)",
      (r.stdout.strip().splitlines() or ["no output"])[-1][:60])
print(f"      state: {state}")
n_fail = results.count(False)
print("SELFTEST ALL OK" if not n_fail else f"SELFTEST FAIL ({n_fail})")
sys.exit(0 if not n_fail else 1)
