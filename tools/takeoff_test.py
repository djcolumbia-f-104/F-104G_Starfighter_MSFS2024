"""Test T3-D: takeoff run, controlled via SimConnect (Claude flies the takeoff per FM 6-5).

Usage (with the Python of the simconnect-mcp venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\takeoff_test.py <output.csv> [vr_kt=157] [theta_target=10.5]
Precondition: aircraft lined up on the runway, engine running, flaps TAKEOFF, trim 5°, parking brake set.
Sequence: full afterburner against the parking brake -> at N1 >= 99 % (max. 12 s) release the brake -> rudder holds
the runway heading -> from vr_kt pull the pitch to theta_target at 3°/s (rotate ~20 kt below liftoff speed, FM 6-5)
-> after liftoff from 30 ft AP in vertical speed mode (+4 000 ft/min), from 50 ft gear up, from 400 ft flaps up,
from 1 500 ft above ground reduced power (throttle 7000) and altitude hold.
Abort (idle + brake) at a heading deviation > 10° on the ground or 90 s without liftoff.
Tail strike guard: on the ground the target pitch is limited to 11° (ground contact at 12.3°, AP-5).
Evaluation: liftoff IAS, ground roll, max. pitch on the ground (printed at the end + CSV).
"""
import csv
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect
from SimConnect.EventList import Event

sys.stdout.reconfigure(encoding="utf-8")
out = sys.argv[1]
vr = float(sys.argv[2]) if len(sys.argv) > 2 else 157.0
theta_target = float(sys.argv[3]) if len(sys.argv) > 3 else 10.5
DEG = 57.29578
FULL = 16383

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)
ev = {n: ae.find(n) for n in ("AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET", "THROTTLE1_SET", "PARKING_BRAKES", "GEAR_UP",
                              "FLAPS_UP", "AP_MASTER", "AP_ALT_VAR_SET_ENGLISH", "AP_ALT_HOLD_ON", "AP_VS_VAR_SET_ENGLISH",
                              "AP_HDG_HOLD_ON", "HEADING_BUG_SET")}
# not in the library's catalog (ae.find -> None, run 5 crashed) -> map directly
ev["AP_PANEL_VS_ON"] = Event(b"AP_PANEL_VS_ON", sm)
missing = [n for n, e in ev.items() if e is None]
if missing:
    sys.exit(f"Events not found: {missing}")


def rad(v):
    return v or 0.0


def state(full=True):
    # During the takeoff run each read waits for the next sim frame (~70 ms) -> only the essentials per loop
    s = {
        "t": time.time(), "ias": aq.get("AIRSPEED_INDICATED") or 0, "gnd": aq.get("SIM_ON_GROUND") == 1,
        "theta": -rad(aq.get("PLANE_PITCH_DEGREES")) * DEG,          # nose up positive
        "hdg": rad(aq.get("PLANE_HEADING_DEGREES_TRUE")) * DEG, "gs": aq.get("GROUND_VELOCITY") or 0, "agl": 0.0,
    }
    if full:
        s["agl"] = aq.get("PLANE_ALT_ABOVE_GROUND") or 0
    return s


def axis(name, v):
    ev[name](int(max(-FULL, min(FULL, v))))


def wrap(d):
    return (d + 180) % 360 - 180


s0 = state()
lat0, lon0 = aq.get("PLANE_LATITUDE"), aq.get("PLANE_LONGITUDE")
print(f"Start position (for msfs_set_aircraft_position): lat {lat0}, lon {lon0}, heading {s0['hdg']:.1f}° true")
if not s0["gnd"]:
    sys.exit("Aircraft is not on the ground - aborted")
