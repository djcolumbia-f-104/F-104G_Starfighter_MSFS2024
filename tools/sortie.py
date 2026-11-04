"""Sortie runner (test plan section 6, 2026-11-04): several test points in one flight, chained by pre/postconditions.

Usage (with the Python of the simconnect-mcp venv; watchdog running):
  C:\\Users\\pete\\AppData\\Local\\simconnect-mcp\\.venv\\Scripts\\python.exe -I tools\\sortie.py <plan.txt> [first_step]
Plan file (tools/sorties/*.txt): one step per line, `label | command | expect | timeout_s`; '#' starts a comment.
- command: a tool path with arguments (run with this Python, -I); `{csv}` = docs/data/flighttest_<date>_<plan>_<label>.csv,
  `{csv:<label>}` = the csv of an earlier step.
- expect: text that must appear in the step output (e.g. "POST OK"); empty = only a zero exit code is required.
The runner stops at the first step that fails (exit code, missing expect text, timeout) - the jet stays in the state the
failed script left (every flight script ends via `position` or on the ground; the watchdog refuels). The full output of
each step goes to build/sorties/<plan>_<label>.txt; key lines (Result/POST/peak/zeta/period/TOUCHDOWN/roll/ABORT) are echoed.
Start in the middle with `first_step` (label). Summary table at the end.
"""
import datetime
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
plan_path = sys.argv[1]
first = sys.argv[2] if len(sys.argv) > 2 else None
plan = os.path.splitext(os.path.basename(plan_path))[0]
date = datetime.date.today().isoformat()
KEY = re.compile(r"Result|POST|peak|zeta|period|TOUCHDOWN|roll from|ABORT|Abort|FAIL|SELFTEST|on runway|equilibrium|after")
os.makedirs(os.path.join(ROOT, "build", "sorties"), exist_ok=True)

steps = []
for line in open(plan_path, encoding="utf-8"):
    line = line.split("#")[0].strip()
    if line:
        label, cmd, expect, tmo = [x.strip() for x in line.split("|")]
        steps.append((label, cmd, expect, float(tmo)))
if first:
    steps = steps[[s[0] for s in steps].index(first):]

csvs, summary = {}, []
for label, cmd, expect, tmo in steps:
    csvs[label] = os.path.join("docs", "data", f"flighttest_{date}_{plan}_{label}.csv")
    cmd = re.sub(r"\{csv:(\w+)\}", lambda m: csvs[m.group(1)], cmd).replace("{csv}", csvs[label])
    print(f"=== {label}: {cmd}")
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-I"] + cmd.split(), cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=tmo)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or "") if isinstance(e.stdout, str) else "", "timeout"
    with open(os.path.join(ROOT, "build", "sorties", f"{plan}_{label}.txt"), "w", encoding="utf-8") as f:
        f.write(out)
    for ln in out.splitlines():
        if KEY.search(ln):
            print("   ", ln[:160])
    ok = rc == 0 and (not expect or expect in out)
    summary.append((label, "OK" if ok else f"FAIL (rc {rc}{', no ' + repr(expect) if expect and expect not in out else ''})",
                    time.time() - t0))
    if not ok:
        print(f"!!! sortie stopped at step '{label}'")
        break

print(f"\nSORTIE {plan} summary")
for label, st, dt in summary:
    print(f"  {label:12} {st:40} {dt:5.0f} s")
print("SORTIE COMPLETE" if len(summary) == len(steps) and all(s[1] == "OK" for s in summary) else "SORTIE INCOMPLETE")
