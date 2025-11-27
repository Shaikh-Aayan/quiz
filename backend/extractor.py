import io
import re
import logging
import json
import time
from typing import List, Dict, Tuple, Optional, Union, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports
try:
    import fitz  # PyMuPDF
    import pdfplumber
    from pdfminer.high_level import extract_text
    from pdf2image import convert_from_bytes
    import pytesseract
    from PIL import Image, UnidentifiedImageError
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    import pdftotext
    PDF_LIBS_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Some PDF processing libraries not available: {str(e)}")
    PDF_LIBS_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors."""
    pass

def is_pdf_corrupted(file_bytes: bytes) -> bool:
    """Check if the PDF is corrupted."""
    try:
        with io.BytesIO(file_bytes) as f:
            # Try to open with PyMuPDF
            doc = fitz.open(stream=f, filetype="pdf")
            # Check if document is encrypted
            if doc.is_encrypted:
                return True
            # Check if we can get page count
            _ = len(doc)
            return False
    except Exception as e:
        logger.warning(f"PDF validation failed: {str(e)}")
        return True

def try_pdfminer_extract(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfminer.six with improved error handling."""
    if not PDF_LIBS_AVAILABLE:
        raise ImportError("PDF processing libraries are not installed")
        
    try:
        with io.BytesIO(file_bytes) as file_stream:
            # Try with layout analysis first
            try:
                # Create a PDF parser object
                parser = PDFParser(file_stream)
                # Create a PDF document object
                doc = PDFDocument(parser)
                
                if not doc.is_extractable:
                    raise PDFExtractionError("PDF text is not extractable")
                
                # Create a PDF resource manager
                rsrcmgr = PDFResourceManager()
                
                # Create a string buffer to store the extracted text
                text_stream = io.StringIO()
                
                # Create a text converter
                device = TextConverter(
                    rsrcmgr=rsrcmgr,
                    outfp=text_stream,
                    laparams=LAParams(
                        line_margin=0.5,
                        word_margin=0.1,
                        char_margin=2.0,
                        line_overlap=0.5,
                        detect_vertical=True,
                        all_texts=True
                    )
                )
                
                # Create a PDF page interpreter
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                
                # Process each page
                for page in PDFPage.create_pages(doc):
                    interpreter.process_page(page)
                
                # Get the extracted text
                text = text_stream.getvalue()
                
                # Clean up
                device.close()
                text_stream.close()
                
                return text.strip()
                
            except Exception as e:
                logger.warning(f"PDFMiner extraction with layout failed: {str(e)}")
                # Fallback to simple extraction
                file_stream.seek(0)
                return extract_text(file_stream).strip()
                
    except Exception as e:
        logger.error(f"PDF extraction failed: {str(e)}")
        raise PDFExtractionError(f"Failed to extract text from PDF: {str(e)}")

def ocr_from_pdf_bytes(file_bytes: bytes, dpi: int = 200) -> str:
    """Extract text from PDF using OCR with improved error handling and performance."""
    if not PDF_LIBS_AVAILABLE:
        raise ImportError("PDF processing libraries are not installed")
    
    text_pages = []
    try:
        # Try to convert PDF to images
        try:
            images = convert_from_bytes(
                file_bytes,
                dpi=dpi,
                fmt='jpeg',
                thread_count=4,
                grayscale=True,
                size=(1654, 2339)
            )
        except Exception as pdf_convert_err:
            # Poppler might not be installed, try without it
            logger.warning(f"PDF conversion with poppler failed: {str(pdf_convert_err)}")
            logger.info("Attempting OCR without poppler...")
            
            # Try using PyMuPDF instead
            try:
                import fitz
                doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
                images = []
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    images.append(img)
            except Exception as fitz_err:
                logger.error(f"PyMuPDF conversion also failed: {str(fitz_err)}")
                raise PDFExtractionError(f"Could not convert PDF to images. Poppler may not be installed: {str(pdf_convert_err)}")
        
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        
        for img in images:
            try:
                # Preprocess image for better OCR
                img = img.convert('L')  # Convert to grayscale
                
                # Enhance image for better OCR
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(2.0)  # Increase contrast
                
                # Perform OCR
                txt = pytesseract.image_to_string(img, config=custom_config)
                if txt.strip():
                    text_pages.append(txt.strip())
                
            except Exception as img_err:
                logger.warning(f"Error processing image: {str(img_err)}")
                continue
        
        if not text_pages:
            raise PDFExtractionError("No text could be extracted from PDF using OCR")
                
        return "\n\n".join(text_pages)
        
    except PDFExtractionError:
        raise
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise PDFExtractionError(f"OCR processing failed: {str(e)}")

