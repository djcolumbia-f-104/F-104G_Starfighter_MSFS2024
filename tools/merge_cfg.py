"""Legt eine F-104-Quelldatei (source/cfg/*.f104.cfg) über eine SDK-Vorlage und schreibt das Ergebnis.

Aufruf: merge_cfg.py <vorlage.cfg | -> <quelle.cfg> <ziel.cfg>
- Gleicher Schlüssel im gleichen Abschnitt (ohne Groß/Klein) -> Zeile der Quelle ersetzt die der Vorlage.
- Neuer Schlüssel -> am Ende des Abschnitts angehängt; neuer Abschnitt -> am Dateiende angehängt.
- Wert DELETE -> Schlüssel wird aus der Vorlage entfernt.
- Vorlage "-" -> Quelle wird ohne Vorlage übernommen (nur DELETE-Zeilen entfernt).
Kommentarzeilen der Quelle vor dem ersten Abschnitt werden als Kopf übernommen.
"""
import re
import sys

SECTION = re.compile(r"^\s*\[([^\]]+)\]")
KEY = re.compile(r"^\s*([^;=\s][^=]*?)\s*=")


def parse(path):
    """-> (kopfzeilen, [(abschnitt, [zeilen])])"""
    head, sections = [], []
    for line in open(path, encoding="utf-8-sig"):
        line = line.rstrip("\r\n")
        m = SECTION.match(line)
        if m:
            sections.append((m.group(1).strip(), [line]))
        elif sections:
            sections[-1][1].append(line)
        else:
            head.append(line)
    return head, sections


def key_of(line):
    m = KEY.match(line)
    return m.group(1).strip().lower() if m else None


def is_delete(line):
    return line.split("=", 1)[1].split(";", 1)[0].strip().upper() == "DELETE"


base_path, src_path, out_path = sys.argv[1:4]
src_head, src_secs = parse(src_path)
base_head, base_secs = ([], []) if base_path == "-" else parse(base_path)

index = {name.lower(): lines for name, lines in base_secs}
for name, lines in src_secs:
    target = index.get(name.lower())
    if target is None:
        target = [lines[0]]
        base_secs.append((name, target))
        index[name.lower()] = target
    for line in lines[1:]:
        k = key_of(line)
        if k is None:
            if line.strip().startswith(";"):
                target.append(line)  # Kommentare der Quelle mitnehmen
            continue
        pos = next((i for i, l in enumerate(target) if key_of(l) == k), None)
        if is_delete(line):
            if pos is not None:
                del target[pos]
        elif pos is None:
            target.append(line)
        else:
            target[pos] = line

with open(out_path, "w", encoding="utf-8", newline="\r\n") as f:
    for line in src_head:
        f.write(line + "\n")
    f.write("; GENERIERT von tools/merge_cfg.py - nicht direkt bearbeiten, sondern source/cfg/ ändern.\n\n")
    for _, lines in base_secs:
        # Leerzeilen am Abschnittsende einheitlich
        while len(lines) > 1 and not lines[-1].strip():
            lines.pop()
        for line in lines:
            f.write(line + "\n")
        f.write("\n")
print(out_path)
