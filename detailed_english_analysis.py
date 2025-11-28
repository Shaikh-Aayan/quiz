#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detailed analysis of English PDF to find all questions and sections"""

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
print("DETAILED ENGLISH PDF ANALYSIS")
print("="*70)
print()

# Find all question numbers
all_questions = {}
for i, line in enumerate(lines):
    line_stripped = line.strip()
    match = re.match(r'^(\d+)\.\s*(.*?)$', line_stripped)
    if match:
        q_num = int(match.group(1))
        q_text = match.group(2)[:60]
        all_questions[q_num] = q_text
        print(f"Q{q_num}: {q_text}...")

print()
print("="*70)
print(f"TOTAL QUESTIONS FOUND: {len(all_questions)}")
print(f"Question numbers: {sorted(all_questions.keys())}")
print("="*70)

# Now find sections by looking for keywords
print()
print("SECTION DETECTION:")
print("="*70)

listening_section = False
reading_section = False
writing_section = False

for i, line in enumerate(lines):
    lower = line.lower()
    
    if 'listening' in lower and 'section' in lower:
        listening_section = True
        reading_section = False
        writing_section = False
        print(f"Line {i}: START LISTENING")
    elif 'reading' in lower and 'section' in lower:
        listening_section = False
        reading_section = True
        writing_section = False
        print(f"Line {i}: START READING")
    elif 'writing' in lower and 'section' in lower:
        listening_section = False
        reading_section = False
        writing_section = True
        print(f"Line {i}: START WRITING")
    
    # Show questions with their section
    match = re.match(r'^(\d+)\.\s*', line.strip())
    if match:
        q_num = int(match.group(1))
        section = "UNKNOWN"
        if listening_section:
            section = "LISTENING"
        elif reading_section:
            section = "READING"
        elif writing_section:
            section = "WRITING"
        print(f"  Q{q_num}: {section}")
