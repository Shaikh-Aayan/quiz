#!/usr/bin/env python3
"""Debug script to see what text is extracted from PDF."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))

from extractor import clean_text
import fitz
import io

pdf_path = Path("E:/ACCA-MCQ-Website/sample_mcqs.pdf")

with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

print("=" * 80)
print("RAW TEXT EXTRACTION")
print("=" * 80)

# Try PyMuPDF
print("\n1. PyMuPDF Extraction:")
print("-" * 80)
try:
    doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
    text_pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        text_pages.append(text)
    pymupdf_text = "\n\n".join(text_pages)
    print(f"Extracted {len(pymupdf_text)} characters")
    print("\nContent:")
    print(pymupdf_text)
except Exception as e:
    print(f"Failed: {e}")
    pymupdf_text = ""

print("\n" + "=" * 80)
print("CLEANED TEXT")
print("=" * 80)
cleaned = clean_text(pymupdf_text)
print(f"Cleaned to {len(cleaned)} characters")
print("\nContent:")
print(cleaned)

print("\n" + "=" * 80)
print("QUESTIONS FOUND")
print("=" * 80)
lines = cleaned.split('\n')
for i, line in enumerate(lines):
    if '?' in line:
        print(f"Line {i}: {line}")
