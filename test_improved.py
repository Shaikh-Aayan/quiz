#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

import fitz
import logging
from backend.improved_physics_parser import parse_physics_mcqs_improved

logging.basicConfig(level=logging.INFO, format='%(message)s')

pdf_path = "Physics-X-Paper-I-2025.pdf"

# Extract text from PDF
doc = fitz.open(pdf_path)
text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text() + "\n"

print("="*70)
print("TESTING IMPROVED PHYSICS PARSER")
print("="*70)

questions = parse_physics_mcqs_improved(text)

print(f"\n✅ Extracted {len(questions)} questions\n")

for i, q in enumerate(questions[:15], 1):
    print(f"Q{i}: {q['question'][:70]}...")
    for j, opt in enumerate(q['options'], 1):
        print(f"   {chr(64+j)}) {opt[:60]}...")
    print()

print("="*70)
print(f"SUMMARY: Expected 40, Got {len(questions)}")
print("="*70)
