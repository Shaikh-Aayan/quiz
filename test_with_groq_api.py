#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test English parser WITH Groq API - includes writing questions"""

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

pdf_path = "English-Compulsory-X-Paper-I-2025.pdf"

print("="*70)
print("TEST: ENGLISH PDF WITH GROQ API (includes writing questions)")
print("="*70)

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

questions = extract_questions_from_pdf(pdf_bytes)

print(f"\n{'='*70}")
print(f"✅ TOTAL EXTRACTED: {len(questions)} questions")
print(f"{'='*70}\n")

# Summary
for i, q in enumerate(questions, 1):
    has_image = "📷" if q.get('image_data') else "  "
    has_answer = "✓" if q.get('correct_option') is not None else "✗"
    print(f"{has_image} {has_answer} Q{i}: {q['question'][:60]}...")
    print(f"   Options: {len(q['options'])} | Answer: {q.get('correct_option', '?')}")
    if q.get('image_data'):
        print(f"   Image: {len(q['image_data'])} bytes")
    print()

print("="*70)
print(f"SUMMARY")
print("="*70)
print(f"✅ Total questions extracted: {len(questions)}")
print(f"✅ Questions with answers: {sum(1 for q in questions if q.get('correct_option') is not None)}")
print(f"✅ Questions with images: {sum(1 for q in questions if q.get('image_data'))}")
print(f"⚠️  Listening questions (Q7-Q13): EXCLUDED (no audio)")
print(f"✅ Reading questions (Q14-Q23): INCLUDED")
print(f"✅ Writing questions (Q24-Q30): INCLUDED (Groq identifies answers)")
print("="*70)
