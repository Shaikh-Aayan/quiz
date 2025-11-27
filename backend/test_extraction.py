#!/usr/bin/env python3
"""Test script to debug MCQ extraction issues."""

import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from extractor import extract_questions_from_pdf

def test_extraction():
    """Test extraction with the sample PDF."""
    pdf_path = Path("E:/ACCA-MCQ-Website/sample_mcqs.pdf")
    
    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return
    
    logger.info(f"Testing extraction with: {pdf_path}")
    logger.info(f"File size: {pdf_path.stat().st_size} bytes")
    
    try:
        # Read PDF
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        logger.info(f"Read {len(pdf_bytes)} bytes from PDF")
        
        # Extract questions
        questions = extract_questions_from_pdf(pdf_bytes)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"EXTRACTION RESULTS")
        logger.info(f"{'='*80}")
        logger.info(f"Total questions extracted: {len(questions)}")
        
        if questions:
            logger.info(f"\n{'='*80}")
            logger.info("DETAILED RESULTS:")
            logger.info(f"{'='*80}\n")
            
            for idx, q in enumerate(questions, 1):
                logger.info(f"Question {idx}:")
                logger.info(f"  Question: {q.get('question', 'N/A')[:100]}")
                logger.info(f"  Options: {len(q.get('options', []))} options")
                for opt_idx, opt in enumerate(q.get('options', []), 0):
                    logger.info(f"    {chr(65+opt_idx)}) {opt[:60]}")
                logger.info(f"  Correct: {q.get('correct_option', 'N/A')}")
                logger.info(f"  Explanation: {q.get('explanation', 'N/A')[:80]}")
                logger.info("")
            
            # Check for issues
            logger.info(f"\n{'='*80}")
            logger.info("ISSUE DETECTION:")
            logger.info(f"{'='*80}\n")
            
            # Check for duplicates
            questions_text = [q['question'] for q in questions]
            unique_questions = set(questions_text)
            if len(questions_text) != len(unique_questions):
                logger.warning(f"⚠️ DUPLICATES DETECTED: {len(questions_text)} total, {len(unique_questions)} unique")
                for q_text in questions_text:
                    if questions_text.count(q_text) > 1:
                        logger.warning(f"   Duplicated: {q_text[:60]}")
            else:
                logger.info("✅ No duplicates detected")
            
            # Check for missing first characters
            logger.info("\nChecking for missing first characters:")
            for idx, q in enumerate(questions, 1):
                q_text = q.get('question', '')
                if q_text and q_text[0].isspace():
                    logger.warning(f"⚠️ Q{idx} starts with space: '{q_text[:20]}'")
                elif q_text and not q_text[0].isalpha() and not q_text[0].isdigit():
                    logger.warning(f"⚠️ Q{idx} starts with special char: '{q_text[:20]}'")
                else:
                    logger.info(f"✅ Q{idx} OK: '{q_text[:40]}'")
            
            # Save to JSON for inspection
            output_file = Path(__file__).parent / "test_extraction_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            logger.info(f"\n✅ Results saved to: {output_file}")
        else:
            logger.warning("No questions extracted!")
            
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_extraction()
