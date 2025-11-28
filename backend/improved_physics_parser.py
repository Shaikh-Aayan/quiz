"""
Improved parser for Physics exam PDFs where options are embedded in question text
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def parse_physics_mcqs_improved(text: str) -> List[Dict]:
    """
    Parse MCQs from Physics exam PDF where options are embedded in question text.
    
    Format:
    1.
    Question text A. Option A B. Option B C. Option C D. Option D
    2.
    Next question...
    """
    
    if not text or len(text) < 50:
        logger.error("Text too short for parsing")
        return []
    
    results = []
    lines = text.split('\n')
    lines = [l.strip() for l in lines]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for question number pattern: "1.", "2.", etc. (just the number)
        q_match = re.match(r'^(\d+)\.\s*$', line)
        
        if not q_match:
            i += 1
            continue
        
        q_num = int(q_match.group(1))
        
        # Collect lines until next question number
        question_block_lines = []
        j = i + 1
        
        while j < len(lines):
            next_line = lines[j]
            
            # Stop if we hit another question number
            if re.match(r'^\d+\.\s*$', next_line):
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
        # We need to find where options start
        
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
            results.append({
                'question': question_text,
                'options': options[:4],  # Max 4 options
                'correct_option': None,
                'explanation': ''
            })
            logger.info(f"✅ Q{q_num}: {question_text[:60]}... | {len(options)} options")
        else:
            logger.debug(f"Q{q_num}: Invalid - text={len(question_text)} opts={len(options)}")
        
        i = j
    
    logger.info(f"✅ Improved parser extracted {len(results)} questions")
    return results