def clean_text(text: str) -> str:
    """Clean and normalize text for better parsing."""
    if not text:
        return ""
    
    # Normalize line endings and whitespace
    text = ' '.join(text.split())
    
    # Remove common OCR artifacts
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize quotes and dashes
    text = text.replace('"', "''").replace('`', "'").replace('“', "''").replace('”', "''")
    text = text.replace('–', '-').replace('—', '-')
    
    return text.strip()

def parse_mcqs_from_text(text: str) -> List[Dict]:
    """Extract MCQs with ultra-robust parsing - handles any format."""
    if not text or len(text) < 30:
        return []

    # Clean and normalize text
    text = clean_text(text)

    # Ensure options/answers land on their own lines even if PDF flattened everything
    text = re.sub(r'(?:\s*)([A-E][\.\)\:])', r'\n\1', text)
    
    results = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # SIMPLE: Check if line looks like a question
        is_question = (
            re.match(r'^(Q\d+|Question\s+\d+|\d+[\.\)]|What|Which|How|Why|Where|When|Who|True|False|Can|Does|Is|Are)', line, re.IGNORECASE) or
            ('?' in line and len(line) > 10) or
            (len(line) > 40 and not re.match(r'^[A-E][\.\)\:]', line))
        )
        
        if not is_question:
            i += 1
            continue
        
        # Clean question
        question_text = re.sub(r'^(Q\d+[\.\)]?\s*|Question\s+\d+[\.\)]?\s*|\d+[\.\)]\s*)', '', line, flags=re.IGNORECASE).strip()
        if len(question_text) < 5:
            i += 1
            continue
        
        # Collect options
        options = []
        answer_idx = None
        j = i + 1
        
        while j < len(lines) and len(options) < 10:
            opt_line = lines[j]
            if not opt_line:
                j += 1
                continue
            
            # Match option: A) text, (A) text, A. text, etc.
            match = re.match(r'^[(\s]*([A-E])[)\.\:\s]+(.+)$', opt_line, re.IGNORECASE)
            if match:
                opt_text = match.group(2).strip()
                if opt_text and len(opt_text) > 1 and not re.match(r'^(Answer|Correct|Key|Q\d+)', opt_text, re.IGNORECASE):
                    options.append(opt_text)
                    if '*' in opt_line or '✓' in opt_line:
                        answer_idx = len(options) - 1
                    j += 1
                    continue
            
            # Check for answer key line
            if re.search(r'^(Answer|Correct|Key|Ans)\s*[\:\=]?\s*([A-E])', opt_line, re.IGNORECASE):
                ans_match = re.search(r'([A-E])', opt_line, re.IGNORECASE)
                if ans_match:
                    answer_idx = ord(ans_match.group(1).upper()) - ord('A')
                break
            
            # Stop if next question
            if re.match(r'^(Q\d+|Question\s+\d+|\d+[\.\)])', opt_line, re.IGNORECASE) and j > i + 1:
                break
            
            j += 1
        
        # Add if valid
        if question_text and len(options) >= 2:
            if answer_idx is None or answer_idx >= len(options):
                answer_idx = None
            
            results.append({
                'question': question_text,
                'options': options[:5],  # Max 5 options
                'correct_option': answer_idx
            })
            logger.info(f"✅ Q: {question_text[:40]}... | Options: {len(options)}")
        
        i = j if j > i + 1 else i + 1
    
    logger.info(f"✅ Extracted {len(results)} questions")
    return results

def fallback_block_parser(text: str) -> List[Dict]:
    """Last-resort parser that groups blocks of text into MCQs."""
    blocks: List[List[str]] = []
    current_block: List[str] = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    for line in lines:
        if re.match(r'^(Q\d+|Question\s+\d+|\d+[\.\)]\s|What|Which|How|Why|Where|When|Who)', line, re.IGNORECASE) and current_block:
            blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)

    if current_block:
        blocks.append(current_block)

    results = []
    for block in blocks:
        if not block:
            continue
        question = block[0]
        options: List[str] = []
        answer_idx = None
        current_opt = None

        for line in block[1:]:
            opt_match = re.match(r'^([A-E])\s*[\.\)\:]*\s*(.*)$', line, re.IGNORECASE)
            if opt_match and opt_match.group(2):
                if current_opt is not None and current_opt[1]:
                    options.append(current_opt[1].strip())
                current_opt = (opt_match.group(1).upper(), opt_match.group(2).strip())
            elif re.search(r'^(Answer|Correct|Key|Ans)', line, re.IGNORECASE):
                ans_match = re.search(r'([A-E])', line, re.IGNORECASE)
                if ans_match:
                    answer_idx = ord(ans_match.group(1).upper()) - ord('A')
            else:
                if current_opt is not None:
                    current_opt = (current_opt[0], current_opt[1] + ' ' + line)

        if current_opt is not None and current_opt[1]:
            options.append(current_opt[1].strip())

        if question and len(options) >= 2:
            if answer_idx is None or answer_idx >= len(options):
                answer_idx = None
            results.append({
                'question': re.sub(r'^(Q\d+[\.\)]\s*|\d+[\.\)]\s*)', '', question).strip(),
                'options': options,
                'correct_option': answer_idx
            })

    return results


