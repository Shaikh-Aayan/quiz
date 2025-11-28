#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the physics parser"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

import fitz
import logging
from backend.physics_parser import parse_physics_mcqs, parse_physics_mcqs_advanced

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

pdf_path = "Physics-X-Paper-I-2025.pdf"

# Extract text from PDF
doc = fitz.open(pdf_path)
text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text() + "\n"

print("="*70)
print("TESTING PHYSICS PARSER")
print("="*70)

# Test basic parser
print("\n🔧 BASIC PARSER:")
print("-"*70)
questions_basic = parse_physics_mcqs(text)
print(f"\n✅ Extracted {len(questions_basic)} questions")

for i, q in enumerate(questions_basic[:10], 1):
    print(f"\nQ{i}: {q['question'][:70]}...")
    print(f"   Options: {len(q['options'])}")
    for j, opt in enumerate(q['options'], 1):
        print(f"      {chr(64+j)}) {opt[:60]}...")

# Test advanced parser
print("\n\n" + "="*70)
print("🔧 ADVANCED PARSER:")
print("-"*70)
questions_adv = parse_physics_mcqs_advanced(text)
print(f"\n✅ Extracted {len(questions_adv)} questions")

for i, q in enumerate(questions_adv[:10], 1):
    print(f"\nQ{i}: {q['question'][:70]}...")
    print(f"   Options: {len(q['options'])}")
    for j, opt in enumerate(q['options'], 1):
        print(f"      {chr(64+j)}) {opt[:60]}...")

# Summary
print("\n\n" + "="*70)
print("SUMMARY:")
print("="*70)
print(f"Expected: 40 questions")
print(f"Basic parser: {len(questions_basic)} questions")
print(f"Advanced parser: {len(questions_adv)} questions")
print(f"\n{'✅ SUCCESS!' if len(questions_adv) >= 35 else '⚠️  NEEDS IMPROVEMENT'}")
