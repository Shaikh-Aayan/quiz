#!/usr/bin/env python3
"""Test script to extract MCQs from Physics PDF"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
from backend.extractor import extract_questions_from_pdf

load_dotenv(Path(__file__).parent / "backend" / ".env")

pdf_path = Path(__file__).parent / "Physics-X-Paper-I-2025.pdf"

print(f"📄 Testing extraction from: {pdf_path}")
print(f"📊 File exists: {pdf_path.exists()}")
print(f"📦 File size: {pdf_path.stat().st_size / 1024:.2f} KB")
print("\n" + "="*60)
print("🚀 Starting MCQ extraction...")
print("="*60 + "\n")

try:
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    questions = extract_questions_from_pdf(pdf_bytes)
    
    print(f"\n✅ Extraction successful!")
    print(f"📊 Total questions extracted: {len(questions)}")
    print("\n" + "="*60)
    print("EXTRACTED MCQs:")
    print("="*60 + "\n")
    
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q.get('question', 'N/A')[:100]}...")
        print(f"   Options: {len(q.get('options', []))} options")
        if q.get('correct_answer'):
            print(f"   Answer: {q.get('correct_answer')}")
        print()
    
except Exception as e:
    print(f"\n❌ Error during extraction:")
    print(f"   Type: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    import traceback
    traceback.print_exc()
