import io
import os
import re
import logging
import json
import time
import base64
from typing import List, Dict, Tuple, Optional, Union, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports - make them optional
PDF_LIBS_AVAILABLE = True
try:
    import fitz  # PyMuPDF
except ImportError:
    PDF_LIBS_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text
except ImportError:
    PDF_LIBS_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
except ImportError:
    PDF_LIBS_AVAILABLE = False

try:
    import pytesseract
except ImportError:
    PDF_LIBS_AVAILABLE = False

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    PDF_LIBS_AVAILABLE = False

# Optional imports that don't break if missing
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pdftotext
except ImportError:
    pdftotext = None

try:
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
except ImportError:
    pass

# Configure logging
logger = logging.getLogger(__name__)

class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors."""
    pass

def detect_paper_type(text: str) -> str:
    """Detect the type of exam paper"""
    text_lower = text.lower()
    
    if "physics" in text_lower or "simple harmonic" in text_lower or "acceleration" in text_lower:
        return "PHYSICS"
    elif "english" in text_lower or "listening" in text_lower or "reading" in text_lower:
        return "ENGLISH"
    elif "mathematics" in text_lower or "algebra" in text_lower:
        return "MATHEMATICS"
    else:
        return "GENERAL"

def parse_english_mcqs(text: str) -> List[Dict]:
    """
    Parse MCQs from English exam PDF.
    Excludes listening questions (no audio).
    Includes reading comprehension and writing questions (Groq can identify answers).
    """
    
    if not text or len(text) < 50:
        logger.debug("Text too short for English parser")
        return []
    
    results = []
    lines = text.split('\n')
    lines = [l.strip() for l in lines]
    
    # Track sections
    in_listening = False
    in_reading = False
    in_writing = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect section headers
        if 'listening' in line.lower() and 'section' in line.lower():
            in_listening = True
            in_reading = False
            in_writing = False
            logger.debug("Entered LISTENING section - will skip (no audio)")
            i += 1
            continue
        elif 'reading' in line.lower() and 'section' in line.lower():
            in_listening = False
            in_reading = True
            in_writing = False
            logger.debug("Entered READING section - will include")
            i += 1
            continue
        elif 'writing' in line.lower() and 'section' in line.lower():
            in_listening = False
            in_reading = False
            in_writing = True
            logger.debug("Entered WRITING section - will include (Groq can handle)")
            i += 1
            continue
        
        # Skip if in listening section only
        if in_listening:
            i += 1
            continue
        
        # Only process reading or writing sections
        if not (in_reading or in_writing):
            i += 1
            continue
        
        # Look for question number pattern
        q_match = re.match(r'^(\d+)\.\s*(.*?)$', line)
        
        if not q_match:
            i += 1
            continue
        
        q_num = int(q_match.group(1))
        first_line_text = q_match.group(2).strip()
        
        # Collect lines until next question number
        question_block_lines = []
        
        if first_line_text:
            question_block_lines.append(first_line_text)
        
        j = i + 1
        
        while j < len(lines):
            next_line = lines[j]
            
            # Stop if we hit another question number
            if re.match(r'^\d+\.\s*', next_line):
                break
            
            # Stop if we hit a section header
            if any(keyword in next_line.lower() for keyword in ['listening', 'reading', 'writing', 'section']):
                break
            
            if next_line.strip():
                question_block_lines.append(next_line)
            
            j += 1
        
        # Join all lines in the block
        question_block = ' '.join(question_block_lines)
        
        # Skip instructions and empty blocks
        if len(question_block) < 10 or any(keyword in question_block.lower() for keyword in 
               ['read each question', 'answer the questions', 'answer sheet', 'write anything', 'erase']):
            i = j
            continue
        
        # Extract options from the block
        option_pattern = r'([A-D])\.\s*([^A-D]*?)(?=(?:[A-D]\.|$))'
        option_matches = list(re.finditer(option_pattern, question_block))
        
        if len(option_matches) < 2:
            logger.debug(f"Q{q_num}: Not enough options found")
            i = j
            continue
        
        # Find where options start
        first_option_pos = option_matches[0].start()
        question_text = question_block[:first_option_pos].strip()
        
        # Extract options
        options = []
        for match in option_matches:
            opt_text = match.group(2).strip()
            opt_text = re.sub(r'\s+', ' ', opt_text)
            opt_text = opt_text.rstrip('.')
            
            if len(opt_text) > 2 and len(opt_text) < 200:
                options.append(opt_text)
        
        # Validate and add question
        if question_text and len(options) >= 2:
            # Try to identify correct answer using Groq (with retry logic)
            correct_option = None
            try:
                correct_option = identify_correct_answer_with_groq(question_text, options[:4])
            except Exception as e:
                logger.debug(f"Groq failed for Q{q_num}: {str(e)}")
            
            results.append({
                'question': question_text,
                'options': options[:4],
                'correct_option': correct_option,
                'explanation': ''
            })
            logger.info(f"✅ Q{q_num}: {question_text[:60]}... | {len(options)} options | Answer: {correct_option}")
        else:
            logger.debug(f"Q{q_num}: Invalid - text_len={len(question_text)} opts={len(options)}")
        
        i = j
    
    logger.info(f"✅ English parser extracted {len(results)} questions (reading + writing, excluded listening)")
    return results

def parse_physics_mcqs_improved(text: str) -> List[Dict]:
    """
    Parse MCQs from Physics exam PDF where options are embedded in question text.
    
    Format:
    1.
    Question text A. Option A B. Option B C. Option C D. Option D
    
    OR
    
    1. Question text A. Option A B. Option B C. Option C D. Option D
    
    This parser is optimized for exam PDFs with embedded options.
    """
    
    if not text or len(text) < 50:
        logger.debug("Text too short for physics parser")
        return []
    
    results = []
    lines = text.split('\n')
    lines = [l.strip() for l in lines]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for question number pattern: "1.", "2.", etc.
        # Match both "1." alone and "1. text"
        q_match = re.match(r'^(\d+)\.\s*(.*?)$', line)
        
        if not q_match:
            i += 1
            continue
        
        q_num = int(q_match.group(1))
        first_line_text = q_match.group(2).strip()
        
        # Collect lines until next question number
        question_block_lines = []
        
        # If there's text on the same line as the question number, add it
        if first_line_text:
            question_block_lines.append(first_line_text)
        
        j = i + 1
        
        while j < len(lines):
            next_line = lines[j]
            
            # Stop if we hit another question number
            if re.match(r'^\d+\.\s*', next_line):
                break
            
            if next_line.strip():
                question_block_lines.append(next_line)
            
            j += 1
        
        # Join all lines in the block
        question_block = ' '.join(question_block_lines)
        
        # Skip instructions
        if any(keyword in question_block.lower() for keyword in 
               ['read each question', 'answer the questions', 'answer sheet', 'calculator if you wish', 
                'write anything', 'erase the first', 'grid black out']):
            logger.debug(f"Skipping instruction Q{q_num}")
            i = j
            continue
        
        # Skip if too short
        if len(question_block) < 10:
            i = j
            continue
        
        # Extract options from the block
        # Pattern: text A. option B. option C. option D. option
        # Find all A., B., C., D. patterns
        option_pattern = r'([A-D])\.\s*([^A-D]*?)(?=(?:[A-D]\.|$))'
        option_matches = list(re.finditer(option_pattern, question_block))
        
        if len(option_matches) < 2:
            logger.debug(f"Q{q_num}: Not enough options found")
            i = j
            continue
        
        # Find where options start (first A.)
        first_option_pos = option_matches[0].start()
        question_text = question_block[:first_option_pos].strip()
        
        # Extract options
        options = []
        for match in option_matches:
            opt_letter = match.group(1)
            opt_text = match.group(2).strip()
            
            # Clean up option text
            opt_text = re.sub(r'\s+', ' ', opt_text)  # Normalize whitespace
            opt_text = opt_text.rstrip('.')  # Remove trailing period
            
            if len(opt_text) > 2 and len(opt_text) < 200:
                options.append(opt_text)
        
        # Validate and add question
        if question_text and len(options) >= 2:
            # Try to identify correct answer using Groq (with retry logic)
            correct_option = None
            try:
                correct_option = identify_correct_answer_with_groq(question_text, options[:4])
            except Exception as e:
                logger.debug(f"Groq failed for Q{q_num}: {str(e)}")
            
            results.append({
                'question': question_text,
                'options': options[:4],  # Max 4 options
                'correct_option': correct_option,
                'explanation': ''
            })
            logger.info(f"✅ Q{q_num}: {question_text[:60]}... | {len(options)} options | Answer: {correct_option}")
        else:
            logger.debug(f"Q{q_num}: Invalid - text_len={len(question_text)} opts={len(options)}")
        
        i = j
    
    logger.info(f"✅ Physics parser extracted {len(results)} questions")
    return results

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

def ocr_from_pdf_bytes(file_bytes: bytes, dpi: int = 300) -> str:
    """Extract text from PDF using OCR with improved error handling and performance."""
    if not PDF_LIBS_AVAILABLE:
        raise ImportError("PDF processing libraries are not installed")
    
    text_pages = []
    try:
        # Try to convert PDF to images
        try:
            logger.info(f"Converting PDF to images at {dpi} DPI...")
            images = convert_from_bytes(
                file_bytes,
                dpi=dpi,
                fmt='png',
                thread_count=4,
                grayscale=False  # Keep color for better OCR
            )
            logger.info(f"Successfully converted {len(images)} pages to images")
        except Exception as pdf_convert_err:
            # Poppler might not be installed, try without it
            logger.warning(f"PDF conversion with poppler failed: {str(pdf_convert_err)}")
            logger.info("Attempting OCR without poppler using PyMuPDF...")
            
            # Try using PyMuPDF instead
            try:
                import fitz
                doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
                images = []
                zoom_factor = dpi / 72  # Convert DPI to zoom factor
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    images.append(img)
                logger.info(f"Successfully converted {len(images)} pages using PyMuPDF")
            except Exception as fitz_err:
                logger.error(f"PyMuPDF conversion also failed: {str(fitz_err)}")
                raise PDFExtractionError(f"Could not convert PDF to images: {str(pdf_convert_err)}")
        
        # Configure Tesseract for better MCQ extraction
        custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        
        for page_num, img in enumerate(images):
            try:
                logger.info(f"Processing page {page_num + 1} with OCR...")
                
                # Preprocess image for better OCR
                img_rgb = img.convert('RGB')
                
                # Enhance image for better OCR
                from PIL import ImageEnhance, ImageFilter
                
                # Increase contrast
                enhancer = ImageEnhance.Contrast(img_rgb)
                img_rgb = enhancer.enhance(2.5)
                
                # Increase brightness slightly
                enhancer = ImageEnhance.Brightness(img_rgb)
                img_rgb = enhancer.enhance(1.1)
                
                # Sharpen image
                img_rgb = img_rgb.filter(ImageFilter.SHARPEN)
                
                # Perform OCR
                txt = pytesseract.image_to_string(img_rgb, config=custom_config)
                if txt.strip():
                    text_pages.append(txt.strip())
                    logger.info(f"Page {page_num + 1}: Extracted {len(txt)} characters")
                else:
                    logger.warning(f"Page {page_num + 1}: No text extracted")
                
            except Exception as img_err:
                logger.warning(f"Error processing page {page_num + 1}: {str(img_err)}")
                continue
        
        if not text_pages:
            raise PDFExtractionError("No text could be extracted from PDF using OCR")
        
        logger.info(f"OCR extraction complete: {len(text_pages)} pages processed")
        return "\n\n".join(text_pages)
        
    except PDFExtractionError:
        raise
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise PDFExtractionError(f"OCR processing failed: {str(e)}")

def clean_text(text: str) -> str:
    """Clean and normalize text for better parsing - preserves structure."""
    if not text:
        return ""
    
    # Remove common OCR artifacts but preserve line structure
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize quotes and dashes
    text = text.replace('"', "'").replace('`', "'").replace('"', "'").replace('"', "'")
    text = text.replace('–', '-').replace('—', '-')
    
    # Clean up excessive whitespace within lines but preserve line breaks
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove leading/trailing whitespace and excessive internal spaces
        line = re.sub(r'\s+', ' ', line).strip()
        if line:  # Only keep non-empty lines
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

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

def extract_images_from_pdf(file_bytes: bytes) -> Dict[int, Tuple[bytes, str]]:
    """
    Extract images from PDF and return as dict: {page_number: (image_bytes, image_type)}
    """
    images_by_page = {}
    
    try:
        doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            if image_list:
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Convert to PNG
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_bytes = pix.tobytes("png")
                        else:  # CMYK
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                            img_bytes = pix.tobytes("png")
                        
                        images_by_page[page_num] = (img_bytes, "png")
                        logger.info(f"✅ Extracted image from page {page_num + 1}")
                        break  # Take first image per page
                    except Exception as e:
                        logger.debug(f"Error extracting image from page {page_num}: {str(e)}")
                        continue
        
        logger.info(f"✅ Extracted {len(images_by_page)} images from PDF")
        return images_by_page
    
    except Exception as e:
        logger.warning(f"Image extraction failed: {str(e)}")
        return {}

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
        
        # Initialize text variable
        text = ""
        
        # Try PyMuPDF first (fastest and most reliable)
        logger.info("Trying PyMuPDF extraction...")
        try:
            text = extract_with_pymupdf(file_bytes)
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed, will try other methods: {str(e)}")
            text = ""  # Ensure text is reset if extraction fails
        
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
        
        # Extract images from PDF
        logger.info("Extracting images from PDF...")
        images_by_page = extract_images_from_pdf(file_bytes)
        
        # Detect paper type
        paper_type = detect_paper_type(text)
        logger.info(f"📋 Detected paper type: {paper_type}")
        
        # Use appropriate parser based on paper type
        extracted_mcqs = []
        
        if paper_type == "ENGLISH":
            logger.info("Using English parser (excludes listening/writing)...")
            extracted_mcqs = parse_english_mcqs(text)
        elif paper_type == "PHYSICS":
            logger.info("Using Physics parser...")
            extracted_mcqs = parse_physics_mcqs_improved(text)
        else:
            logger.info("Using Physics parser as default...")
            extracted_mcqs = parse_physics_mcqs_improved(text)
        
        if extracted_mcqs and len(extracted_mcqs) >= 5:
            logger.info(f"✅ Parser found {len(extracted_mcqs)} MCQs - using this")
            # Attach images to questions (if available)
            for i, mcq in enumerate(extracted_mcqs):
                if i in images_by_page:
                    img_bytes, img_type = images_by_page[i]
                    mcq['image_data'] = img_bytes
                    mcq['image_type'] = img_type
            return extracted_mcqs
        
        # Fallback: Try Groq-based extraction if specialized parser didn't find enough
        logger.info("Specialized parser found < 5 questions, trying Groq...")
        groq_mcqs = validate_and_structure_with_groq(text)
        
        if groq_mcqs and len(groq_mcqs) >= 5:
            logger.info(f"✅ Extracted {len(groq_mcqs)} questions using Groq")
            # Attach images to questions (if available)
            for i, mcq in enumerate(groq_mcqs):
                if i in images_by_page:
                    img_bytes, img_type = images_by_page[i]
                    mcq['image_data'] = img_bytes
                    mcq['image_type'] = img_type
            return groq_mcqs
        
        # Final fallback: Try primary parser only (NOT fallback parser - it adds garbage)
        logger.info("Groq found < 5 questions, trying primary parser...")
        all_mcqs = []
        
        try:
            logger.info("Trying Primary Parser...")
            parsed_mcqs = parse_mcqs_from_text(text)
            if parsed_mcqs:
                logger.info(f"✅ Primary Parser found {len(parsed_mcqs)} MCQs")
                all_mcqs.extend(parsed_mcqs)
        except Exception as e:
            logger.warning(f"Primary Parser failed: {str(e)}")
        
        # If we found MCQs with any parser, use them
        if all_mcqs:
            # Deduplicate MCQs based on question text (more intelligent deduplication)
            unique_mcqs = {}
            for mcq in all_mcqs:
                q = mcq['question'].strip()
                # Skip malformed questions (too long, contains multiple questions)
                if not q or len(q) < 5:
                    continue
                # Skip if question contains multiple question markers
                if q.count('?') > 1:
                    logger.warning(f"⚠️ Skipping malformed question with multiple markers: {q[:50]}")
                    continue
                # Skip if question contains newlines (sign of multiple questions merged)
                if '\n' in q:
                    logger.warning(f"⚠️ Skipping malformed question with newlines: {q[:50]}")
                    continue
                # Use first 100 chars as dedup key to handle slight variations
                dedup_key = q[:100].lower()
                if dedup_key not in unique_mcqs:
                    unique_mcqs[dedup_key] = mcq
            
            mcqs = list(unique_mcqs.values())
            logger.info(f"✅ Extracted {len(mcqs)} unique MCQs from text (deduplicated from {len(all_mcqs)})")
            
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
            
            # Attach images to questions (if available)
            for i, mcq in enumerate(mcqs):
                if i in images_by_page:
                    img_bytes, img_type = images_by_page[i]
                    mcq['image_data'] = img_bytes
                    mcq['image_type'] = img_type
            
            return mcqs
        
        logger.warning("❌ No MCQs could be extracted with any parser")
        return []
        
    except Exception as e:
        logger.error(f"❌ Error in extract_questions_from_pdf: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []


def validate_and_structure_with_groq(text: str) -> List[Dict]:
    """Use Groq to validate and structure MCQs from extracted text with enhanced accuracy."""
    try:
        from groq import Groq
        import os
        
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set, skipping Groq extraction")
            return []
        
        client = Groq(api_key=api_key)
        
        # Split text into chunks to avoid token limits
        max_chunk_size = 3000
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        all_questions = []
        
        for chunk_idx, text_chunk in enumerate(chunks):
            logger.info(f"Processing text chunk {chunk_idx + 1}/{len(chunks)}... ({len(text_chunk)} chars)")
            logger.debug(f"Chunk content preview: {text_chunk[:200]}...")
            
            prompt = f"""You are an expert MCQ extraction system. Your ONLY job is to extract ALL multiple-choice questions from the provided text and return them as valid JSON.

