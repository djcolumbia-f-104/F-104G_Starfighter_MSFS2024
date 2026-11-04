"""Probe every SimVar/unit pair of the systems module in the running sim (lesson 2026-11-03: an invalid unit name -
"pounds per square foot" - silently killed the module's whole state request).

Usage (with the Python of the simconnect-mcp venv; sim running with the F-104G loaded):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\probe_units.py [source.cpp]
Parses every SimConnect_AddToDataDefinition(..., "NAME", "UNIT") of the source (default: the systems module), probes each
pair in its own short process (a SimConnect exception corrupts later reads in the same connection) and prints
OK / FAIL (SimConnect exception, e.g. NAME_UNRECOGNIZED) / NOVALUE (read timeout, not an error by itself). Exit code 1 on
any FAIL, 2 if the sim cannot be reached. Called by tools/build_wasm.sh before every module build and by selftest.py.
"""
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "source", "wasm",
                                                          "f104_systems", "F104Systems.cpp")
PROBE = r"""
import sys
from SimConnect import SimConnect
from SimConnect.RequestList import Request
try:
    sm = SimConnect()
except Exception as e:
    print("NOSIM", e); sys.exit(2)
v = Request((sys.argv[1].encode(), sys.argv[2].encode()), sm, _time=0, _attemps=20).value
print("VALUE", v)
sm.exit()
"""

pairs = re.findall(r'AddToDataDefinition\([^,]+,\s*\w+,\s*"([^"]+)",\s*"([^"]+)"', open(SRC, encoding="utf-8").read())
seen, fails = set(), 0
for name, unit in pairs:
    if (name, unit) in seen:
        continue
    seen.add((name, unit))
    try:
        r = subprocess.run([sys.executable, "-I", "-c", PROBE, name, unit], capture_output=True, text=True, timeout=20)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        out = "TIMEOUT"
    if "NOSIM" in out:
        print("sim not reachable - units NOT probed")
        sys.exit(2)
    if "EXCEPTION" in out:
        status = "FAIL"
        fails += 1
    elif "VALUE None" in out or "TIMEOUT" in out:
        status = "NOVALUE"
    else:
        status = "OK"
    print(f"{status:8} {name} | {unit}")
print(f"{len(seen)} pairs, {fails} FAIL")
sys.exit(1 if fails else 0)
