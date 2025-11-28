#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test both PDFs with improved Groq retry logic"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from backend.extractor import extract_questions_from_pdf
import os

pdfs = sorted([f for f in os.listdir('.') if f.endswith('.pdf')])

print("\n" + "="*80)
print("🧪 FINAL TEST - Both PDFs with Improved Groq")
print("="*80 + "\n")

for pdf_file in pdfs:
    print(f"\n{'='*80}")
    print(f"📄 {pdf_file}")
    print(f"{'='*80}\n")
    
    with open(pdf_file, 'rb') as f:
        pdf_bytes = f.read()
    
    questions = extract_questions_from_pdf(pdf_bytes)
    
    with_answers = sum(1 for q in questions if q.get('correct_option') is not None)
    with_images = sum(1 for q in questions if q.get('image_data'))
    
    print(f"✅ Extracted: {len(questions)} questions")
    print(f"✅ With answers: {with_answers}/{len(questions)} ({100*with_answers//len(questions)}%)")
    print(f"✅ With images: {with_images}/{len(questions)}")
    
    # Show first 5
    print(f"\n📋 First 5 questions:")
    for i, q in enumerate(questions[:5], 1):
        ans = q.get('correct_option')
        ans_str = f"✓ {ans}" if ans is not None else "✗ None"
        print(f"   Q{i}: {q['question'][:50]}... [{ans_str}]")

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80 + "\n")