def aggressive_parser(text: str) -> List[Dict]:
    """Ultra-aggressive parser for extremely tough PDFs - splits on any option marker."""
    results = []
    
    # Split on option markers (A), B), C), etc. - very aggressive
    parts = re.split(r'(?i)(?:^|\s)([A-E])\s*[\.\)\:]\s*', text, flags=re.MULTILINE)
    
    if len(parts) < 3:
        return []
    
    question_text = parts[0].strip()
    if len(question_text) < 10:
        question_text = ""
    
    options = []
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            opt_text = parts[i + 1].strip()
            # Take first 200 chars of option (avoid taking next question)
            opt_text = re.split(r'(?i)(?:^|\s)([A-E])\s*[\.\)\:]', opt_text)[0].strip()
            opt_text = opt_text[:200].strip()
            if opt_text and len(opt_text) > 2:
                options.append(opt_text)
    
    if question_text and len(options) >= 2:
        results.append({
            'question': question_text,
            'options': options[:5],  # Max 5 options
            'correct_option': None
        })
    
    return results

def extract_questions_from_pdf(file_bytes: bytes, skip_ocr: bool = False) -> List[Dict]:
    """Main function to extract questions from PDF using multiple methods."""
    if not PDF_LIBS_AVAILABLE:
        logger.error("Required PDF processing libraries are not installed")
        return []
        
    def extract_with_pymupdf(file_bytes: bytes) -> str:
        """Extract text from PDF using PyMuPDF with improved text extraction."""
        try:
            doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
            text_pages = []
            
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    # Try different text extraction methods
                    text = page.get_text("text")  # 'text' mode for better layout
                    if not text.strip():
                        # Fallback to raw text extraction
                        text = page.get_text("blocks")
                        if text:
                            text = "\n".join(block[4] for block in text if block[4].strip())
                    
                    if text.strip():
                        text_pages.append(text.strip())
                        
                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1} with PyMuPDF: {str(e)}")
                    continue
            
            return "\n\n".join(text_pages) if text_pages else ""
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {str(e)}")
            return ""

    def extract_with_pdfminer(file_bytes: bytes) -> str:
        """Fallback extraction using pdfminer.six."""
        try:
            from pdfminer.high_level import extract_text
            return extract_text(io.BytesIO(file_bytes))
        except Exception as e:
            logger.error(f"PDFMiner extraction failed: {str(e)}")
            return ""

    try:
        logger.info("Starting PDF extraction process...")
        
        # Try PyMuPDF first (fastest and most reliable)
        logger.info("Trying PyMuPDF extraction...")
        text = extract_with_pymupdf(file_bytes)
        
        # If text is too short or seems incomplete, try pdfminer
        if not text or len(text.strip()) < 100:
            logger.info("Text too short, trying PDFMiner...")
            text = extract_with_pdfminer(file_bytes)
        
        # If still no luck, try OCR (unless skipped)
        if (not text or len(text.strip()) < 50) and not skip_ocr:
            logger.info("All text extraction methods failed, trying OCR...")
            text = ocr_from_pdf_bytes(file_bytes)
        
        if not text or not text.strip():
            logger.error("❌ Failed to extract text from PDF")
            return []
        
        # Clean and normalize the extracted text
        logger.info("Cleaning and normalizing extracted text...")
        text = clean_text(text)
        
        # Try Groq-based extraction first (most reliable when it works)
        logger.info("Trying Groq-based extraction...")
        mcqs = validate_and_structure_with_groq(text)
        
        if mcqs:
            logger.info(f"✅ Extracted {len(mcqs)} questions using Groq")
            return mcqs
            
        logger.info("Groq extraction failed or returned no questions, falling back to rule-based parsers...")
        
        # Parse the extracted text into MCQs using multiple parsers
        all_mcqs = []
        
        # Try each parser and collect results
        parsers = [
            ("Primary Parser", parse_mcqs_from_text),
            ("Fallback Parser", fallback_block_parser),
            ("Aggressive Parser", aggressive_parser)
        ]
        
        for parser_name, parser_func in parsers:
            try:
                logger.info(f"Trying {parser_name}...")
                parsed_mcqs = parser_func(text)
                if parsed_mcqs:
                    logger.info(f"✅ {parser_name} found {len(parsed_mcqs)} MCQs")
                    all_mcqs.extend(parsed_mcqs)
            except Exception as e:
                logger.warning(f"{parser_name} failed: {str(e)}")
        
        # If we found MCQs with any parser, use them
        if all_mcqs:
            # Deduplicate MCQs based on question text
            unique_mcqs = {}
            for mcq in all_mcqs:
                q = mcq['question'].strip()
                if q and q not in unique_mcqs:
                    unique_mcqs[q] = mcq
            
            mcqs = list(unique_mcqs.values())
            logger.info(f"✅ Extracted {len(mcqs)} unique MCQs from text")
            
            # Try to identify correct answers for any questions that don't have them
            for mcq in mcqs:
                if mcq.get('correct_option') is None or mcq['correct_option'] >= len(mcq['options']):
                    try:
                        mcq['correct_option'] = identify_correct_answer_with_groq(
                            mcq['question'], 
                            mcq['options']
                        )
                    except Exception as e:
                        logger.warning(f"Failed to identify correct answer: {str(e)}")
                        mcq['correct_option'] = 0  # Default to first option
            
            return mcqs
        
        logger.warning("❌ No MCQs could be extracted with any parser")
        return []