CRITICAL RULES (MUST FOLLOW - NO EXCEPTIONS):
1. Extract EVERY SINGLE question you find - be thorough and comprehensive - DO NOT SKIP ANY
2. Questions may be formatted in ANY way - adapt to all formats
3. ALWAYS return ONLY a valid JSON array - NOTHING ELSE, NO MARKDOWN, NO CODE BLOCKS
4. Each question MUST have these exact fields: question, options, correct_option, explanation
5. Count the questions in the text and ensure you extract that many in your response

RESPONSE FORMAT (MUST BE VALID JSON - NO MARKDOWN):
[
  {{
    "question": "Question text without numbers or prefixes",
    "options": ["Option 1", "Option 2", "Option 3"],
    "correct_option": 0,
    "explanation": "Why this answer is correct"
  }},
  {{
    "question": "Another question",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_option": 2,
    "explanation": "Explanation for this answer"
  }}
]

EXTRACTION RULES:
1. Remove ALL question prefixes: Q1, 1., Question 1, etc.
2. Remove ALL option markers: A), B), •, 1), -, etc.
3. Combine multi-line options into single lines
4. Trim ALL whitespace
5. Keep 2-6 options per question (remove if more than 6)
6. correct_option MUST be 0-based index (0=first, 1=second, etc.)

