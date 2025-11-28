#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final debug test - check exactly what's being extracted"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from backend.extractor import extract_questions_from_pdf
import json

pdf_path = "Mathematics-X-Paper-I-2025.pdf"

print("="*80)
print("🔍 FINAL DEBUG TEST - Mathematics PDF")
print("="*80)

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

print(f"\n📊 Extracting from {pdf_path}...")
questions = extract_questions_from_pdf(pdf_bytes)

print(f"\n✅ Extracted {len(questions)} questions\n")

# Show first 5 with full details
print("📋 FIRST 5 QUESTIONS (with full details):")
print("-"*80)

for i, q in enumerate(questions[:5], 1):
    print(f"\nQ{i}:")
    print(f"  Question: {q['question'][:60]}...")
    print(f"  Options: {q['options']}")
    print(f"  correct_option: {q.get('correct_option')} (type: {type(q.get('correct_option'))})")
    print(f"  explanation: {q.get('explanation', 'N/A')}")
    print(f"  image_data: {q.get('image_data') is not None}")

# Show JSON format (what API will return)
print("\n\n📤 JSON FORMAT (what API returns):")
print("-"*80)
print(json.dumps(questions[:3], indent=2, default=str))

print("\n" + "="*80)
print(f"SUMMARY: {len(questions)} questions extracted")
print(f"Questions with answers: {sum(1 for q in questions if q.get('correct_option') is not None)}")
print("="*80)
