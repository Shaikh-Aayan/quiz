#!/usr/bin/env python3
"""Extract MCQs from Physics PDF using OCR"""

import sys
sys.path.insert(0, 'backend')

from pathlib import Path
from dotenv import load_dotenv
from extractor import extract_questions_from_pdf
import json

load_dotenv(Path('backend/.env'))

pdf_path = Path('Physics-X-Paper-I-2025.pdf')

print("="*60)
print("🚀 EXTRACTING MCQs WITH OCR ENABLED")
print("="*60)

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

# Extract with OCR enabled (skip_ocr=False)
questions = extract_questions_from_pdf(pdf_bytes, skip_ocr=False)

print(f"\n✅ Extraction Complete!")
print(f"📊 Total questions extracted: {len(questions)}")

if questions:
    print("\n" + "="*60)
    print("EXTRACTED MCQs:")
    print("="*60)
    
    for i, q in enumerate(questions, 1):
        print(f"\nQ{i}: {q.get('question', 'N/A')[:80]}...")
        print(f"   Options: {len(q.get('options', []))} options")
        opts = q.get('options', [])
        for j, opt in enumerate(opts[:4], 1):
            print(f"      {chr(64+j)}) {opt[:60]}...")
        if q.get('correct_option') is not None:
            print(f"   ✓ Answer: {chr(65 + q.get('correct_option'))}")
        print()
else:
    print("\n❌ No questions extracted!")

# Save to JSON for inspection
output_file = Path('extracted_questions.json')
with open(output_file, 'w') as f:
    json.dump(questions, f, indent=2)
print(f"\n💾 Saved to: {output_file}")
