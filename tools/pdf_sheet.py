"""Kontaktabzug: mehrere PDF-Seiten als Raster in einem PNG (zum schnellen Durchblättern).

Aufruf: pdf_sheet.py <pdf> <ausgabe.png> <erste_seite> [anzahl=12] [spalten=4]
Seiten 1-basiert; jede Kachel ist mit der PDF-Seitennummer beschriftet.
"""
import sys

import pymupdf

pdf, out, first = sys.argv[1], sys.argv[2], int(sys.argv[3])
count = int(sys.argv[4]) if len(sys.argv) > 4 else 12
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 4

src = pymupdf.open(pdf)
last = min(first + count - 1, len(src))
tile_w, tile_h = 612, 792
rows = (last - first) // cols + 1
sheet = pymupdf.open()
page = sheet.new_page(width=cols * tile_w, height=rows * tile_h)
for i, n in enumerate(range(first, last + 1)):
    r = pymupdf.Rect(0, 0, tile_w, tile_h) + (
        (i % cols) * tile_w, (i // cols) * tile_h, (i % cols) * tile_w, (i // cols) * tile_h)
    page.show_pdf_page(r, src, n - 1)
    page.draw_rect(r, color=(0.6, 0.6, 0.6), width=2)
    page.insert_text(r.tl + (12, 40), f"PDF {n}", fontsize=36, color=(1, 0, 0))
page.get_pixmap(dpi=48, colorspace=pymupdf.csGRAY).save(out)
print(out)
