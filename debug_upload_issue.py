#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug why upload is failing"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
from backend.extractor import extract_questions_from_pdf

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Try to find the PDF
import os
pdfs = [f for f in os.listdir('.') if f.endswith('.pdf')]
print(f"PDFs found: {pdfs}\n")

for pdf_file in pdfs:
    print("="*70)
    print(f"Testing: {pdf_file}")
    print("="*70)
    
    try:
        with open(pdf_file, 'rb') as f:
            pdf_bytes = f.read()
        
        print(f"File size: {len(pdf_bytes)} bytes\n")
        
        questions = extract_questions_from_pdf(pdf_bytes)
        
        print(f"\n✅ SUCCESS: Extracted {len(questions)} questions")
        if questions:
            print(f"First question: {questions[0]['question'][:60]}...")
            print(f"Has answer: {questions[0].get('correct_option') is not None}")
            print(f"Has image: {questions[0].get('image_data') is not None}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
