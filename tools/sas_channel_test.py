"""H1 build-up bu0: SAS actuator channel check - rudder and aileron trim written as SimVars (card H1-sas.md).

Usage (with the Python of the simconnect-mcp venv; jet positioned with MCP `position` at 15 000 ft, TAS 545 kt,
AP ALT hold + wing leveler, yaw damper off):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\sas_channel_test.py <output.csv> [rud=0.5] [ail=0.1]
Steps: RUDDER TRIM PCT 0 -> +rud -> -rud -> 0, then AILERON TRIM PCT +ail -> -ail -> 0 (5 s each).
Per step (mean of the last 2 s): trim read back (pct and degrees), rudder/aileron deflection, sideslip, body rates, bank.
Answers: settable at all, sign (nose/roll direction per + percent), degrees per percent, lag, β per trim degree
(prediction 0.35 x trim degree if one trim degree acts like one rudder degree, T3-E2).
Abort: |β| > 5°, |bank| > 45°, |yaw rate| > 20°/s -> both trims 0, script ends (AP stays engaged).
"""
import csv
import sys
import time

from SimConnect import AircraftRequests, SimConnect

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
RUD = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
AIL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
DEG = 57.29578
STEP = 5.0
STEPS = [("rud", 0.0), ("rud", RUD), ("rud", -RUD), ("rud", 0.0), ("ail", AIL), ("ail", -AIL), ("ail", 0.0)]
VARS = ["RUDDER_TRIM_PCT", "RUDDER_TRIM", "RUDDER_DEFLECTION", "AILERON_TRIM_PCT", "AILERON_AVERAGE_DEFLECTION",
        "INCIDENCE_BETA", "ROTATION_VELOCITY_BODY_X", "ROTATION_VELOCITY_BODY_Y", "ROTATION_VELOCITY_BODY_Z",
        "PLANE_BANK_DEGREES"]
RAD = {"RUDDER_TRIM", "RUDDER_DEFLECTION", "AILERON_AVERAGE_DEFLECTION", "INCIDENCE_BETA", "ROTATION_VELOCITY_BODY_X",
       "ROTATION_VELOCITY_BODY_Y", "ROTATION_VELOCITY_BODY_Z", "PLANE_BANK_DEGREES"}

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)


def read():
    row = {}
    for v in VARS:
        x = aq.get(v)
        row[v] = None if x is None else (x * DEG if v in RAD else x)
    return row


def zero():
    aq.set("RUDDER_TRIM_PCT", 0.0)
    aq.set("AILERON_TRIM_PCT", 0.0)


rows = []
aborted = None
t0 = time.time()
try:
    for i, (axis, cmd) in enumerate(STEPS):
        aq.set("RUDDER_TRIM_PCT" if axis == "rud" else "AILERON_TRIM_PCT", cmd)
        while (t := time.time() - t0) < (i + 1) * STEP:
            r = read()
            rows.append({"t": round(t, 3), "step": i, "axis": axis, "cmd": cmd, **r})
            b, bank, yr = r["INCIDENCE_BETA"], r["PLANE_BANK_DEGREES"], r["ROTATION_VELOCITY_BODY_Y"]
            if (b is not None and abs(b) > 5) or (bank is not None and abs(bank) > 45) or (yr is not None and abs(yr) > 20):
                aborted = f"t {t:.1f} s: beta {b}, bank {bank}, yaw rate {yr}"
                break
        if aborted:
            break
finally:
    zero()
    sm.exit()

with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} samples ({len(rows) / max(rows[-1]['t'], 1e-3):.1f} Hz) -> {out}")
if aborted:
    print("ABORTED", aborted)


def mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else float("nan")


short = {"RUDDER_TRIM_PCT": "rtrim%", "RUDDER_TRIM": "rtrim°", "RUDDER_DEFLECTION": "rud°", "AILERON_TRIM_PCT": "atrim%",
         "AILERON_AVERAGE_DEFLECTION": "ail°", "INCIDENCE_BETA": "beta°", "ROTATION_VELOCITY_BODY_X": "qX°/s",
         "ROTATION_VELOCITY_BODY_Y": "rY°/s", "ROTATION_VELOCITY_BODY_Z": "pZ°/s", "PLANE_BANK_DEGREES": "bank°"}
print("step axis   cmd  " + " ".join(f"{s:>8}" for s in short.values()))
for i, (axis, cmd) in enumerate(STEPS):
    seg = [r for r in rows if r["step"] == i and r["t"] > (i + 1) * STEP - 2.0]
    if seg:
        print(f"{i:4d} {axis:4} {cmd:+5.2f} " + " ".join(f"{mean([r[v] for r in seg]):8.3f}" for v in short))
# lag: first sample after each step where the read-back trim reached half of the command change
for i in range(1, len(STEPS)):
    axis, cmd = STEPS[i]
    var = "RUDDER_TRIM_PCT" if axis == "rud" else "AILERON_TRIM_PCT"
    prev = STEPS[i - 1][1] if STEPS[i - 1][0] == axis else 0.0
    seg = [r for r in rows if r["step"] == i and r[var] is not None]
    hit = next((r for r in seg if abs(r[var] - prev) >= 0.5 * abs(cmd - prev) > 0), None)
    if hit:
        print(f"step {i}: {var} half-way after {hit['t'] - i * STEP:.2f} s")