FINDING CORRECT ANSWERS (PRIORITY ORDER):
1. Look for explicit markers: "Answer: A", "Correct: B", "Key: C", "*", "✓"
2. If found, convert letter to 0-based index (A=0, B=1, C=2, D=3, etc.)
3. If NOT found, use your expert knowledge to determine the best answer
4. If completely uncertain, default to 0

EXAMPLES (FOLLOW EXACTLY):
Input: "1. What is 2+2?\nA) 3\nB) 4\nC) 5\nAnswer: B"
Output: {{"question": "What is 2+2?", "options": ["3", "4", "5"], "correct_option": 1, "explanation": "2+2 equals 4"}}

Input: "Q1: Capital of France?\n• Paris\n• London\n• Berlin"
Output: {{"question": "Capital of France?", "options": ["Paris", "London", "Berlin"], "correct_option": 0, "explanation": "Paris is the capital of France"}}

Input: "Which planet is largest?\nA) Earth\nB) Jupiter\nC) Saturn\nD) Mars"
Output: {{"question": "Which planet is largest?", "options": ["Earth", "Jupiter", "Saturn", "Mars"], "correct_option": 1, "explanation": "Jupiter is the largest planet"}}

TEXT TO EXTRACT FROM:
{text_chunk}

FINAL INSTRUCTIONS:
- Return ONLY valid JSON array
- No markdown, no code blocks, no explanations
- If you cannot extract any questions, return empty array: []
- VERIFY: Count all questions in the text and ensure your JSON has that many
- VERIFY: Each question has question, options (array), correct_option (number), explanation (string)"""

        logger.info("📤 Sending to Groq for enhanced MCQ extraction...")
        
        # Try up to 3 times to get a valid response
        max_retries = 3
        for attempt in range(max_retries):
            try:
                message = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    max_tokens=4096,
                    temperature=0.3,  # Lower temperature for more consistent extraction
                )
                response = message.choices[0].message.content
                logger.info(f"📥 Groq response length: {len(response)} chars")
                logger.debug(f"Groq response preview: {response[:300]}...")
                
                # Clean up the response to make it valid JSON if needed
                response = response.strip()
                if not response.startswith('['):
                    # Try to find the JSON array in the response (non-greedy)
                    json_match = re.search(r'\[[\s\S]*?\](?=\s*$|\s*\n)', response)
                    if json_match:
                        response = json_match.group(0)
                    else:
                        # Try greedy as fallback
                        json_match = re.search(r'\[[\s\S]*\]', response)
                        if json_match:
                            response = json_match.group(0)
                
                # Ensure we have a valid response
                if not response:
                    raise ValueError("Empty response from Groq")
                
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
                            # Remove leading A), B), etc. - be careful not to remove first character of actual option
                            # Only remove if it's a single letter followed by ) or .
                            opt = re.sub(r'^[A-Za-z][\.\)\s]+', '', opt).strip()
                            # Remove any remaining leading numbers or bullets (but preserve content)
                            opt = re.sub(r'^[\d\s\.\)\-•]+', '', opt).strip()
                            if opt and len(opt) > 0:  # Only add non-empty options
                                cleaned_options.append(opt)
                        
                        options = cleaned_options
                        
                        # Validate question and options
                        if not q_text:
                            logger.warning(f"⚠️ Skipping question with no text")
                            continue
                        if len(options) < 2:
                            logger.warning(f"⚠️ Skipping question with {len(options)} options (need 2+): {q_text[:50]}...")
                            logger.debug(f"   Options were: {options}")
                            continue
                        
                        # Handle correct answer - check both 'correct' and 'correct_option'
                        correct = item.get('correct_option') or item.get('correct')
                        if correct is None or not isinstance(correct, int) or correct >= len(options) or correct < 0:
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
                    logger.info(f"✅ Successfully extracted {len(questions)} questions from chunk {chunk_idx + 1}")
                    all_questions.extend(questions)
                    # Count question markers in original text to verify we got them all
                    question_count = text_chunk.count('?')
                    if len(questions) < question_count:
                        logger.warning(f"⚠️ Found {question_count} question marks but only extracted {len(questions)} questions - may be missing some")
                else:
                    logger.warning("⚠️ No valid questions found in this chunk")
                
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
        
        # Return all questions from all chunks (with deduplication)
        if all_questions:
            # Deduplicate across all chunks
            unique_questions = {}
            for q in all_questions:
                q_text = q.get('question', '').strip()
                if q_text:
                    # Use first 100 chars as dedup key
                    dedup_key = q_text[:100].lower()
                    if dedup_key not in unique_questions:
                        unique_questions[dedup_key] = q
            
            deduped = list(unique_questions.values())
            logger.info(f"✅ Total extracted {len(deduped)} unique questions from all chunks (deduplicated from {len(all_questions)})")
            return deduped
        
        logger.warning("⚠️ No questions extracted from any chunk")
        return []
        
    except Exception as e:
        logger.error(f"❌ Groq extraction failed: {str(e)}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return []


def extract_answer_key_from_pdf(file_bytes: bytes) -> dict:
    """Extract and validate answer key from PDF using Groq AI."""
    try:
        from groq import Groq
        import os
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set, cannot validate answer key")
            return {"status": "error", "message": "GROQ_API_KEY not configured"}
        
        client = Groq(api_key=api_key)
        
        # Extract text from PDF
        logger.info("Extracting text from answer key PDF...")
        text = ""
        
        try:
            doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
            text_pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    text_pages.append(text.strip())
            text = "\n\n".join(text_pages)
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}, trying PDFMiner...")
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(io.BytesIO(file_bytes))
            except Exception as e2:
                logger.error(f"PDFMiner also failed: {e2}")
                return {"status": "error", "message": "Could not extract text from answer key PDF"}
        
        if not text or len(text.strip()) < 10:
            return {"status": "error", "message": "Answer key PDF appears to be empty"}
        
        logger.info(f"Extracted {len(text)} characters from answer key")
        
        # Use Groq to parse and validate the answer key
        prompt = f"""You are an expert at parsing answer keys. Analyze this answer key document and extract all answers.

