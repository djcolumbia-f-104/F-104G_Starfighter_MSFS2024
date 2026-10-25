"""Test T3-D: Startlauf, geregelt per SimConnect (Claude fliegt den Start nach FM 6-5).

Aufruf (mit dem Python der simconnect-mcp-venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\takeoff_test.py <ausgabe.csv> [vr_kt=157] [theta_ziel=10.5]
Voraussetzung: Flugzeug steht auf der Startbahn ausgerichtet, Triebwerk läuft, Klappen TAKEOFF, Trimmung 5°,
Parkbremse gesetzt.
Ablauf: volle Nachbrennerleistung gegen die Parkbremse -> bei N1 >= 99 % (max. 10 s) Bremse lösen -> Seitenruder hält
den Startkurs -> ab vr_kt Nicklage mit 3°/s auf theta_ziel ziehen (Rotieren ~20 kt unter Abhebegeschwindigkeit,
FM 6-5) -> nach dem Abheben ab 30 ft AP im Steigratenmodus (+4 000 ft/min), ab 50 ft Fahrwerk ein, ab 400 ft Klappen
ein, ab 1 500 ft über Grund Military und Höhenhaltung.
Abbruch (Leerlauf + Bremse) bei Kursabweichung > 10° am Boden oder 90 s ohne Abheben.
Heckaufsetzer-Wächter: am Boden wird die Ziel-Nicklage auf 11° begrenzt (Bodenberührung bei 12,3°, AP-5).
Auswertung: Abhebe-IAS, Rollstrecke, max. Nicklage am Boden (Ausgabe am Ende + CSV).
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
# nicht im Katalog der Bibliothek (ae.find -> None, Lauf 5 brach ab) -> direkt abbilden
ev["AP_PANEL_VS_ON"] = Event(b"AP_PANEL_VS_ON", sm)
missing = [n for n, e in ev.items() if e is None]
if missing:
    sys.exit(f"Events nicht gefunden: {missing}")


def rad(v):
    return v or 0.0


def state(full=True):
    # Jede Abfrage wartet im Startlauf auf den nächsten Sim-Frame (~70 ms) -> nur das Nötigste je Durchlauf
    s = {
        "t": time.time(), "ias": aq.get("AIRSPEED_INDICATED") or 0, "gnd": aq.get("SIM_ON_GROUND") == 1,
        "theta": -rad(aq.get("PLANE_PITCH_DEGREES")) * DEG,          # Nase hoch positiv
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
print(f"Startposition (für msfs_set_aircraft_position): lat {lat0}, lon {lon0}, Kurs {s0['hdg']:.1f}° rw")
if not s0["gnd"]:
    sys.exit("Flugzeug ist nicht am Boden - abgebrochen")
# Hebelstellung allein genügt nicht (Lauf 5: Hebel TAKEOFF, Klappen 0°, weil hydraulisch ohne Hydrauliksystem)
flap = rad(aq.get("TRAILING_EDGE_FLAPS_LEFT_ANGLE")) * DEG
print(f"Klappen Hinterkante {flap:.1f}°, Trimmung {rad(aq.get('ELEVATOR_TRIM_POSITION')) * DEG:.2f}°")
if not 10 <= flap <= 20:
    sys.exit("Klappen nicht in TAKEOFF (15°) - abgebrochen")
hdg0 = s0["hdg"]
if aq.get("BRAKE_PARKING_POSITION") != 1:
    ev["PARKING_BRAKES"]()
axis("AXIS_ELEVATOR_SET", 0)
axis("AXIS_RUDDER_SET", 0)
ev["THROTTLE1_SET"](FULL)
t_spool = time.time()
while time.time() - t_spool < 12 and (aq.get("TURB_ENG_N1:1") or 0) < 99:
    time.sleep(0.2)
print(f"N1 {aq.get('TURB_ENG_N1:1') or 0:.1f} % nach {time.time() - t_spool:.1f} s -> Bremse lösen")
ev["PARKING_BRAKES"]()

# Verstärkungen für ~3 Hz Regeltakt (Lauf 2 mit 2500/1500 bzw. 1500/900 schwang auf und endete im Boden)
KP_HDG, KD_HDG = 700.0, 400.0            # Zählwerte je ° bzw. °/s (positive Achse = Nase LINKS, T3-D Lauf 1)
KP_TH, KD_TH = 800.0, 200.0              # Zählwerte je ° bzw. °/s (positive Achse = Nase runter, Runde D/E)
FF_TH = 5000.0                           # Vorhalt "Knüppel ziehen" (Lauf 3 mit 2500: nur 6-7° am Boden)
LIM_RUD, LIM_PULL, LIM_PUSH = 8000, 12000, 3000
ap_on = False                            # nach dem Abheben übernimmt der AP (Nickregler schwingt in der Luft bei ~3 Hz)
res = {"start": s0, "liftoff": None, "theta_max_gnd": 0.0, "vr_t": None}
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
                theta_cmd = min(theta_cmd, 11.0)       # Heck setzt bei 12,3° auf
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
            # Steigratenmodus: AP_ALT_HOLD_ON hält die AKTUELLE Höhe (Lauf 4: zurück auf die Bahn gedrückt)
            ev["AP_ALT_VAR_SET_ENGLISH"](int(aq.get("PLANE_ALTITUDE") or 0) + 3000)
            ev["AP_VS_VAR_SET_ENGLISH"](4000)
            if aq.get("AUTOPILOT_MASTER") != 1:
                ev["AP_MASTER"]()
            ev["AP_PANEL_VS_ON"]()
            ev["AP_HDG_HOLD_ON"]()
            ap_on = True
            print(f"AP übernimmt bei {s['agl']:.0f} ft über Grund, {s['ias']:.0f} kt")
        dist += s["gs"] * 1.68781 * dt                      # kt -> ft/s
        s["dist"] = dist
        if s["gnd"]:
            res["theta_max_gnd"] = max(res["theta_max_gnd"], s["theta"])
            air_since = None
        elif air_since is None:
            air_since = s
            if res.get("first_air") is None:            # erstes Abheben (Lauf 5 setzte danach noch einmal auf)
                res["first_air"] = s
                print(f"Erstes Abheben: {s['ias']:.0f} kt, Nicklage {s['theta']:.1f}°, Rollstrecke {dist:.0f} ft")
        elif res["liftoff"] is None and s["t"] - air_since["t"] > 1.0:
            res["liftoff"] = dict(air_since, tt=air_since["t"] - t0)
            print(f"Abheben: {air_since['ias']:.0f} kt, Nicklage {air_since['theta']:.1f}°, "
                  f"Rollstrecke {res['liftoff']['dist']:.0f} ft, {res['liftoff']['tt']:.1f} s")
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
            aborted = f"Abbruch: Kursabweichung {err_h:.1f}°"
        elif res["liftoff"] is None and s["t"] - t0 > 90:
            aborted = "Abbruch: 90 s ohne Abheben"
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
    ev["THROTTLE1_SET"](11141)
    ev["HEADING_BUG_SET"](int(round(hdg0)) % 360)
    ev["AP_ALT_VAR_SET_ENGLISH"](int(aq.get("PLANE_ALTITUDE") or 0) + 3000)
    if aq.get("AUTOPILOT_MASTER") != 1:
        ev["AP_MASTER"]()
    ev["AP_ALT_HOLD_ON"]()
    ev["AP_HDG_HOLD_ON"]()
sm.exit()
lo = res["liftoff"]
print(aborted or "fertig", "->", out)
print(f"Vr erreicht nach {res['vr_t']} s; max. Nicklage am Boden {res['theta_max_gnd']:.1f}° (Heck bei 12,3°)")
if lo:
    print(f"Ergebnis: Abheben bei {lo['ias']:.0f} kt IAS nach {lo['dist']:.0f} ft / {lo['tt']:.1f} s")
