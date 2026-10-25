"""Removes piston engine states ([Engine Parameters.*], [Propeller.*]) from the test bed's .flt files.

Usage: clean_flt.py <flt folder>
Background: the .flt files come from the SDK's piston engine sample. On loading they set the J79 to
46 % (runway) or 150 % rpm with magnetos -> impossible initial state, the engine never started.
"""
import os
import re
import sys

DROP = re.compile(r"^\[(Engine Parameters|Propeller)\.", re.I)
folder = sys.argv[1]
for name in sorted(os.listdir(folder)):
    if not name.lower().endswith(".flt"):
        continue
    path = os.path.join(folder, name)
    out, skip, removed = [], False, 0
    for line in open(path, encoding="utf-8-sig").read().splitlines():
        if line.startswith("["):
            skip = bool(DROP.match(line))
            removed += skip
        if not skip:
            out.append(line)
    open(path, "w", encoding="utf-8", newline="\r\n").write("\n".join(out).rstrip() + "\n")
    print(f"{name}: {removed} section(s) removed")
