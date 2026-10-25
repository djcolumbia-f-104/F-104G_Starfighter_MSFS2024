"""Entfernt Kolbenmotor-Zustände ([Engine Parameters.*], [Propeller.*]) aus den .flt-Dateien des Prüfstands.

Aufruf: clean_flt.py <flt-ordner>
Hintergrund: Die .flt-Dateien stammen vom Kolbenmotor-Beispiel des SDK. Sie setzten das J79 beim Laden auf
46 % (Startbahn) bzw. 150 % Drehzahl mit Magnetzündern -> unmöglicher Anfangszustand, Triebwerk sprang nie an.
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
    print(f"{name}: {removed} Abschnitt(e) entfernt")
