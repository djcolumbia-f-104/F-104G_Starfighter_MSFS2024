"""Listet die Parameter einer SDK-Referenzseite (docs/sdk-ref/*.md) kompakt auf.

Aufruf: sdkref_params.py <datei.md> [abschnitt]
Ausgabe je Parameter: Name | Typ | Pflicht | Kurzbeschreibung (gekürzt).
Ohne <abschnitt> alle Abschnitte; sonst nur der passende (z. B. "AIRPLANE_GEOMETRY").
"""
import re
import sys

path = sys.argv[1]
want = sys.argv[2].upper() if len(sys.argv) > 2 else None
section = None
for line in open(path, encoding="utf-8"):
    m = re.match(r"^#{2,4} (?:<span[^>]*>)?\[?([^\]<]+)", line)
    if m:
        section = m.group(1).strip()
        if not want or want in section.upper():
            print(f"\n## {section}")
        continue
    if want and (not section or want not in section.upper()):
        continue
    if line.startswith("|") and "`" in line.split("|")[1]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        name = re.sub(r"<[^>]+>|\{\{[^}]*\}\}", "", cells[0]).strip()
        desc = re.sub(r"<[^>]+>|\{\{[^}]*\}\}|\[([^\]]*)\]\([^)]*\)", r"\1", cells[1] if len(cells) > 1 else "")
        rest = " | ".join(cells[2:4]) if len(cells) > 3 else ""
        print(f"{name} | {rest} | {desc[:160]}")
