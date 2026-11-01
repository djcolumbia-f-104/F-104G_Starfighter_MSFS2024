"""Ground roll from a fixed reference speed to the stop (landing_test.py logs) - independent of the touchdown transient
(hop, engine spool-down, nose lowering). Usage: python -I tools/roll_from_speed.py <landing.csv> [kias=165] [chute|nochute]
FM reference scaled with (v / 166.5)²: A8-3 2 760 ft with chute, A8-4 3 130 ft without (17 900 lb, 1 500 ft, 12 °C)."""
import csv
import sys

fn = sys.argv[1]
v0 = float(sys.argv[2]) if len(sys.argv) > 2 else 165.0
ref = 3130.0 if "nochute" in sys.argv[3:] else 2760.0
r = [x for x in csv.DictReader(open(fn)) if x["phase"] == "rollout"]
s = None
for i in range(1, len(r)):
    fa, fb = float(r[i - 1]["ias"]), float(r[i]["ias"])
    if fb <= v0 < fa:
        k = (fa - v0) / (fa - fb)
        s = float(r[i - 1]["along_ft"]) + k * (float(r[i]["along_ft"]) - float(r[i - 1]["along_ft"]))
if s is None:
    sys.exit("reference speed not crossed in the rollout")
roll = float(r[-1]["along_ft"]) - s
fm = ref * (v0 / 166.5) ** 2
print(f"roll from {v0:.0f} KIAS: {roll:.0f} ft, FM {fm:.0f} ft -> {100 * (roll / fm - 1):+.1f} %")
