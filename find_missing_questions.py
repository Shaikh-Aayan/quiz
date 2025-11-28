#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find missing questions in PDF"""

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

# Find all question numbers
print("All question numbers found in PDF:")
print("="*70)

question_numbers = set()
for i, line in enumerate(lines):
    q_match = re.match(r'^(\d+)\.\s*$', line)
    if q_match:
        q_num = int(q_match.group(1))
        question_numbers.add(q_num)
        # Show context
        context = []
        if i+1 < len(lines):
            context.append(lines[i+1][:80])
        if i+2 < len(lines):
            context.append(lines[i+2][:80])
        print(f"Q{q_num}: {' | '.join(context)}")

print("\n" + "="*70)
print(f"Total questions found: {len(question_numbers)}")
print(f"Question numbers: {sorted(question_numbers)}")

# Find missing
all_q = set(range(1, 41))
missing = all_q - question_numbers
print(f"\nMissing questions: {sorted(missing)}")
print(f"Total missing: {len(missing)}")
