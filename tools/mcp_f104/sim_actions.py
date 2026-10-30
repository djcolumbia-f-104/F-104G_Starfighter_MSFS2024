"""Small sim actions for the project MCP server (run as a subprocess with the simconnect-mcp venv Python).

Usage: sim_actions.py state
       sim_actions.py position <alt_ft> <tas_kt> <heading> <lat> <lon> <throttle> <lateral: wl|hdg>
       sim_actions.py runway
       sim_actions.py accel <csv> <mach_stop> <max_s>
Each command prints a compact result (a few lines). One SimConnect connection per call, closed at the end.
"""
import subprocess
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

DEG = 57.29578
RUNWAY = (48.34472097713059, 11.803858844132039, 263.4)       # EDDM 26L, T3-D start position
ROOT = __file__.rsplit("tools", 1)[0]
SIMPY = sys.executable

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)


def ev(name, *arg):
    e = ae.find(name) or Event(name.encode(), sm)
    e(*arg)


def g(name):
    return aq.get(name)


def state():
    return {
        "alt_ft": round(g("PLANE_ALTITUDE") or 0), "agl_ft": round(g("PLANE_ALT_ABOVE_GROUND") or 0),
        "ias_kt": round(g("AIRSPEED_INDICATED") or 0), "mach": round(g("AIRSPEED_MACH") or 0, 3),
        "pitch_deg": round(-(g("PLANE_PITCH_DEGREES") or 0) * DEG, 1), "bank_deg": round((g("PLANE_BANK_DEGREES") or 0) * DEG, 1),
        "on_ground": int(g("SIM_ON_GROUND") or 0), "ap": int(g("AUTOPILOT_MASTER") or 0),
        "yaw_damper": int(g("AUTOPILOT_YAW_DAMPER") or 0), "n1": round(g("TURB_ENG_N1:1") or 0, 1),
        "throttle_pct": round(g("GENERAL_ENG_THROTTLE_LEVER_POSITION:1") or 0), "weight_lb": round(g("TOTAL_WEIGHT") or 0),
        "fuel_lb": round(g("FUEL_TOTAL_QUANTITY_WEIGHT") or 0), "gear_pct": g("GEAR_TOTAL_PCT_EXTENDED"),
        "flaps_deg": round((g("TRAILING_EDGE_FLAPS_LEFT_ANGLE") or 0) * DEG, 1),
        "trim_deg": round((g("ELEVATOR_TRIM_POSITION") or 0) * DEG, 2), "oat_c": round(g("AMBIENT_TEMPERATURE") or 0, 1),
    }


def ap_on():
    """AP_MASTER is a toggle: read first, toggle, verify (a failed toggle let the jet dive on 2026-10-26)."""
    for _ in range(3):
        if g("AUTOPILOT_MASTER") == 1:
            return True
        ev("AP_MASTER")
        time.sleep(0.7)
    return g("AUTOPILOT_MASTER") == 1


cmd = sys.argv[1]
if cmd == "state":
    print(state())

elif cmd == "position":
    alt, tas, hdg, lat, lon, thr = (float(v) for v in sys.argv[2:8])
    lateral = sys.argv[8] if len(sys.argv) > 8 else "wl"
    ok = ap_on()
    ev("AP_ALT_VAR_SET_ENGLISH", int(alt))
    ev("HEADING_BUG_SET", int(hdg) % 360)
    ev("AP_ALT_HOLD_ON")
    ev("AP_WING_LEVELER_ON" if lateral == "wl" else "AP_HDG_HOLD_ON")
    sm.set_pos(alt, lat, lon, int(tas), 0.0, 0.0, hdg, 0)          # Airspeed must be an int
    ev("GEAR_UP")
    ev("FLAPS_UP")
    ev("THROTTLE1_SET", int(thr))
    time.sleep(1.0)
    ok = ap_on() and ok
    ev("AP_ALT_HOLD_ON")
    lowest = alt
    t0 = time.time()
    while time.time() - t0 < 25:                       # AP needs ~15-20 s to pull out after positioning (α = 0)
        a = g("PLANE_ALTITUDE") or 0
        lowest = min(lowest, a)
        if not g("AUTOPILOT_MASTER"):
            ap_on()
        if not g("AUTOPILOT_ALTITUDE_LOCK"):               # 2026-10-26: ALT hold was off once -> dived 5 000 ft
            ev("AP_ALT_VAR_SET_ENGLISH", int(alt))
            ev("AP_ALT_HOLD_ON")
        time.sleep(1)
    s = state()
    print(f"positioned; AP {'on' if s['ap'] else 'OFF!'} (first check {'ok' if ok else 'needed retries'}); "
          f"sank to {lowest:.0f} ft; now {s}")

