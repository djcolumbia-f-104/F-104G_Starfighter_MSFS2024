"""Project MCP server "f104": the F-104G test loop as compact tools (saves tokens: only key figures are returned).

Runs with the simconnect-mcp venv Python (has mcp + SimConnect). Registered in the project's .mcp.json.
Every sim action runs as a subprocess with its own short SimConnect connection, so the server never holds a stale
connection after a sim restart. Scripts: tools/*.py (tests, analyses), tools/mcp_f104/sim_actions.py (actions).
"""
import datetime
import os
import re
import subprocess
import sys
import time

from mcp.server.fastmcp import FastMCP

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SIMPY = sys.executable                                            # simconnect-mcp venv
TOOLPY = os.path.join(ROOT, "tools", ".venv", "Scripts", "python.exe")
DATA = os.path.join(ROOT, "docs", "data")
mcp = FastMCP("f104")


def run(py, script, *args, timeout=600):
    p = subprocess.run([py, "-I", os.path.join(ROOT, script), *map(str, args)], cwd=ROOT, capture_output=True,
                       stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    out = (p.stdout or "") + (("\nSTDERR: " + p.stderr[-1500:]) if p.returncode and p.stderr else "")
    return p.returncode, out


def csv_path(name):
    """Short name -> docs/data/flighttest_<date>_<name>.csv"""
    if name.endswith(".csv") or os.sep in name or "/" in name:
        return os.path.join(ROOT, name)
    return os.path.join(DATA, f"flighttest_{datetime.date.today():%Y-%m-%d}_{name}.csv")


def pick(text, pattern, last=40):
    lines = [l for l in text.splitlines() if re.search(pattern, l)]
    return "\n".join(lines[-last:]) or text[-1500:]


@mcp.tool()
def check_build() -> str:
    """T0/T1: cfg rules and build state. Returns only failed checks and the summary line."""
    rc, out = run(TOOLPY, "tools/check_cfg.py", ".")
    return pick(out, r"^(ERROR|WARNING)|checks,")


@mcp.tool()
def build_cfg() -> str:
    """Regenerate common/config/*.cfg from source/cfg (run after editing source/cfg; then the user does Build All)."""
    p = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", os.path.join(ROOT, "tools", "build_cfg.ps1")],
                       cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, text=True, timeout=120)
    return (p.stdout or "")[-300:] + check_build()


@mcp.tool()
def preflight() -> str:
    """T2 in the running sim: test bed loaded, engine, fuel selector, flaps/gear/trim state (compact)."""
    rc, out = run(SIMPY, "tools/preflight.py", timeout=60)
    keep = r"FAIL|OK|Weight|Fuel lb|CG|Flaps trailing|Gear extended|Trim|Autopilot|On ground"
    return ("ALL OK\n" if rc == 0 else "PREFLIGHT FAILED\n") + pick(out, keep)


@mcp.tool()
def sim_state() -> str:
    """Compact snapshot: altitude, IAS, Mach, attitude, AP/yaw damper, N1, throttle, weight, fuel, gear, flaps, trim, OAT."""
    return run(SIMPY, "tools/mcp_f104/sim_actions.py", "state", timeout=60)[1].strip()


@mcp.tool()
def position(altitude_ft: float = 16500, tas_kt: float = 520, heading: float = 270, lat: float = 48.25,
             lon: float = 11.0, throttle: int = 8000, lateral: str = "wl") -> str:
    """Reposition in the air with AP ALT hold (+ wing leveler 'wl' or heading 'hdg'), gear/flaps up; verifies the AP
    (toggle event!) before and after, waits 25 s for the pull-out and reports the lowest altitude.
    tas_kt is TRUE airspeed (520 at 16 500 ft ≈ 420 KIAS). Throttle 0..16383 (11141 = military)."""
    return run(SIMPY, "tools/mcp_f104/sim_actions.py", "position", altitude_ft, tas_kt, heading, lat, lon, throttle,
               lateral, timeout=90)[1].strip()