# The lever position alone is not enough (run 5: lever TAKEOFF, flaps 0° because hydraulic without a hydraulic system)
flap = rad(aq.get("TRAILING_EDGE_FLAPS_LEFT_ANGLE")) * DEG
print(f"Flaps trailing edge {flap:.1f}°, trim {rad(aq.get('ELEVATOR_TRIM_POSITION')) * DEG:.2f}°")
if not 10 <= flap <= 20:
    sys.exit("Flaps not in TAKEOFF (15°) - aborted")
hdg0 = s0["hdg"]
if aq.get("BRAKE_PARKING_POSITION") != 1:
    ev["PARKING_BRAKES"]()
axis("AXIS_ELEVATOR_SET", 0)
axis("AXIS_RUDDER_SET", 0)
ev["THROTTLE1_SET"](FULL)
t_spool = time.time()
while time.time() - t_spool < 12 and (aq.get("TURB_ENG_N1:1") or 0) < 99:
    time.sleep(0.2)
print(f"N1 {aq.get('TURB_ENG_N1:1') or 0:.1f} % after {time.time() - t_spool:.1f} s -> brake released")
ev["PARKING_BRAKES"]()

# Gains for a ~3 Hz control loop (run 2 with 2500/1500 and 1500/900 oscillated and ended in the ground)
KP_HDG, KD_HDG = 700.0, 400.0            # counts per ° and per °/s (positive axis = nose LEFT, T3-D run 1)
KP_TH, KD_TH = 800.0, 200.0              # counts per ° and per °/s (positive axis = nose down, rounds D/E)
FF_TH = 5000.0                           # feed-forward "pull the stick" (run 3 with 2500: only 6-7° on the ground)
LIM_RUD, LIM_PULL, LIM_PUSH = 8000, 12000, 3000
ap_on = False                            # after liftoff the AP takes over (the pitch loop oscillates in the air at ~3 Hz)
res = {"start": s0, "liftoff": None, "first_air": None, "theta_max_gnd": 0.0, "vr_t": None}
prev = state()
t0 = prev["t"]
theta_cmd = 0.0
gear_up = flaps_up = False
aborted = ""
air_since = None
dist = 0.0
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "ias", "gnd", "theta", "theta_cmd", "hdg_err", "agl", "dist_ft", "gs", "cmd_elev", "cmd_rud"])
    while True:
        s = state(full=not prev["gnd"] or res["liftoff"] is not None)
        dt = max(s["t"] - prev["t"], 0.02)
        err_h = wrap(hdg0 - s["hdg"])
        r = wrap(s["hdg"] - prev["hdg"]) / dt
        q = (s["theta"] - prev["theta"]) / dt
        if s["ias"] >= vr and res["vr_t"] is None:
            res["vr_t"] = s["t"] - t0
        if res["vr_t"] is not None:
            theta_cmd = min(theta_target, theta_cmd + 3.0 * dt)
            if s["gnd"]:
                theta_cmd = min(theta_cmd, 11.0)       # tail touches at 12.3°
        cmd_rud = -(KP_HDG * err_h - KD_HDG * r) if res["liftoff"] is None or s["agl"] < 50 else 0.0
        cmd_rud = max(-LIM_RUD, min(LIM_RUD, cmd_rud))
        cmd_elev = 0.0
        if res["vr_t"] is not None and not ap_on:
            cmd_elev = -(FF_TH + KP_TH * (theta_cmd - s["theta"]) - KD_TH * q)
            cmd_elev = max(-LIM_PULL, min(LIM_PUSH, cmd_elev))
        axis("AXIS_RUDDER_SET", cmd_rud)
        if not ap_on:
            axis("AXIS_ELEVATOR_SET", cmd_elev)
        if res["liftoff"] and s["agl"] > 30 and not ap_on:
            axis("AXIS_ELEVATOR_SET", 0)
            ev["HEADING_BUG_SET"](int(round(hdg0)) % 360)
            # vertical speed mode: AP_ALT_HOLD_ON holds the CURRENT altitude (run 4: pushed back onto the runway)
            ev["AP_ALT_VAR_SET_ENGLISH"](int(aq.get("PLANE_ALTITUDE") or 0) + 3000)
            ev["AP_VS_VAR_SET_ENGLISH"](4000)
            if aq.get("AUTOPILOT_MASTER") != 1:
                ev["AP_MASTER"]()
            ev["AP_PANEL_VS_ON"]()
            ev["AP_HDG_HOLD_ON"]()
            ap_on = True
            print(f"AP takes over at {s['agl']:.0f} ft above ground, {s['ias']:.0f} kt")
        dist += s["gs"] * 1.68781 * dt                      # kt -> ft/s
        s["dist"] = dist
        if s["gnd"]:
            res["theta_max_gnd"] = max(res["theta_max_gnd"], s["theta"])
            air_since = None
        elif air_since is None:
            air_since = s
            if res["first_air"] is None:                # first liftoff (run 5 touched down once more afterwards)
                res["first_air"] = s
                print(f"First liftoff: {s['ias']:.0f} kt, pitch {s['theta']:.1f}°, ground roll {dist:.0f} ft")
        elif res["liftoff"] is None and s["t"] - air_since["t"] > 1.0:
            res["liftoff"] = dict(air_since, tt=air_since["t"] - t0)
            print(f"Liftoff: {air_since['ias']:.0f} kt, pitch {air_since['theta']:.1f}°, "
                  f"ground roll {res['liftoff']['dist']:.0f} ft, {res['liftoff']['tt']:.1f} s")
        if res["liftoff"] and s["agl"] > 50 and not gear_up:
            ev["GEAR_UP"]()
            gear_up = True
        if res["liftoff"] and s["agl"] > 400 and not flaps_up:
            ev["FLAPS_UP"]()
            flaps_up = True
        w.writerow([round(s["t"] - t0, 2), round(s["ias"], 1), int(s["gnd"]), round(s["theta"], 2),
                    round(theta_cmd, 2), round(err_h, 2), round(s["agl"]), round(dist), round(s["gs"], 1),
                    int(cmd_elev), int(cmd_rud)])
        f.flush()
        prev = s
        if res["liftoff"] is None and s["gnd"] and abs(err_h) > 10:
            aborted = f"Abort: heading deviation {err_h:.1f}°"
        elif res["liftoff"] is None and s["t"] - t0 > 90:
            aborted = "Abort: 90 s without liftoff"
        if aborted:
            ev["THROTTLE1_SET"](0)
            ev["PARKING_BRAKES"]()
            break
        if s["agl"] > 1500 or s["t"] - t0 > 150:
            break
        time.sleep(0.05)

