#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug Q36 and Q39"""

import fitz
import re

pdf_path = "Physics-X-Paper-I-2025.pdf"
doc = fitz.open(pdf_path)
text = ""

for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text() + "\n"

lines = text.split('\n')
lines = [l.strip() for l in lines]

# Find Q35 and Q37 to see what's between them
print("Looking for Q35, Q36, Q37, Q38, Q39, Q40...")
print("="*70)

for i, line in enumerate(lines):
    if re.match(r'^(35|36|37|38|39|40)\.\s*$', line):
        q_num = int(line.split('.')[0])
        print(f"\nFound Q{q_num} at line {i}")
        print(f"Context (lines {i} to {min(i+15, len(lines))}):")
        for j in range(i, min(i+15, len(lines))):
            print(f"  {j}: {lines[j][:80]}")