TASK: Extract the answer key in a structured format.

RESPONSE FORMAT (MUST BE VALID JSON):
{{
  "answers": [
    {{"question_number": 1, "answer": "A", "explanation": "Optional explanation"}},
    {{"question_number": 2, "answer": "B", "explanation": "Optional explanation"}},
    ...
  ],
  "total_questions": <number>,
  "format_notes": "Description of the answer key format found"
}}

PARSING RULES:
1. Extract question numbers and their corresponding answers
2. Answers can be letters (A, B, C, D) or numbers (1, 2, 3, 4)
3. If explanations are provided, include them
4. Normalize all answers to uppercase letters (A, B, C, D)
5. If answer is a number, convert to letter (1->A, 2->B, etc.)

ANSWER KEY TEXT:
{text[:3000]}

Return ONLY valid JSON. No markdown, no explanations."""

        logger.info("📤 Sending answer key to Groq for validation...")
        
        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=2048,
            temperature=0.2,  # Low temperature for consistent parsing
        )
        
        response = message.choices[0].message.content.strip()
        logger.info(f"📥 Groq response length: {len(response)} chars")
        
        # Parse the JSON response
        try:
            # Try to find JSON in response
            if not response.startswith('{'):
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    response = json_match.group(0)
            
            answer_key = json.loads(response)
            
            logger.info(f"✅ Successfully parsed answer key: {answer_key.get('total_questions', 0)} questions")
            logger.info(f"   Format: {answer_key.get('format_notes', 'Unknown')}")
            
            return {
                "status": "success",
                "answer_key": answer_key,
                "message": f"Successfully extracted answer key with {answer_key.get('total_questions', 0)} answers"
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response as JSON: {e}")
            logger.debug(f"Response was: {response[:500]}")
            return {
                "status": "error",
                "message": "Could not parse answer key format",
                "raw_response": response[:500]
            }
        
    except Exception as e:
        logger.error(f"Answer key extraction failed: {str(e)}")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": f"Answer key extraction failed: {str(e)}"}


def identify_correct_answer_with_groq(question: str, options: List[str]) -> Optional[int]:
    """Use Groq to identify the correct answer for a multiple-choice question with retry logic."""
    import time
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.debug("GROQ_API_KEY not set, returning None")
        return None
    
    max_retries = 3
    retry_delay = 1  # Start with 1 second
    
    for attempt in range(max_retries):
        try:
            client = Groq(api_key=api_key)
            options_str = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
            
            prompt = f"""Answer this multiple-choice question by selecting the BEST option.

Question: {question}

Options:
{options_str}

Respond with ONLY: ANSWER: A (or B, C, D, etc.)"""
            
            message = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=50,
                temperature=0.1,
            )
            response = message.choices[0].message.content.strip()
            logger.debug(f"🤖 Groq response: {response}")
            
            # Extract the answer
            match = re.search(r'ANSWER:\s*([A-Z])', response, re.IGNORECASE)
            if not match:
                match = re.search(r'\b([A-Z])\b', response)
                
            if match:
                letter = match.group(1).upper()
                idx = ord(letter) - ord('A')
                if 0 <= idx < len(options):
                    logger.info(f"✅ Answer: {letter} (index {idx})")
                    return idx
            
            logger.warning(f"⚠️ Could not parse: {response}")
            return None
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for rate limit
            if "429" in error_str or "rate" in error_str or "too many" in error_str:
                if attempt < max_retries - 1:
                    logger.warning(f"⏱️ Rate limited, retrying in {retry_delay}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(f"❌ Rate limited after {max_retries} attempts")
                    return None
            else:
                logger.error(f"❌ Groq error: {str(e)}")
                return None
    
    return None
