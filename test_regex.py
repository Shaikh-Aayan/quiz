#!/usr/bin/env python3
import re
import fitz

pdf_path = "Physics-X-Paper-I-2025.pdf"

# Extract text from PDF
doc = fitz.open(pdf_path)
text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text() + "\n"

lines = text.split('\n')
lines = [l.strip() for l in lines]

# Test regex
print("Testing regex pattern: r'^(\d+)\.\s*$'")
print()

count = 0
for i, line in enumerate(lines):
    if re.match(r'^(\d+)\.\s*$', line):
        print(f"Line {i}: MATCH - '{line}'")
        count += 1
        if count >= 20:
            break

print(f"\nTotal matches: {count}")

# Show what lines look like
print("\n" + "="*70)
print("Sample lines around question 1:")
for i, line in enumerate(lines[65:85]):
    print(f"{i+65}: '{line}'")
