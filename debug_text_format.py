#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug the text format"""

import fitz
import re

pdf_path = "Physics-X-Paper-I-2025.pdf"

# Extract text from PDF
doc = fitz.open(pdf_path)
text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text() + "\n"

# Find all lines that start with a number followed by period
lines = text.split('\n')
print("="*70)
print("LINES STARTING WITH NUMBER.:")
print("="*70)

count = 0
for i, line in enumerate(lines):
    if re.match(r'^\d+\.', line):
        print(f"Line {i}: {repr(line[:100])}")
        count += 1
        if count >= 50:
            break

print(f"\nTotal lines with number pattern: {count}")

# Show lines around question 1
print("\n" + "="*70)
print("CONTEXT AROUND FIRST REAL QUESTION:")
print("="*70)

for i, line in enumerate(lines):
    if 'vibrating body' in line.lower():
        print(f"\nFound at line {i}")
        for j in range(max(0, i-3), min(len(lines), i+15)):
            print(f"{j}: {repr(lines[j][:80])}")
        break

# Show lines around question 6
print("\n" + "="*70)
print("CONTEXT AROUND QUESTION 6:")
print("="*70)

for i, line in enumerate(lines):
    if 'loudest sound' in line.lower():
        print(f"\nFound at line {i}")
        for j in range(max(0, i-3), min(len(lines), i+15)):
            print(f"{j}: {repr(lines[j][:80])}")
        break
