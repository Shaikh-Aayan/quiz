#!/usr/bin/env python3
"""Deep analysis of PDF structure"""

import fitz
import re

pdf_path = "Physics-X-Paper-I-2025.pdf"
doc = fitz.open(pdf_path)

print("="*70)
print("DEEP PDF ANALYSIS")
print("="*70)

# Check each page
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    
    print(f"\n📄 PAGE {page_num + 1}:")
    print(f"   Text length: {len(text)} chars")
    print(f"   Question marks: {text.count('?')}")
    print(f"   Lines: {len(text.split(chr(10)))}")
    
    # Check for images
    image_list = page.get_images()
    print(f"   Images: {len(image_list)}")
    
    # Show first 300 chars
    print(f"\n   First 300 chars:")
    print(f"   {text[:300]}")
    print()

# Check if PDF is image-based
print("\n" + "="*70)
print("PDF TYPE CHECK:")
print("="*70)

total_text = ""
total_images = 0
for page_num in range(len(doc)):
    page = doc[page_num]
    total_text += page.get_text()
    total_images += len(page.get_images())

print(f"Total text chars: {len(total_text)}")
print(f"Total images: {total_images}")

if total_images > 0:
    print("\n⚠️  PDF contains images - likely scanned/image-based")
    print("    Need OCR (Tesseract) to extract text from images")
else:
    print("\n✓ PDF is text-based")

# Look for question numbering patterns
print("\n" + "="*70)
print("QUESTION NUMBERING PATTERNS:")
print("="*70)

# Find all lines that might be questions
lines = total_text.split('\n')
potential_questions = []

for i, line in enumerate(lines):
    # Check for question patterns
    if re.match(r'^\s*\d+\s*[.)]', line) and len(line) > 10:
        potential_questions.append((i, line[:80]))
    elif '?' in line and len(line) > 10:
        potential_questions.append((i, line[:80]))

print(f"Found {len(potential_questions)} potential question lines")
print("\nFirst 20:")
for line_num, text in potential_questions[:20]:
    print(f"  Line {line_num}: {text}...")

# Check for option patterns
print("\n" + "="*70)
print("OPTION PATTERNS:")
print("="*70)

option_count = 0
for line in lines:
    if re.match(r'^\s*[A-D]\s*[.)]', line):
        option_count += 1

print(f"Lines starting with A), B), C), D): {option_count}")

# Summary
print("\n" + "="*70)
print("SUMMARY:")
print("="*70)
print(f"Pages: {len(doc)}")
print(f"Total text: {len(total_text)} chars")
print(f"Total images: {total_images}")
print(f"Question marks: {total_text.count('?')}")
print(f"Potential questions: {len(potential_questions)}")
print(f"Option lines: {option_count}")
print(f"\n⚠️  ISSUE: PDF says 40 questions but only {total_text.count('?')} have '?'")
print(f"⚠️  ISSUE: Only {len(potential_questions)} potential question lines found")
print(f"\n💡 SOLUTION: PDF is likely image-based or has non-standard formatting")
print(f"💡 SOLUTION: Need to use Tesseract OCR on page images")