@mcp.tool()
def runway_start() -> str:
    """Put the jet on EDDM runway 26L (T3-D start position): engine idle, AP off, gear down, flaps TAKEOFF, trim 5°,
    parking brake set. Check the returned flaps_deg (15) before a takeoff."""
    return run(SIMPY, "tools/mcp_f104/sim_actions.py", "runway", timeout=60)[1].strip()


@mcp.tool()
def takeoff(name: str = "T3D_takeoff", vr_kt: float = 157, theta_deg: float = 10.5) -> str:
    """T3-D scripted takeoff (tools/takeoff_test.py) from the runway; returns liftoff speed, pitch, ground roll.
    Compare with FM Fig. A2-3: liftoff ≈ 155 + 4.43 kt per 1 000 lb above 14 000 lb."""
    rc, out = run(SIMPY, "tools/takeoff_test.py", csv_path(name), vr_kt, theta_deg, timeout=240)
    return pick(out, r"Flaps|liftoff|Liftoff|Abort|Result|Vr|STDERR|takes over")


@mcp.tool()
def doublet(name: str = "doublet", seconds: int = 30) -> str:
    """T3-J rudder doublet (tools/doublet_test.py, 7 Hz): Dutch roll period and amplitude ratio per cycle.
    Target CR-2144 F/C 4 (15 000 ft, M 0.9): 1.41 s, 0.43/cycle. Fly position() first (AP ALT + wing leveler)."""
    rc, out = run(SIMPY, "tools/doublet_test.py", csv_path(name), seconds, timeout=seconds + 60)
    return pick(out, r"period|samples|STDERR|peak", last=6)