elif cmd == "runway":
    ev("THROTTLE1_SET", 0)
    if g("AUTOPILOT_MASTER") == 1:
        ev("AP_MASTER")
    sm.set_pos(0, RUNWAY[0], RUNWAY[1], 0, 0.0, 0.0, RUNWAY[2], 1)
    ev("GEAR_DOWN")
    ev("FLAPS_1")
    ev("ELEVATOR_TRIM_SET", 7447)                         # 5° nose up (16383 = 11°)
    if g("BRAKE_PARKING_POSITION") != 1:
        ev("PARKING_BRAKES")
    time.sleep(6)                                         # flaps extending (5 s)
    print(f"on runway EDDM 26L; {state()}")

elif cmd == "approach":
    # T3-L: decelerate (idle + speed brakes), gear down < 255 KIAS, LAND flaps < 230 KIAS (FM: 240-210), then hold the
    # target IAS with a throttle P-loop for hold_s while logging. Run at a safe altitude (AP ALT hold).
    csv_path, target, hold_s = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    ev("THROTTLE1_SET", 0)
    ev("SPOILERS_ON")
    t0 = time.time()
    while time.time() - t0 < 180:
        ias = g("AIRSPEED_INDICATED") or 0
        if ias < 255 and g("GEAR_HANDLE_POSITION") != 1:
            ev("GEAR_DOWN")
        if ias < 230:
            ev("FLAPS_DOWN")
            ev("SPOILERS_OFF")
            break
        time.sleep(1)
    log = subprocess.Popen([SIMPY, "-I", ROOT + "tools/simlog.py", csv_path, str(hold_s + 40), "3"],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    thr = 9000.0
    t1 = time.time()
    while time.time() - t1 < hold_s + 35:
        err = target - (g("AIRSPEED_INDICATED") or 0)
        thr = max(0.0, min(11141.0, thr + 60.0 * err))          # integrating P-loop on the throttle, no afterburner
        ev("THROTTLE1_SET", int(thr))
        if (g("PLANE_ALT_ABOVE_GROUND") or 0) < 3000:
            ev("FLAPS_UP")
            ev("THROTTLE1_SET", 16383)
            print("ABORT: below 3 000 ft AGL")
            break
        time.sleep(1)
    s = state()
    log.wait()
    print(f"approach config held at target {target} KIAS for {hold_s} s (+35 s settling); end {s}; "
          f"throttle cmd {thr:.0f}; log {csv_path}")

elif cmd == "accel":
    csv_path, mach_stop, max_s = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    log = subprocess.Popen([SIMPY, "-I", ROOT + "tools/simlog.py", csv_path, str(max_s + 20), "3"],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    time.sleep(3)
    s0 = state()
    ev("THROTTLE1_SET", 16383)
    t0 = time.time()
    trail = []
    hits = 0
    while time.time() - t0 < max_s:
        m = g("AIRSPEED_MACH") or 0
        if not trail or time.time() - trail[-1][0] > 20:
            trail.append((time.time(), round(m, 2), round(g("PLANE_ALTITUDE") or 0),
                          round((g("ELEVATOR_TRIM_POSITION") or 0) * DEG, 1)))
        # FM limit 750 KEAS (Fig. 6-6, M 2.0 / 750 KEAS). NOT the sim's AIRSPEED_INDICATED: MSFS computes it
        # isentropically without the normal shock ahead of the pitot (2026-10-30: 740 "KIAS" at M 1.77 / 33 000 ft,
        # Rayleigh pitot gives ≈ 680 KCAS, EAS ≈ 604) -> stop on EAS = TAS x sqrt(rho / rho0)
        eas = (g("AIRSPEED_TRUE") or 0) * ((g("AMBIENT_DENSITY") or 0) / 0.0023769) ** 0.5
        hit = m >= mach_stop or eas > 740
        # stop must hold on two consecutive reads (failed reads)
        hits = hits + 1 if hit else 0
        if hits >= 2:
            break
        time.sleep(1)
    ev("THROTTLE1_SET", 0)
    dur = time.time() - t0
    s1 = state()
    log.wait()
    print(f"accel {s0['mach']} -> {s1['mach']} in {dur:.0f} s (stop at M {mach_stop} / 740 KEAS); "
          f"alt {s0['alt_ft']} -> {s1['alt_ft']}; OAT {s0['oat_c']} °C; weight {s0['weight_lb']}; fuel left {s1['fuel_lb']}")
    print("trail (Mach, alt, trim°):", [(m, a, tr) for _, m, a, tr in trail])
    print("log:", csv_path)

sm.exit()