def identify_correct_answer_with_groq(question: str, options: List[str]) -> int:
    """Use Groq to identify the correct answer for a multiple-choice question."""
    try:
        from groq_ai import groq_generate_explanation
        
        options_str = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""You are an expert at answering multiple-choice questions. 
For the following question, select the SINGLE BEST answer from the given options.

Question: {question}

Options:
{options_str}

INSTRUCTIONS:
1. Analyze the question and all options carefully
2. If the question is unclear or lacks sufficient information, make your best educated guess
3. Return ONLY the letter of the correct answer (A, B, C, etc.) in this exact format:
   ANSWER: X
   (where X is the letter of the correct option)
"""
        
        response = groq_generate_explanation(prompt).strip()
        logger.info(f"🤖 Groq identified answer: {response}")
        
        # Extract the answer using a more robust pattern
        match = re.search(r'ANSWER:\s*([A-Z])', response, re.IGNORECASE)
        if not match:
            # Try to find just a single letter in the response
            match = re.search(r'\b([A-Z])\b', response)
            
        if match:
            letter = match.group(1).upper()
            idx = ord(letter) - ord('A')
            if 0 <= idx < len(options):
                logger.info(f"✅ Answer identified: {letter} (index {idx})")
                return idx
        
        logger.warning(f"⚠️ Could not parse answer from: {response}")
        return 0  # Default to first option if can't determine
        
    except Exception as e:
        logger.error(f"❌ Error in identify_correct_answer_with_groq: {str(e)}")
        return 0  # Default to first option on error


def validate_and_structure_with_groq(raw_text: str) -> List[Dict]:
    """Use Groq to validate and structure MCQs from raw text using JSON with enhanced extraction."""
    try:
        from groq_ai import groq_generate_explanation
        import json
        
        # Take a larger chunk for better context
        text_chunk = raw_text[:5000]  # Increased from 3000 to 5000 for better context
        
        prompt = """You are an expert at extracting multiple-choice questions from text. 
Extract ALL valid MCQs from the following text and format them as a JSON array.

IMPORTANT INSTRUCTIONS:
1. Extract EVERY question you find, even if some information is missing
2. Each question MUST have at least 2 options
3. The 'correct' field MUST be the 0-based index of the correct answer
4. If the correct answer isn't marked, make your best educated guess
5. Clean up the text - remove any question numbers, bullet points, or extra whitespace
6. If an option starts with a letter and parenthesis (like 'A)'), remove that prefix
7. If the text contains answers separately, match them to the correct questions

OUTPUT FORMAT:
[
  {
    "question": "What is the capital of France?",
    "options": [
      "Paris",
      "London",
      "Berlin",
      "Madrid"
    ],
    "correct": 0,
    "explanation": "Paris is the capital of France."
  }
]

EXAMPLES OF HANDLING DIFFERENT FORMATS:
1. If you see:
   "1. What is 2+2?\nA) 3\nB) 4\nC) 5\nAnswer: B"
   
   Convert to:
   {
     "question": "What is 2+2?",
     "options": ["3", "4", "5"],
     "correct": 1,
     "explanation": "2+2 equals 4."
   }

