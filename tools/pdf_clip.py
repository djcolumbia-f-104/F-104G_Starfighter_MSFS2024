"""Renders a clip of a PDF page, optionally rotated (for tables printed sideways).

Usage: pdf_clip.py <pdf> <output.png> <page> [x0 y0 x1 y1] [--rot 90|180|270] [--dpi 170]
Clip in fractions of the page (0..1), default whole page. Page numbers are 1-based.
"""
import sys

import pymupdf

args = sys.argv[1:]
rot, dpi = 0, 170
if "--rot" in args:
    i = args.index("--rot")
    rot = int(args[i + 1])
    del args[i:i + 2]
if "--dpi" in args:
    i = args.index("--dpi")
    dpi = int(args[i + 1])
    del args[i:i + 2]
pdf, out, n = args[0], args[1], int(args[2])
box = [float(v) for v in args[3:7]] if len(args) >= 7 else [0, 0, 1, 1]

page = pymupdf.open(pdf)[n - 1]
r = page.rect
clip = pymupdf.Rect(r.width * box[0], r.height * box[1], r.width * box[2], r.height * box[3])
mat = pymupdf.Matrix(dpi / 72, dpi / 72).prerotate(rot)
page.get_pixmap(matrix=mat, clip=clip, colorspace=pymupdf.csGRAY).save(out)
print(out)
