#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test extraction to get all 40 MCQs"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

import logging
from backend.extractor import extract_questions_from_pdf

logging.basicConfig(level=logging.INFO, format='%(message)s')

pdf_path = "Physics-X-Paper-I-2025.pdf"

print("="*70)
print("TESTING FULL EXTRACTION - TARGET: 40 MCQs")
print("="*70)

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

questions = extract_questions_from_pdf(pdf_bytes)

print(f"\n{'='*70}")
print(f"✅ TOTAL EXTRACTED: {len(questions)} questions")
print(f"{'='*70}\n")

for i, q in enumerate(questions, 1):
    has_image = "📷" if q.get('image_data') else "  "
    print(f"{has_image} Q{i}: {q['question'][:65]}...")
    print(f"   Options: {len(q['options'])} | Answer: {q.get('correct_option', '?')}")
    if q.get('image_data'):
        print(f"   Image: {len(q['image_data'])} bytes")
    print()

print("="*70)
print(f"RESULT: {len(questions)}/40 questions extracted")
if len(questions) >= 35:
    print("✅ EXCELLENT - Got most questions!")
elif len(questions) >= 30:
    print("✅ GOOD - Got 30+ questions")
else:
    print("⚠️  Need more work")
print("="*70)
