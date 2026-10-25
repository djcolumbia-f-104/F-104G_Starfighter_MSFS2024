"""Checks whether a PDF has a text layer (or contains only scanned images)."""
import sys

import pymupdf

doc = pymupdf.open(sys.argv[1])
pages = len(doc)
with_text = 0
for page in doc:
    if len(page.get_text().strip()) > 50:
        with_text += 1
print(f"pages: {pages}, with text: {with_text}")
for i in sorted({0, min(10, pages - 1), pages // 2}):
    print(f"--- page {i + 1} ---")
    print(doc[i].get_text()[:400])
