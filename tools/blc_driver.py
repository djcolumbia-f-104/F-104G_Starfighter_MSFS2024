"""H3 BLC driver (card docs/notes/test-cards/H3-blc-rpm.md): rpm-dependent BLC flap lift as an EFFECTIVE trailing-edge
flap deflection. Runs in the background next to a test script (SimConnect, ≈ 10 Hz); the final add-on will need the same
logic as an in-aircraft gauge (AP-9).

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\blc_driver.py <log.csv> <seconds>
Law (build-up 1, 2026-10-31, ..._H3_bu1.csv): BLC fraction f(N1) [S] = 0.3 at idle 67 %, 0.6 at 75 %, 0.9 at 80 %, 1.0 at
≥ 83 % (FM 2-24: greatest effect above 80 %, some effect retained at lower power); TE percent p = 1 - 0.52 (1 - f)
(measured: TE 54 % -> ΔCL -0.116, 42 % -> -0.152 at constant α; full BLC loss ΔCL 0.135 -> 48 %).
Writes ONLY with the flap lever in LAND (index 2) and once the leading-edge flaps have reached their LAND stage (≥ 29°; they stop at 29.4° by the coupling):
MSFS moves all flap systems with one travel fraction and stops when the first reaches its stage - an early TE write froze
the LE flaps at 3° in build-up 1. Outside LAND it writes nothing (the flap system takes over).
"""
import csv
import sys
import time

from SimConnect import AircraftRequests, SimConnect

out, dur = sys.argv[1], float(sys.argv[2])
DEG = 57.29578
F_TABLE = [(67.0, 0.3), (75.0, 0.6), (80.0, 0.9), (83.0, 1.0)]          # [S] N1 % -> BLC fraction


def blc_fraction(n1):
    if n1 <= F_TABLE[0][0]:
        return F_TABLE[0][1]
    for (x0, y0), (x1, y1) in zip(F_TABLE, F_TABLE[1:]):
        if n1 <= x1:
            return y0 + (y1 - y0) * (n1 - x0) / (x1 - x0)
    return 1.0


def te_percent(f):
    return 1.0 - 0.52 * (1.0 - f)


sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
t0 = time.time()
active = False
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["t", "handle", "le_deg", "n1", "f", "te_set", "te_deg"])
    while time.time() - t0 < dur:
        handle = aq.get("FLAPS_HANDLE_INDEX")
        le = aq.get("LEADING_EDGE_FLAPS_LEFT_ANGLE")
        n1 = aq.get("TURB_ENG_N1:1")
        if handle is None or le is None or n1 is None:                  # failed read: do nothing this cycle
            time.sleep(0.05)
            continue
        if handle == 2 and (active or le * DEG >= 29.0):
            active = True
            f = blc_fraction(n1)
            p = te_percent(f)
            aq.set("TRAILING_EDGE_FLAPS_LEFT_PERCENT", p)
            aq.set("TRAILING_EDGE_FLAPS_RIGHT_PERCENT", p)
        else:
            if handle != 2:
                active = False
            f, p = float("nan"), float("nan")
        w.writerow([round(time.time() - t0, 2), int(handle), round(le * DEG, 1), round(n1, 1), round(f, 3), round(p, 3),
                    round((aq.get("TRAILING_EDGE_FLAPS_LEFT_ANGLE") or 0) * DEG, 1)])
        fh.flush()
        time.sleep(0.05)
sm.exit()
