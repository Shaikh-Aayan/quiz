#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Physics parser WITH Groq API"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

# Load .env
from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
from backend.extractor import extract_questions_from_pdf

logging.basicConfig(level=logging.INFO, format='%(message)s')

pdf_path = "Physics-X-Paper-I-2025.pdf"

print("="*70)
print("TEST: PHYSICS PDF WITH GROQ API")
print("="*70)

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

questions = extract_questions_from_pdf(pdf_bytes)

print(f"\n{'='*70}")
print(f"✅ TOTAL EXTRACTED: {len(questions)} questions")
print(f"{'='*70}\n")

# Show first 10 and last 5
for i, q in enumerate(questions[:10], 1):
    has_image = "📷" if q.get('image_data') else "  "
    has_answer = "✓" if q.get('correct_option') is not None else "✗"
    print(f"{has_image} {has_answer} Q{i}: {q['question'][:60]}...")
    print(f"   Options: {len(q['options'])} | Answer: {q.get('correct_option', '?')}")

print("\n... (middle questions omitted) ...\n")

for i, q in enumerate(questions[-5:], len(questions)-4):
    has_image = "📷" if q.get('image_data') else "  "
    has_answer = "✓" if q.get('correct_option') is not None else "✗"
    print(f"{has_image} {has_answer} Q{i}: {q['question'][:60]}...")
    print(f"   Options: {len(q['options'])} | Answer: {q.get('correct_option', '?')}")

print()
print("="*70)
print(f"SUMMARY")
print("="*70)
print(f"✅ Total questions extracted: {len(questions)}")
print(f"✅ Questions with answers: {sum(1 for q in questions if q.get('correct_option') is not None)}")
print(f"✅ Questions with images: {sum(1 for q in questions if q.get('image_data'))}")
print("="*70)
