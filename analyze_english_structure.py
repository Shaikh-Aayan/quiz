#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze English PDF structure to identify listening vs reading sections"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz
import re

pdf_path = "English-Compulsory-X-Paper-I-2025.pdf"

doc = fitz.open(pdf_path)
text = ""

for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text() + "\n"

lines = text.split('\n')

print("="*70)
print("ANALYZING ENGLISH PDF STRUCTURE")
print("="*70)
print()

# Find sections
current_section = None
section_questions = {}

for i, line in enumerate(lines):
    line = line.strip()
    
    # Detect section headers
    if 'listening' in line.lower():
        current_section = 'LISTENING'
        section_questions[current_section] = []
        print(f"📍 Found LISTENING section at line {i}")
    elif 'reading' in line.lower():
        current_section = 'READING'
        section_questions[current_section] = []
        print(f"📍 Found READING section at line {i}")
    elif 'writing' in line.lower():
        current_section = 'WRITING'
        section_questions[current_section] = []
        print(f"📍 Found WRITING section at line {i}")
    
    # Find question numbers
    if re.match(r'^\d+\.\s*', line):
        q_num = int(line.split('.')[0])
        if current_section:
            if current_section not in section_questions:
                section_questions[current_section] = []
            section_questions[current_section].append(q_num)

print()
print("="*70)
print("SECTION BREAKDOWN")
print("="*70)

for section, questions in section_questions.items():
    print(f"\n{section}: {len(questions)} questions")
    print(f"  Questions: {questions}")

print()
print("="*70)
print("RECOMMENDATION")
print("="*70)
if 'LISTENING' in section_questions:
    listening_qs = section_questions['LISTENING']
    print(f"\n⚠️  EXCLUDE {len(listening_qs)} listening questions: {listening_qs}")
    print("   (We don't have audio, so we can't answer these)")

if 'READING' in section_questions:
    reading_qs = section_questions['READING']
    print(f"\n✅ INCLUDE {len(reading_qs)} reading questions: {reading_qs}")
    print("   (We have text passages, Groq can identify answers)")

if 'WRITING' in section_questions:
    writing_qs = section_questions['WRITING']
    print(f"\n⚠️  EXCLUDE {len(writing_qs)} writing questions: {writing_qs}")
    print("   (Subjective, no single correct answer)")
