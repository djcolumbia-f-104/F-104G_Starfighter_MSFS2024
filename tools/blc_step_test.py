"""H3 build-up 1 (card docs/notes/test-cards/H3-blc-rpm.md): trailing-edge flap override steps in the landing
configuration IN THE AIR -> lift change per TE percent (which lift scalar MSFS applies at an intermediate TE angle).

Usage (with the Python of the simconnect-mcp venv; jet AIRBORNE - never position from the ground):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\blc_step_test.py <output.csv> [steps=1,0.54,0.42,1] [ias=185] [alt=12000] [shots]
Sequence: set_pos, gear DOWN, flaps LAND, trim 5.2° (AP off), throttle PI holds the IAS (N1 stays high), elevator PI
holds the altitude; 25 s settle, then each TE step (SimVar TRAILING_EDGE_FLAPS_LEFT/RIGHT_PERCENT written every cycle)
for 20 s. Per step (last 10 s): α, CL = W n / (q S) (q from AIRSPEED_TRUE and AMBIENT_DENSITY), TE angle, LE angle,
N1, elevator. "shots": sim screenshot (tools/screenshot.ps1) at the end of each step for the debug drag window.
End: TE 100 %, gear up, flaps TAKEOFF, Military, flaps UP at ≥ 265 KIAS, AP ALT hold.
Abort (-> end): pitch outside -10..20°, |bank| > 30°, IAS < 160.
"""
import csv
import os
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
out = sys.argv[1]
STEPS = [float(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else [1.0, 0.54, 0.42, 1.0]
IAS0 = float(sys.argv[3]) if len(sys.argv) > 3 else 185.0
ALT0 = float(sys.argv[4]) if len(sys.argv) > 4 else 12000.0
SHOTS = "shots" in sys.argv[5:]
DEG = 57.29578
HDG = 263.4
LAT, LON = 48.36, 12.10
TRIM_DEG = 5.2
STEP_S, SETTLE_S = 20.0, 25.0

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    (ae.find(name) or Event(name.encode(), sm))(*arg)


def g(name):
    return aq.get(name) or 0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def te(frac):
    aq.set("TRAILING_EDGE_FLAPS_LEFT_PERCENT", frac)
    aq.set("TRAILING_EDGE_FLAPS_RIGHT_PERCENT", frac)


def shot(tag):
    if SHOTS:
        png = out.replace(".csv", f"_{tag}.png")
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(os.path.dirname(__file__), "screenshot.ps1"), png, "-Sim"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)


if g("SIM_ON_GROUND") == 1 or g("FUEL_TOTAL_QUANTITY_WEIGHT") < 2000:
    sm.exit()
    sys.exit("ABORT: on the ground or fuel < 2 000 lb - take off / refuel first")
for _ in range(3):
    if g("AUTOPILOT_MASTER") != 1:
        break
    ev("AP_MASTER")
    time.sleep(0.3)
sm.set_pos(ALT0, LAT, LON, int(IAS0), -4.0, 0.0, HDG, 0)
time.sleep(1.0)
ev("GEAR_DOWN")
ev("FLAPS_DOWN")
for _ in range(5):
    aq.set("ELEVATOR_TRIM_POSITION", TRIM_DEG / DEG)
    time.sleep(0.2)
    if abs(g("ELEVATOR_TRIM_POSITION") * DEG - TRIM_DEG) < 0.3:
        break
ev("THROTTLE1_SET", 11141)
print(f"weight {g('TOTAL_WEIGHT'):.0f} lb, trim {g('ELEVATOR_TRIM_POSITION') * DEG:.1f}°, IAS {g('AIRSPEED_INDICATED'):.0f}, "
      f"steps {STEPS}")

rows, reason = [], "done"
st = {"integ": 0.0, "th": 11141.0, "vs_f": 0.0}
t0 = prev_t = time.time()
prev_alt, prev_th = g("PLANE_ALTITUDE"), -g("PLANE_PITCH_DEGREES") * DEG
seg = -1                                          # -1 = settle
while True:
    t = time.time()
    dt = max(t - prev_t, 0.05)
    prev_t = t
    el = t - t0
    new_seg = -1 if el < SETTLE_S else int((el - SETTLE_S) // STEP_S)
    if new_seg != seg:
        if seg >= 0:
            shot(f"step{seg}")
        seg = new_seg
        if seg >= len(STEPS):
            break
    frac = 1.0 if seg < 0 else STEPS[seg]
    te(frac)
    alt, ias = g("PLANE_ALTITUDE") or prev_alt, g("AIRSPEED_INDICATED")
    theta, bank = -g("PLANE_PITCH_DEGREES") * DEG, g("PLANE_BANK_DEGREES") * DEG
    q = (theta - prev_th) / dt
    vs = (alt - prev_alt) / dt * 60
    st["vs_f"] = 0.5 * st["vs_f"] + 0.5 * vs
    prev_alt, prev_th = alt, theta
    # elevator PI on the vertical speed towards the start altitude (landing_test.py gains)
    err = (st["vs_f"] - clamp(4.0 * (ALT0 - alt), -800.0, 800.0)) / 60.0
    st["integ"] = clamp(st["integ"] + err * dt, -200, 200)
    cmd = clamp(300.0 * err + 10.0 * st["integ"] + 150.0 * q, -9000, 6000)
    ev("AXIS_ELEVATOR_SET", int(cmd))
    ev("AXIS_AILERONS_SET", int(clamp(-(250.0 * bank), -4000, 4000)))
    st["th"] = clamp(st["th"] + 500.0 * (IAS0 - ias) * dt, 0.0, 16383.0)
    ev("THROTTLE1_SET", int(st["th"]))
    if not -10 < theta < 20 or abs(bank) > 30 or ias < 160:
        reason = f"ABORT: pitch {theta:.0f}°, bank {bank:.0f}°, IAS {ias:.0f}"
        break
    rho, tas = g("AMBIENT_DENSITY"), g("AIRSPEED_TRUE") * 1.68781
    qd = 0.5 * rho * tas * tas
    w, n = g("TOTAL_WEIGHT"), g("G_FORCE")
    rows.append([round(el, 2), seg, frac, round(alt), round(ias, 1), round(st["vs_f"]), round(theta, 2),
                 round(g("INCIDENCE_ALPHA") * DEG, 2), round(w * n / (qd * 196.1), 4) if qd > 1 else "",
                 round(g("TRAILING_EDGE_FLAPS_LEFT_ANGLE") * DEG, 1), round(g("LEADING_EDGE_FLAPS_LEFT_ANGLE") * DEG, 1),
                 round(g("TURB_ENG_N1:1"), 1), int(cmd), round(g("ELEVATOR_POSITION"), 3), round(n, 3)])
    time.sleep(0.03)

# end: FM clean-up
te(1.0)
ev("AXIS_AILERONS_SET", 0)
ev("THROTTLE1_SET", 11141)
ev("GEAR_UP")
ev("FLAPS_1")
t_e = time.time()
while time.time() - t_e < 90 and g("AIRSPEED_INDICATED") < 265:
    alt = g("PLANE_ALTITUDE") or ALT0
    ev("AXIS_ELEVATOR_SET", int(clamp(150.0 * (g("VERTICAL_SPEED") - clamp(2.0 * (ALT0 - alt), -500, 500)) / 60.0, -6000, 4000)))
    time.sleep(0.1)
ev("FLAPS_UP")
ev("AXIS_ELEVATOR_SET", 0)
ev("THROTTLE1_SET", 9000)
ev("AP_MASTER")
time.sleep(0.3)
if g("AUTOPILOT_MASTER") != 1:
    ev("AP_MASTER")
ev("AP_ALT_VAR_SET_ENGLISH", int(g("PLANE_ALTITUDE")))
ev("AP_ALT_HOLD_ON")
sm.exit()
with open(out, "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["t", "seg", "te_set", "alt", "ias", "vs_fpm", "pitch", "alpha", "cl", "te_deg", "le_deg", "n1", "el_cmd",
                 "elev_pos", "g"])
    wr.writerows(rows)
print(reason)
print("step  TE set  TE°   LE°   α°     CL      IAS   N1    elev   (last 10 s of each step)")
for k, frac in enumerate(STEPS):
    s = [r for r in rows if r[1] == k and r[0] - (SETTLE_S + k * STEP_S) > STEP_S - 10 and r[8] != ""]
    if s:
        m = lambda i: sum(r[i] for r in s) / len(s)
        print(f"{k:3d}  {frac:5.2f}  {m(9):5.1f} {m(10):5.1f} {m(7):6.2f}  {m(8):.4f}  {m(4):5.1f} {m(11):5.1f} {m(13):6.3f}")
print(f"{len(rows)} samples -> {out}")
