#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean up old questions from database"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.db import SessionLocal
from backend.models import Question

print("="*70)
print("🧹 DATABASE CLEANUP")
print("="*70)

db = SessionLocal()

# Get count before
count_before = db.query(Question).count()
print(f"\n📊 Questions in database BEFORE cleanup: {count_before}")

if count_before > 0:
    print("\n📋 Questions to be deleted:")
    questions = db.query(Question).all()
    for q in questions:
        print(f"  - {q.source_file}: {q.question[:50]}...")
    
    # Delete all
    print(f"\n🗑️  Deleting all {count_before} questions...")
    db.query(Question).delete()
    db.commit()
    
    count_after = db.query(Question).count()
    print(f"✅ Questions in database AFTER cleanup: {count_after}")
else:
    print("\n✅ Database is already clean!")

db.close()

print("\n" + "="*70)
print("✅ CLEANUP COMPLETE")
print("="*70)
print("\nNow you can upload fresh PDFs and they will be saved correctly!")