2. If you see questions and answers separately:
   "Questions:\n1. Capital of France?\n2. 2+2?\nAnswers: 1. A 2. B"
   
   Convert to separate question objects with correct answers.

TEXT TO PROCESS:
""" + text_chunk + """

IMPORTANT: Return ONLY valid JSON. No other text or explanation."""

        logger.info("📤 Sending to Groq for enhanced MCQ extraction...")
        
        # Try up to 3 times to get a valid response
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = groq_generate_explanation(prompt)
                logger.info(f"📥 Groq response length: {len(response)} chars")
                
                # Clean up the response to make it valid JSON if needed
                response = response.strip()
                if not response.startswith('['):
                    # Try to find the JSON array in the response
                    json_match = re.search(r'\[(.|\n)*\]', response)
                    if json_match:
                        response = json_match.group(0)
                
                # Parse the JSON
                parsed = json.loads(response)
                if not isinstance(parsed, list):
                    raise ValueError("Response is not a JSON array")
                
                questions = []
                for item in parsed:
                    try:
                        q_text = item.get('question', '').strip()
                        options = [str(opt).strip() for opt in item.get('options', [])]
                        
                        # Clean options (remove A), B), etc. if present)
                        cleaned_options = []
                        for opt in options:
                            # Remove leading A), B), etc.
                            opt = re.sub(r'^[A-Za-z][\.\)\s]*', '', opt).strip()
                            # Remove any remaining leading numbers or bullets
                            opt = re.sub(r'^[\d\s\.\)\-•]*', '', opt).strip()
                            if opt:  # Only add non-empty options
                                cleaned_options.append(opt)
                        
                        options = cleaned_options
                        
                        # Validate question and options
                        if not q_text or len(options) < 2:
                            logger.warning(f"⚠️ Skipping invalid question: {q_text[:50]}...")
                            continue
                        
                        # Handle correct answer
                        correct = item.get('correct')
                        if correct is None or not isinstance(correct, int) or correct >= len(options):
                            logger.info(f"❓ No valid answer for: {q_text[:50]}... Using Groq to identify...")
                            correct = identify_correct_answer_with_groq(q_text, options)
                        
                        questions.append({
                            'question': q_text,
                            'options': options[:10],  # Allow up to 10 options
                            'correct_option': correct if correct is not None else 0,
                            'explanation': item.get('explanation', '')
                        })
                        
                        logger.info(f"✅ Extracted: {q_text[:60]}... | Options: {len(options)} | Correct: {correct}")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing question: {str(e)}")
                        continue
                
                if questions:
                    logger.info(f"✅ Successfully extracted {len(questions)} questions")
                    return questions
                
                logger.warning("⚠️ No valid questions found in the response")
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ Attempt {attempt + 1}/{max_retries}: JSON parse error: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"❌ Failed to parse Groq response after {max_retries} attempts")
                    logger.debug(f"Response was: {response[:500]}...")
                continue
            except Exception as e:
                logger.error(f"❌ Unexpected error during extraction: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    raise
        
        return []
        
    except Exception as e:
        logger.error(f"❌ Groq extraction failed: {str(e)}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return []

def identify_correct_answer_with_groq(question: str, options: List[str]) -> int:
    """Use Groq to identify the correct answer for a multiple-choice question."""
    try:
        from groq_ai import groq_generate_explanation
        
        options_str = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""You are an expert at answering multiple-choice questions. 
For the following question, select the SINGLE BEST answer from the given options.

Question: {question}

Options:
{options_str}

INSTRUCTIONS:
1. Analyze the question and all options carefully
2. If the question is unclear or lacks sufficient information, make your best educated guess
3. Return ONLY the letter of the correct answer (A, B, C, etc.) in this exact format:
   ANSWER: X
   (where X is the letter of the correct option)
"""
        
        response = groq_generate_explanation(prompt).strip()
        logger.info(f"🤖 Groq identified answer: {response}")
        
        # Extract the answer using a more robust pattern
        match = re.search(r'ANSWER:\s*([A-Z])', response, re.IGNORECASE)
        if not match:
            # Try to find just a single letter in the response
            match = re.search(r'\b([A-Z])\b', response)
            
        if match:
            letter = match.group(1).upper()
            idx = ord(letter) - ord('A')
            if 0 <= idx < len(options):
                logger.info(f"✅ Answer identified: {letter} (index {idx})")
                return idx
        
        logger.warning(f"⚠️ Could not parse answer from: {response}")
        return 0  # Default to first option if can't determine
        
    except Exception as e:
        logger.error(f"❌ Error in identify_correct_answer_with_groq: {str(e)}")
        return 0  # Default to first option on error