for n in ("AXIS_RUDDER_SET", "AXIS_ELEVATOR_SET"):
    axis(n, 0)
if not aborted:
    # reduced power: with military + ALT hold the jet reached 600 KIAS at 3 000 ft (run 6)
    ev["THROTTLE1_SET"](7000)
    ev["HEADING_BUG_SET"](int(round(hdg0)) % 360)
    ev["AP_ALT_VAR_SET_ENGLISH"](int(aq.get("PLANE_ALTITUDE") or 0) + 3000)
    if aq.get("AUTOPILOT_MASTER") != 1:
        ev["AP_MASTER"]()
    ev["AP_ALT_HOLD_ON"]()
    ev["AP_HDG_HOLD_ON"]()
sm.exit()
lo, fa = res["liftoff"], res["first_air"]
print(aborted or "done", "->", out)
print(f"Vr reached after {res['vr_t']} s; max. pitch on the ground {res['theta_max_gnd']:.1f}° (tail at 12.3°)")
if fa:
    print(f"Result: first liftoff at {fa['ias']:.0f} kt IAS, pitch {fa['theta']:.1f}°, after {fa['dist']:.0f} ft")
if lo:
    print(f"Result: sustained liftoff at {lo['ias']:.0f} kt IAS after {lo['dist']:.0f} ft / {lo['tt']:.1f} s")
