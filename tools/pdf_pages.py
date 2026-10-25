"""Renders PDF pages as PNG.

Usage: pdf_pages.py <pdf> <output folder> <pages> [dpi]
<pages> 1-based, e.g. "1-12" or "5,7,20-22".
"""
import os
import sys

import pymupdf


def parse_pages(spec):
    pages = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            pages.extend(range(int(a), int(b) + 1))
        else:
            pages.append(int(part))
    return pages


pdf, out_dir, spec = sys.argv[1:4]
dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 110
os.makedirs(out_dir, exist_ok=True)
doc = pymupdf.open(pdf)
for n in parse_pages(spec):
    path = os.path.join(out_dir, f"s{n:03d}.png")
    doc[n - 1].get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY).save(path)
    print(path)
