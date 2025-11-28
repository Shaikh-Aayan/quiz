#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive local test - all PDFs, all features"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
from backend.extractor import extract_questions_from_pdf
import os

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Find all PDFs
pdfs = sorted([f for f in os.listdir('.') if f.endswith('.pdf')])

print("\n" + "="*80)
print("🧪 COMPREHENSIVE LOCAL TEST - ALL PDFs")
print("="*80 + "\n")

all_results = {}

for pdf_file in pdfs:
    print(f"\n{'='*80}")
    print(f"📄 Testing: {pdf_file}")
    print(f"{'='*80}\n")
    
    try:
        with open(pdf_file, 'rb') as f:
            pdf_bytes = f.read()
        
        print(f"📊 File size: {len(pdf_bytes):,} bytes")
        
        questions = extract_questions_from_pdf(pdf_bytes)
        
        print(f"\n✅ EXTRACTION SUCCESSFUL")
        print(f"   Total questions: {len(questions)}")
        
        # Analyze questions
        with_answers = sum(1 for q in questions if q.get('correct_option') is not None)
        with_images = sum(1 for q in questions if q.get('image_data'))
        
        print(f"   Questions with answers: {with_answers}/{len(questions)}")
        print(f"   Questions with images: {with_images}/{len(questions)}")
        
        # Show first 3 questions
        print(f"\n📋 First 3 Questions:")
        for i, q in enumerate(questions[:3], 1):
            answer_status = "✓" if q.get('correct_option') is not None else "✗"
            image_status = "📷" if q.get('image_data') else "  "
            print(f"   {image_status} {answer_status} Q{i}: {q['question'][:55]}...")
            print(f"      Options: {len(q['options'])} | Answer: {q.get('correct_option', '?')}")
        
        # Show last 3 questions
        if len(questions) > 3:
            print(f"\n📋 Last 3 Questions:")
            for i, q in enumerate(questions[-3:], len(questions)-2):
                answer_status = "✓" if q.get('correct_option') is not None else "✗"
                image_status = "📷" if q.get('image_data') else "  "
                print(f"   {image_status} {answer_status} Q{i}: {q['question'][:55]}...")
                print(f"      Options: {len(q['options'])} | Answer: {q.get('correct_option', '?')}")
        
        all_results[pdf_file] = {
            'status': '✅ SUCCESS',
            'total': len(questions),
            'with_answers': with_answers,
            'with_images': with_images
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        all_results[pdf_file] = {
            'status': '❌ FAILED',
            'error': str(e)
        }

# Final Summary
print(f"\n\n{'='*80}")
print("📊 FINAL SUMMARY")
print(f"{'='*80}\n")

for pdf_file, result in all_results.items():
    print(f"📄 {pdf_file}")
    if result['status'] == '✅ SUCCESS':
        print(f"   Status: {result['status']}")
        print(f"   Questions: {result['total']}")
        print(f"   With answers: {result['with_answers']}/{result['total']}")
        print(f"   With images: {result['with_images']}/{result['total']}")
    else:
        print(f"   Status: {result['status']}")
        print(f"   Error: {result.get('error', 'Unknown')}")
    print()

# Overall status
total_pdfs = len(all_results)
successful = sum(1 for r in all_results.values() if r['status'] == '✅ SUCCESS')

print(f"{'='*80}")
print(f"🎯 OVERALL: {successful}/{total_pdfs} PDFs successful")
if successful == total_pdfs:
    print("✅ ALL TESTS PASSED!")
else:
    print(f"⚠️  {total_pdfs - successful} PDFs failed")
print(f"{'='*80}\n")
