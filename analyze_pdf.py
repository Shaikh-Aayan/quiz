#!/usr/bin/env python3
"""Analyze the Physics PDF to understand its structure"""

import fitz
import re

pdf_path = "Physics-X-Paper-I-2025.pdf"

# Open PDF
doc = fitz.open(pdf_path)
print(f"📄 PDF: {pdf_path}")
print(f"📊 Pages: {len(doc)}")

# Extract all text
full_text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    full_text += text + "\n---PAGE BREAK---\n"

print(f"📝 Total characters: {len(full_text)}")
print(f"❓ Question marks: {full_text.count('?')}")

# Find question patterns
print("\n" + "="*60)
print("QUESTION PATTERNS FOUND:")
print("="*60)

# Pattern 1: Q1, Q2, Q3, etc.
q_pattern = re.findall(r'Q\d+', full_text)
print(f"\n✓ Q# pattern: {len(set(q_pattern))} unique")

# Pattern 2: 1., 2., 3., etc.
num_pattern = re.findall(r'^\d+\.', full_text, re.MULTILINE)
print(f"✓ Number pattern (1., 2., etc.): {len(num_pattern)}")

# Pattern 3: Lines with question marks
question_lines = [line for line in full_text.split('\n') if '?' in line and len(line) > 10]
print(f"✓ Lines with '?': {len(question_lines)}")

# Show first 20 lines with question marks
print("\n" + "="*60)
print("FIRST 20 QUESTIONS (lines with ?):")
print("="*60)
for i, line in enumerate(question_lines[:20], 1):
    print(f"\n{i}. {line[:100]}...")

# Look for answer patterns
print("\n" + "="*60)
print("ANSWER KEY PATTERNS:")
print("="*60)

answer_patterns = re.findall(r'(?:Answer|Ans|Key|Correct)\s*[:=]\s*([A-E])', full_text, re.IGNORECASE)
print(f"✓ Answer lines found: {len(answer_patterns)}")
if answer_patterns:
    print(f"  Answers: {answer_patterns[:20]}")

# Look for option patterns
print("\n" + "="*60)
print("OPTION PATTERNS:")
print("="*60)

# Find A), B), C), D), E) patterns
option_lines = re.findall(r'^[A-E]\)', full_text, re.MULTILINE)
print(f"✓ Option markers (A), B), etc.): {len(option_lines)}")

# Find • bullet patterns
bullet_lines = re.findall(r'^•', full_text, re.MULTILINE)
print(f"✓ Bullet points (•): {len(bullet_lines)}")

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print(f"Expected questions: 40")
print(f"Question marks found: {full_text.count('?')}")
print(f"Q# patterns: {len(set(q_pattern))}")
print(f"Lines with ?: {len(question_lines)}")

# Show sample of text
print("\n" + "="*60)
print("TEXT SAMPLE (first 1000 chars):")
print("="*60)
print(full_text[:1000])
