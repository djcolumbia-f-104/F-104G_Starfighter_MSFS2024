r"""Weather presets for the test program (2026-11-06, F9 crosswind): copies pete's in-sim template (clear sky, ISA, one
ground wind layer; docs/data/weather/template_F-104G_350_20Kts.WPR, saved from the MSFS 2024 weather panel) with other wind
directions/speeds into %APPDATA%\Microsoft Flight Simulator 2024\Weather\Presets.

Usage: tools\.venv\Scripts\python.exe -I tools\make_wpr.py [dir:kt ...]   (default: the F9 set + F-104G_Calm_ISA)
Runway 26L = 263° -> 350° and 170° are ≈ pure crosswind from the right / left. Only the WindLayerAngle/WindLayerSpeed
values and the name change; the template's format (version 1,4) is kept byte for byte otherwise.
"""
import math
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TEMPLATE = os.path.join(ROOT, "docs", "data", "weather", "template_F-104G_350_20Kts.WPR")
OUT = os.path.join(os.environ["APPDATA"], "Microsoft Flight Simulator 2024", "Weather", "Presets")
sets = sys.argv[1:] or ["350:10", "350:15", "350:25",   # 350:20 = pete's own template preset (never overwritten)
                         "170:10", "170:15", "170:20", "170:25", "0:0"]
tpl = open(TEMPLATE, encoding="utf-8").read()
for item in sets:
    d, kt = (float(v) for v in item.split(":"))
    name = "F-104G_Calm_ISA" if kt == 0 else f"F-104G_{d:03.0f}_{kt:.0f}Kts"
    s = re.sub(r"<Name>.*?</Name>", f"<Name>{name}</Name>", tpl, count=1)
    s = re.sub(r'(<WindLayerAngle Value=")[0-9.]+', rf"\g<1>{d:.3f}", s, count=1)
    s = re.sub(r'(<WindLayerSpeed Value=")[0-9.]+', rf"\g<1>{kt:.3f}", s, count=1)
    path = os.path.join(OUT, name + ".WPR")
    if name == "F-104G_350_20Kts":
        print("skipped", name, "(template preset saved in the sim)")
        continue
    if os.path.exists(path) and open(path, encoding="utf-8").read() == s:
        print("unchanged", name)
        continue
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    xw = kt * abs(math.sin(math.radians(d - 263.4)))
    print(f"wrote {name}.WPR (wind {d:.0f}°/{kt:.0f} kt -> crosswind on 26L ≈ {xw:.0f} kt)")
