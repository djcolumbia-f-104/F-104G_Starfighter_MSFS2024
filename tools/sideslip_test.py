"""Test T3-E2: stationärer Schiebeflug (Steady Heading Sideslip) mit Gegenquerruder, geregelt per SimConnect.

Aufruf (mit dem Python der simconnect-mcp-venv):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\sideslip_test.py <ausgabe.csv> [ruder_s=15] [ruder_anteil=1.0]
Voraussetzung: Flugzeug fliegt ruhig im gewünschten Zustand (z. B. Fahrwerk/Klappen aus, ~250 kt) mit AP Höhenhaltung.
Ablauf: AP aus -> Vorzeichen von Querruder/Höhenruder mit kleinen Prüfausschlägen bestimmen -> Regler halten
Querlage 0 (Querruder) und Steigrate 0 (Höhenruder) -> 5 s ohne Seitenruder -> volles Seitenruder ruder_s Sekunden
-> 5 s ohne -> Achsen frei, AP wieder an. Abbruch bei |Querlage| > 45° oder > 1 500 ft Höhenverlust.
Auswertung: Querruderausschlag (AILERON_AVERAGE_DEFLECTION) bei vollem Seitenruder vs. Clβ·β/Clδa (CR-2144).
"""
import csv
import math
import sys
import time

from SimConnect import AircraftEvents, AircraftRequests, SimConnect

sys.stdout.reconfigure(encoding="utf-8")
out = sys.argv[1]
rudder_s = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0
rudder_frac = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
DEG = 57.29578
FULL = 16383

sm = SimConnect()
aq = AircraftRequests(sm, _time=0)
ae = AircraftEvents(sm)
ev = {n: ae.find(n) for n in ("AXIS_AILERONS_SET", "AXIS_ELEVATOR_SET", "AXIS_RUDDER_SET", "AUTOPILOT_OFF", "AP_MASTER",
                              "AP_ALT_HOLD_ON", "AP_WING_LEVELER_ON")}


def state():
    return {
        "t": time.time(), "bank": (aq.get("PLANE_BANK_DEGREES") or 0) * DEG, "alt": aq.get("PLANE_ALTITUDE") or 0,
        "pitch": (aq.get("PLANE_PITCH_DEGREES") or 0) * DEG, "beta": (aq.get("INCIDENCE_BETA") or 0) * DEG,
        "ias": aq.get("AIRSPEED_INDICATED") or 0, "rud": (aq.get("RUDDER_DEFLECTION") or 0) * DEG,
        "ail": (aq.get("AILERON_LEFT_DEFLECTION") or 0) * DEG, "elev": (aq.get("ELEVATOR_DEFLECTION") or 0) * DEG,
    }


def axis(name, v):
    ev[name](int(max(-FULL, min(FULL, v))))


def probe(name, key, amount, dur):
    """Kleiner Prüfausschlag; liefert das Vorzeichen der Wirkung auf state[key] (+1/-1)."""
    s0 = state()
    axis(name, amount)
    time.sleep(dur)
    s1 = state()
    axis(name, 0)
    time.sleep(dur)
    d = s1[key] - s0[key]
    print(f"Prüfausschlag {name} {amount:+d}: Δ{key} = {d:+.2f}")
    return 1 if d > 0 else -1


start = state()
ap_on = aq.get("AUTOPILOT_MASTER") == 1
if ap_on:
    ev["AUTOPILOT_OFF"]()
time.sleep(0.5)
# Vorzeichen: positiver Achswert -> Querlage +/-, Nicklage +/- (PLANE_PITCH_DEGREES: Nase hoch = negativ)
s_ail = probe("AXIS_AILERONS_SET", "bank", 4000, 0.6)
s_elev = probe("AXIS_ELEVATOR_SET", "pitch", 3000, 0.5)
start = state()

KP_BANK, KD_BANK = 400.0, 250.0          # Zählwerte je ° bzw. °/s
KI_BANK = 150.0                          # Zählwerte je °·s (Runde D ohne I-Anteil: 14° bleibende Querlage)
integ_bank = 0.0
KP_VS, KI_VS = 120.0, 40.0               # Zählwerte je ft/s bzw. ft
phases = [(5.0, 0.0), (rudder_s, rudder_frac * FULL), (5.0, 0.0)]
prev = state()
alt_ref = prev["alt"]
integ = 0.0
aborted = ""
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t", "phase", "ias", "alt", "bank", "beta", "rud", "ail", "elev", "cmd_ail", "cmd_elev", "cmd_rud"])
    t0 = time.time()
    for k, (dur, rud) in enumerate(phases):
        axis("AXIS_RUDDER_SET", rud)
        tend = time.time() + dur
        while time.time() < tend:
            s = state()
            dt = max(s["t"] - prev["t"], 0.02)
            p = (s["bank"] - prev["bank"]) / dt
            vs = (s["alt"] - prev["alt"]) / dt
            integ = max(-200.0, min(200.0, integ + (s["alt"] - alt_ref) * dt))
            # Gegenkopplung: Querruder gegen Querlage und Rollrate, Höhenruder gegen Steigrate und Höhenabweichung
            integ_bank = max(-30.0, min(30.0, integ_bank + s["bank"] * dt))
            cmd_ail = -s_ail * (KP_BANK * s["bank"] + KD_BANK * p + KI_BANK * integ_bank)
            cmd_elev = s_elev * (KP_VS * vs + KI_VS * integ / 10.0)   # Nase hoch = Nicklage negativ -> s_elev
            axis("AXIS_AILERONS_SET", cmd_ail)
            axis("AXIS_ELEVATOR_SET", cmd_elev)
            w.writerow([round(s["t"] - t0, 2), k, round(s["ias"], 1), round(s["alt"]), round(s["bank"], 2),
                        round(s["beta"], 2), round(s["rud"], 2), round(s["ail"], 2), round(s["elev"], 2),
                        int(cmd_ail), int(cmd_elev), int(rud)])
            f.flush()
            prev = s
            if abs(s["bank"]) > 45 or s["alt"] < start["alt"] - 1500:
                aborted = f"Abbruch: Querlage {s['bank']:.0f}°, Höhe {s['alt']:.0f} ft"
                break
            time.sleep(0.05)
        if aborted:
            break
for n in ("AXIS_RUDDER_SET", "AXIS_AILERONS_SET", "AXIS_ELEVATOR_SET"):
    axis(n, 0)
ev["AP_MASTER"]()
ev["AP_ALT_HOLD_ON"]()
ev["AP_WING_LEVELER_ON"]()
sm.exit()
print(aborted or "fertig", "->", out)
