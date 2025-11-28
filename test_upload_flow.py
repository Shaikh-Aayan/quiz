#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the complete upload flow - extraction to database"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

import logging
from backend.extractor import extract_questions_from_pdf
from backend.db import SessionLocal
from backend.models import Question

logging.basicConfig(level=logging.INFO, format='%(message)s')

pdf_path = "English-Compulsory-X-Paper-I-2025.pdf"

print("="*70)
print("TEST: COMPLETE UPLOAD FLOW")
print("="*70)

# Step 1: Extract
print("\n1️⃣  EXTRACTION STEP")
print("-"*70)

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

questions = extract_questions_from_pdf(pdf_bytes)
print(f"✅ Extracted {len(questions)} questions")

# Show what we extracted
print("\n📋 First 3 extracted questions:")
for i, q in enumerate(questions[:3], 1):
    print(f"\nQ{i}:")
    print(f"  Question: {q['question'][:50]}...")
    print(f"  Options: {q['options']}")
    print(f"  Answer: {q.get('correct_option')}")
    print(f"  Explanation: {q.get('explanation', 'N/A')[:50]}")

# Step 2: Save to database
print("\n\n2️⃣  DATABASE SAVE STEP")
print("-"*70)

db = SessionLocal()

# Clear old questions from this file
old_count = db.query(Question).filter(Question.source_file == pdf_path).count()
if old_count > 0:
    print(f"⚠️  Clearing {old_count} old questions from database...")
    db.query(Question).filter(Question.source_file == pdf_path).delete()
    db.commit()

# Save new questions
saved = 0
for i, record in enumerate(questions, 1):
    try:
        question = Question(
            question=record.get("question"),
            options=record.get("options", []),
            correct_option=record.get("correct_option"),
            explanation=record.get("explanation", ""),
            source_file=pdf_path,
            page_no=record.get("page_no"),
            image_data=None,
            image_type=None,
        )
        db.add(question)
        saved += 1
        print(f"✅ Q{i}: Saved with answer={record.get('correct_option')}")
    except Exception as e:
        print(f"❌ Q{i}: Failed - {str(e)}")

db.commit()
print(f"\n✅ Saved {saved} questions to database")

# Step 3: Verify from database
print("\n\n3️⃣  VERIFICATION STEP")
print("-"*70)

db_questions = db.query(Question).filter(Question.source_file == pdf_path).all()
print(f"✅ Retrieved {len(db_questions)} questions from database")

print("\n📋 First 3 questions from database:")
for i, q in enumerate(db_questions[:3], 1):
    print(f"\nQ{i}:")
    print(f"  Question: {q.question[:50]}...")
    print(f"  Options: {q.options}")
    print(f"  Answer: {q.correct_option}")
    print(f"  Explanation: {q.explanation[:50] if q.explanation else 'N/A'}")

# Step 4: Check via to_dict (what API returns)
print("\n\n4️⃣  API RESPONSE STEP")
print("-"*70)

print("\n📋 First 3 questions as API would return them:")
for i, q in enumerate(db_questions[:3], 1):
    q_dict = q.to_dict()
    print(f"\nQ{i}:")
    print(f"  Question: {q_dict['question'][:50]}...")
    print(f"  Options: {q_dict['options']}")
    print(f"  Answer: {q_dict['correct_option']}")
    print(f"  Image URL: {q_dict.get('image_url', 'None')}")

db.close()

print("\n" + "="*70)
print("✅ TEST COMPLETE")
print("="*70)