@mcp.tool()
def sideslip(name: str = "sideslip", rudder_s: float = 15) -> str:
    """T3-E/E2 closed-loop steady sideslip (tools/sideslip_test.py): returns β/δr and δa/δr (second half of the
    full-rudder phase). Targets CR-2144 Table III-9: β/δr 0.32-0.42, δa/δr 0.27-0.47."""
    path = csv_path(name)
    rc, out = run(SIMPY, "tools/sideslip_test.py", path, rudder_s, 1.0, timeout=rudder_s + 90)
    import csv
    try:
        rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["phase"] == "1"]
        late = rows[len(rows) // 2:]
        m = {k: sum(float(r[k]) for r in late) / len(late) for k in ("ias", "bank", "beta", "rud", "ail")}
        return (f"{out.strip().splitlines()[-1]}\nfull rudder: IAS {m['ias']:.0f} kt, β {m['beta']:.2f}°, rudder "
                f"{m['rud']:.2f}°, aileron {m['ail']:.2f}°, bank {m['bank']:.1f}° -> β/δr {abs(m['beta'] / m['rud']):.2f}, "
                f"δa/δr {abs(m['ail'] / m['rud']):.2f}")
    except Exception as e:                                         # aborted run: show the script output
        return f"{out[-800:]}\n(evaluation failed: {e})"


@mcp.tool()
def approach(name: str = "T3L_approach", target_ias: float = 200, hold_s: int = 45) -> str:
    """T3-L approach configuration: idle + speed brakes, gear down < 255 KIAS, LAND flaps < 230 KIAS, then hold
    target_ias with a throttle loop (no AB) while logging. Fly position() at a safe altitude first (aborts below
    3 000 ft AGL). FM final approach: 170 KIAS up to 15 000 lb, +5 kt per 1 000 lb (Fig. A8-2)."""
    return run(SIMPY, "tools/mcp_f104/sim_actions.py", "approach", csv_path(name), target_ias, hold_s,
               timeout=hold_s + 300)[1].strip()


@mcp.tool()
def landing(name: str = "T3L_landing", start_nm: float = 6, glide_deg: float = 3) -> str:
    """T3-L scripted approach and landing on EDDM 26L (tools/landing_test.py): repositions start_nm out on the glide
    path with gear + LAND flaps, AP HDG (localizer from cross-track) + AP VS (glide path) + throttle loop on the FM
    final approach speed, flare, touchdown, brakes. Returns touchdown IAS/sink/position and ground roll.
    FM ground roll at 17 900 lb, 1 500 ft field, 12 °C, no wind: 3 130 ft without chute (Fig. A8-4), 2 760 ft with the
    18-ft chute (Fig. A8-3); +5 kt headwind ≈ -4 %. The chute is the ground spoiler drag (speed brake handle)."""
    rc, out = run(SIMPY, "tools/landing_test.py", csv_path(name), start_nm, glide_deg, timeout=700)
    return pick(out, r"weight|flare|TOUCHDOWN|GO-AROUND|Result|samples|STDERR")


@mcp.tool()
def accel_run(name: str = "accel", mach_stop: float = 1.2, max_s: int = 240) -> str:
    """Level full-afterburner acceleration with logging (simlog 3 Hz, ~1 Hz real) until mach_stop, 740 KIAS or
    max_s; throttle to idle at the end. Use for T3-H/T3-I/T3-F; then analyse('climb'|'drag', name)."""
    return run(SIMPY, "tools/mcp_f104/sim_actions.py", "accel", csv_path(name), mach_stop, max_s,
               timeout=max_s + 120)[1].strip()


@mcp.tool()
def log(name: str, seconds: int = 60) -> str:
    """Start the flight data logger (tools/simlog.py) in the background for `seconds`; returns the CSV path at once."""
    path = csv_path(name)
    subprocess.Popen([SIMPY, "-I", os.path.join(ROOT, "tools", "simlog.py"), path, str(seconds), "3"], cwd=ROOT,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"logging {seconds} s -> {path}"


@mcp.tool()
def analyse(kind: str, name: str, t_from: float = 0, t_to: float = 1e9) -> str:
    """Evaluate a log: kind 'lift' (T3-A/T3-G), 'drag' (T3-F, speed brake ΔCD), 'climb' (T3-H excess thrust vs.
    D-6398). Returns band means and verdicts only."""
    script = {"lift": "tools/analyse_lift.py", "drag": "tools/analyse_drag.py", "climb": "tools/analyse_climb.py"}[kind]
    args = [".", csv_path(name)] + ([t_from, t_to] if kind == "drag" else [])
    rc, out = run(TOOLPY, script, *args, timeout=120)
    return pick(out, r"T3-|^M |Band|ft  M|Speed brakes|mean|STDERR")


@mcp.tool()
def sim_event(name: str, value: int | None = None) -> str:
    """Send one SimConnect event (e.g. THROTTLE1_SET 11141, SPOILERS_ON, YAW_DAMPER_OFF). Toggle events switch blindly."""
    code = ("import sys\nfrom SimConnect import SimConnect, AircraftEvents\nfrom SimConnect.EventList import Event\n"
            "sm = SimConnect(); ae = AircraftEvents(sm)\n"
            f"e = ae.find({name!r}) or Event({name!r}.encode(), sm)\n"
            f"e({'' if value is None else int(value)})\nsm.exit()\nprint('sent')")
    p = subprocess.run([SIMPY, "-I", "-c", code], capture_output=True, stdin=subprocess.DEVNULL, text=True, timeout=30)
    return (p.stdout + p.stderr[-300:]).strip()


@mcp.tool()
def restart_sim(wait_s: int = 600) -> str:
    """Quit MSFS 2024 and start it again via Steam, then wait until SimConnect answers (main menu).
    The user still has to start the flight (world map -> EDDM runway, F-104G Pruefstand) unless loading works.
    Note: lateral cfg changes only need Build All + aircraft reload; lift (normalization) needs a full restart."""
    subprocess.run(["taskkill", "/IM", "FlightSimulator2024.exe", "/F"], capture_output=True, stdin=subprocess.DEVNULL)
    time.sleep(10)
    os.startfile("steam://rungameid/2537590")
    t0 = time.time()
    while time.time() - t0 < wait_s:
        time.sleep(15)
        p = subprocess.run([SIMPY, "-I", "-c", "from SimConnect import SimConnect; SimConnect().exit(); print('up')"],
                           capture_output=True, stdin=subprocess.DEVNULL, text=True, timeout=60)
        if "up" in p.stdout:
            return f"sim restarted, SimConnect answers after {time.time() - t0:.0f} s - user: start the flight"
    return f"sim started but SimConnect did not answer within {wait_s} s"


if __name__ == "__main__":
    mcp.run()
