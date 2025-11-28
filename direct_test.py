#!/usr/bin/env python3
import re
import fitz

pdf_path = "Physics-X-Paper-I-2025.pdf"

# Extract text from PDF
doc = fitz.open(pdf_path)
text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text() + "\n"

lines = text.split('\n')
lines = [l.strip() for l in lines]

results = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Look for question number pattern
    q_match = re.match(r'^(\d+)\.\s*$', line)
    
    if not q_match:
        i += 1
        continue
    
    q_num = int(q_match.group(1))
    print(f"\nFound Q{q_num} at line {i}")
    
    # Next line(s) should be the question text
    question_lines = []
    j = i + 1
    
    # Collect question text until we hit an option (A., B., C., D.)
    while j < len(lines):
        next_line = lines[j]
        
        # Stop if we hit an option
        if re.match(r'^[A-D]\.\s', next_line):
            print(f"  Hit option at line {j}: {next_line[:50]}")
            break
        
        # Stop if we hit another question number
        if re.match(r'^\d+\.\s*$', next_line):
            print(f"  Hit next question at line {j}")
            break
        
        if next_line.strip():
            question_lines.append(next_line)
        
        j += 1
    
    question_text = ' '.join(question_lines).strip()
    print(f"  Question: {question_text[:80]}")
    
    # Collect options
    options = []
    while j < len(lines) and len(options) < 6:
        opt_line = lines[j]
        
        # Match option: A. text, A) text, etc.
        opt_match = re.match(r'^([A-D])[.\)\:]\s*(.+)$', opt_line)
        
        if opt_match:
            opt_text = opt_match.group(2).strip()
            
            # Skip empty or too-short options
            if len(opt_text) >= 2 and len(opt_text) < 200:
                options.append(opt_text)
                print(f"    {opt_match.group(1)}) {opt_text[:60]}")
            
            j += 1
        else:
            # Check if this is the next question
            if re.match(r'^\d+\.\s*$', opt_line):
                break
            j += 1
    
    print(f"  Total options: {len(options)}")
    
    if question_text and len(options) >= 2:
        results.append({
            'question': question_text,
            'options': options[:4],
        })
    
    i = j
    
    if len(results) >= 10:
        break

print(f"\n\nTotal extracted: {len(results)}")
