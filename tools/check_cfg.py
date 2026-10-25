"""Checks the generated cfg files and the build state (test levels T0 and T1, see docs/flight-model-plan.md).

Usage: check_cfg.py <project folder>     (with tools\\.venv; after build_cfg.ps1 or after Build All in the sim)
Each rule carries the number of its work package (AP-x). ERROR = target not reached yet, WARNING = check it.
Exit code 1 if at least one ERROR occurs.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = sys.argv[1]
CFG = os.path.join(root, "PackageSources", "SimObjects", "Airplanes", "pete-f104g", "common", "config")
PKG = os.path.join(root, "Packages", "pete-aircraft-f104g", "SimObjects", "Airplanes", "pete-f104g", "common", "config")
LOG = os.path.join(os.environ.get("APPDATA", ""), "Microsoft Flight Simulator 2024", "BuilderLogError.txt")


def load(path):
    """-> {section: {key: value}} (lower case, comments removed)"""
    data, sec = {}, None
    for line in open(path, encoding="utf-8-sig"):
        line = line.split(";", 1)[0].strip()
        m = re.match(r"^\[([^\]]+)\]", line)
        if m:
            sec = data.setdefault(m.group(1).strip().lower(), {})
        elif "=" in line and sec is not None:
            k, v = line.split("=", 1)
            sec[k.strip().lower()] = v.strip()
    return data


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def curve(v):
    """1D curve 'x:y, x:y' -> [(x, y)] or None on a format error"""
    try:
        return [tuple(float(t) for t in p.split(":")) for p in v.split(",")]
    except (AttributeError, ValueError):
        return None


results = []


def check(ap, text, ok, level="ERROR", info=""):
    results.append(("OK" if ok else level, ap, text, info))


fm = load(os.path.join(CFG, "flight_model.cfg"))
eng = load(os.path.join(CFG, "engines.cfg"))
geo, aero, tune = fm.get("airplane_geometry", {}), fm.get("aerodynamics", {}), fm.get("flight_tuning", {})

# --- T0: rules from the SDK reference/tutorials and sources ---
check("AP-1", "modern_fm_only = 1 (otherwise the flight model depends on the sim options)",
      num(tune.get("modern_fm_only")) == 1, info=f"is {tune.get('modern_fm_only')}")
check("AP-1", "lift_coef_at_drag_zero set (mandatory per SDK; D-7137 polar -> 0)",
      "lift_coef_at_drag_zero" in aero, info=f"is {aero.get('lift_coef_at_drag_zero')}")
check("AP-1", "wing_camber != 0 (per tutorial 'Fine Tuning' 0 is silently replaced by 1)",
      num(geo.get("wing_camber")) not in (None, 0), info=f"is {geo.get('wing_camber')}")
check("AP-1", "aero_center_lift = 0 (25 % MAC = datum = model origin)",
      num(aero.get("aero_center_lift")) == 0 and num(aero.get("compute_aero_center")) == 0,
      info=f"is {aero.get('aero_center_lift')}")
legacy = {k: num(aero.get(k)) for k in ("lift_coef_delta_elevator", "lift_coef_horizontal_incidence",
                                        "lift_coef_pitch_rate", "lift_coef_daoa")}
check("AP-1b", "FSX legacy lift terms = 0 (A/B test whether MSFS still uses them)",
      all(v in (None, 0) for v in legacy.values()), level="WARNING",
      info=", ".join(f"{k.replace('lift_coef_', '')} {v}" for k, v in legacy.items() if v))
check("AP-2", "all-moving tail: htail_area = 0, whole area 48.2 ft² in elevator_area (tutorial 'Tail Geometry')",
      num(geo.get("htail_area")) == 0 and abs((num(geo.get("elevator_area")) or 0) - 48.2) < 0.5,
      info=f"htail {geo.get('htail_area')}, elevator {geo.get('elevator_area')}")
check("AP-2", "elevator_lift_coef 3.0-4.4 (CR-96008 CLδe x S/S_h; CR-2144 2.8) instead of default 5.0",
      3.0 <= (num(aero.get("elevator_lift_coef")) or 5.0) <= 4.4, info=f"is {aero.get('elevator_lift_coef', '5.0 (default)')}")
check("AP-3", "htail_incidence = 0 (normalization at α=0; trim at α=0 is 0, rounds A/B2), takeoff trim 5° (FM 6-5)",
      num(geo.get("htail_incidence")) == 0 and num(geo.get("elevator_trim_neutral")) == 5,
      info=f"htail {geo.get('htail_incidence')}, trim_neutral {geo.get('elevator_trim_neutral')}")
check("AP-2b", "trim range nose up >= 11° (FM 6-5)", (num(geo.get("elevator_trim_up_limit")) or 0) >= 11)
check("AP-6", "rudder_maxangle_scalar ≈ 0.32 (flap-type rudder share, CR-2144), elevator_maxangle_scalar 1 (all-moving tail)",
      abs((num(tune.get("rudder_maxangle_scalar")) or 1) - 0.32) < 0.05 and (num(tune.get("elevator_maxangle_scalar")) or 1) == 1,
      info=f"rudder {tune.get('rudder_maxangle_scalar')}, elevator {tune.get('elevator_maxangle_scalar')}")
check("AP-6", "rudder_lift_coef stays 5 (vertical tail = directional stability, round B2)",
      (num(aero.get("rudder_lift_coef")) or 5.0) >= 4.9, info=f"is {aero.get('rudder_lift_coef', '5.0')}")

flaps, lcf = fm.get("flaps.0", {}), num(aero.get("lift_coef_flaps")) or 0
for pos, target in ((1, 0.30), (2, 0.62)):
    v = [num(t) for t in flaps.get(f"flaps-position.{pos}", "0").split(",")]
    v += [None] * (8 - len(v))
    dcl = lcf * (num(flaps.get("lift_scalar")) or 1) * (v[3] or 1) * (v[0] or 0) / 57.29578
    check("AP-10", f"flap position {pos}: ΔCL ≈ {target} (lift_coef_flaps x lift scalar x rad), add incidence 1",
          abs(dcl - target) < 0.03 and v[7] == 1, info=f"ΔCL {dcl:.3f}, add incidence {v[7]}")

hyd = num(load(os.path.join(CFG, "systems.cfg")).get("hydraulic_system", {}).get("normal_pressure")) or 0
check("AP-10", "flaps electric (FM 1-73: AC motors); hydraulic only with a hydraulic system (T3-D run 5)",
      num(flaps.get("system_type")) == 0, info=f"system_type {flaps.get('system_type')}")
check("AP-10", "gear not hydraulic as long as [HYDRAULIC_SYSTEM] has no pressure (round E)",
      num(fm.get("contact_points", {}).get("gear_system_type")) != 1 or hyd > 0,
      info=f"gear_system_type {fm.get('contact_points', {}).get('gear_system_type')}, hydraulic pressure {hyd}")

cp = fm.get("contact_points", {})


def point(n):
    """point.N -> (z, y) in ft or None"""
    v = cp.get(f"point.{n}", "")
    parts = [p.strip() for p in v.split(",")]
    try:
        return float(parts[1]), float(parts[3])
    except (IndexError, ValueError):
        return None


main = point(1)
if main:
    import math
    angles = {n: math.degrees(math.atan2(p[1] - main[1], main[0] - p[0]))
              for n in range(3, 10) if (p := point(n)) and p[0] < main[0] - 3}
    if angles:
        n, a = min(angles.items(), key=lambda kv: kv[1])
        check("AP-5", "tail strike angle about the main wheel 11-15° (CR-2144 three-view)", 11 <= a <= 15,
              info=f"{a:.1f}° at point.{n}")

for name, maxn in (("lift_coef_aoa_table", 47), ("lift_coef_mach_table", 17), ("drag_coef_zero_lift_mach_tab", 47)):
    c = curve(aero.get(name))
    check("AP-0", f"{name}: 1D format, x ascending, <= {maxn} entries",
          c is not None and len(c) <= maxn and all(a[0] < b[0] for a, b in zip(c, c[1:])),
          info=f"{len(c) if c else 'format error'} entries")
nd = eng.get("turbineenginedata", {}).get("uncorrected_commanded_ne_table")
if nd is not None:
    check("AP-0", "uncorrected_commanded_Ne_table in nD format ('x, x :: y, y')", "::" in nd)

# --- T1: build state ---
for f in ("flight_model.cfg", "engines.cfg", "aircraft.cfg", "systems.cfg", "../flt/runway.FLT"):
    src, pkg = os.path.join(CFG, f), os.path.join(PKG, f)
    same = os.path.exists(pkg) and open(src, "rb").read() == open(pkg, "rb").read()
    check("T1", f"package contains the current {f} (Build All done after build_cfg.ps1)", same, level="WARNING")
if os.path.exists(LOG):
    newest = max(os.path.getmtime(os.path.join(PKG, f)) for f in os.listdir(PKG))
    check("T1", "BuilderLogError.txt not newer than the last build (otherwise read the log!)",
          os.path.getmtime(LOG) < newest - 5)

w = max(len(r[2]) for r in results)
for status, ap, text, info in results:
    print(f"{status:8} {ap:5} {text:{w}}  {info if status != 'OK' else ''}".rstrip())
n = sum(r[0] == "ERROR" for r in results)
print(f"\n{len(results)} checks, {n} ERRORS, {sum(r[0] == 'WARNING' for r in results)} WARNINGS")
sys.exit(1 if n else 0)
