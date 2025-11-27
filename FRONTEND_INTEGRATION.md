# Frontend Integration Guide - Answer Key Upload

## Quick Start

Add this HTML to your frontend to enable answer key upload:

```html
<!-- Answer Key Upload Section -->
<div class="answer-key-section">
  <h2>📋 Upload Answer Key</h2>
  <p>Upload a PDF containing the answer key. AI will validate and extract all answers.</p>
  
  <div class="upload-area">
    <input 
      type="file" 
      id="answerKeyFile" 
      accept=".pdf" 
      style="display: none;"
    />
    <button 
      onclick="document.getElementById('answerKeyFile').click()"
      class="upload-btn"
    >
      Choose Answer Key PDF
    </button>
    <span id="answerKeyFileName" class="file-name"></span>
  </div>
  
  <button 
    onclick="uploadAnswerKey()" 
    class="submit-btn"
    id="uploadAnswerKeyBtn"
    disabled
  >
    Upload & Validate Answer Key
  </button>
  
  <div id="answerKeyResult" class="result-area"></div>
</div>
```

## JavaScript Implementation

```javascript
// Handle answer key file selection
document.getElementById('answerKeyFile').addEventListener('change', function(e) {
  const fileName = e.target.files[0]?.name || '';
  document.getElementById('answerKeyFileName').textContent = fileName;
  document.getElementById('uploadAnswerKeyBtn').disabled = !fileName;
});

// Upload answer key
async function uploadAnswerKey() {
  const fileInput = document.getElementById('answerKeyFile');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Please select an answer key PDF');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  const resultDiv = document.getElementById('answerKeyResult');
  resultDiv.innerHTML = '<p class="loading">⏳ Processing answer key...</p>';
  
  try {
    const response = await fetch('http://127.0.0.1:8000/upload-answer-key', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (response.ok && data.status === 'success') {
      displayAnswerKeySuccess(data);
    } else {
      displayAnswerKeyError(data.detail || 'Failed to process answer key');
    }
  } catch (error) {
    displayAnswerKeyError(`Error: ${error.message}`);
  }
}

// Display success result
function displayAnswerKeySuccess(data) {
  const resultDiv = document.getElementById('answerKeyResult');
  const answerKey = data.answer_key;
  
  let html = `
    <div class="success-box">
      <h3>✅ Answer Key Validated Successfully!</h3>
      <p><strong>File:</strong> ${data.file_name}</p>
      <p><strong>Message:</strong> ${data.message}</p>
      <p><strong>Format:</strong> ${answerKey.format_notes}</p>
      <p><strong>Total Questions:</strong> ${answerKey.total_questions}</p>
      
      <h4>Extracted Answers:</h4>
      <table class="answers-table">
        <thead>
          <tr>
            <th>Q#</th>
            <th>Answer</th>
            <th>Explanation</th>
          </tr>
        </thead>
        <tbody>
  `;
  
  answerKey.answers.forEach(ans => {
    html += `
      <tr>
        <td>${ans.question_number}</td>
        <td><strong>${ans.answer}</strong></td>
        <td>${ans.explanation || '-'}</td>
      </tr>
    `;
  });
  
  html += `
        </tbody>
      </table>
      <button onclick="downloadAnswerKeyJSON('${JSON.stringify(answerKey).replace(/'/g, "\\'")}')">
        📥 Download as JSON
      </button>
    </div>
  `;
  
  resultDiv.innerHTML = html;
}

// Display error result
function displayAnswerKeyError(error) {
  const resultDiv = document.getElementById('answerKeyResult');
  resultDiv.innerHTML = `
    <div class="error-box">
      <h3>❌ Error Processing Answer Key</h3>
      <p>${error}</p>
      <button onclick="document.getElementById('answerKeyFile').click()">
        Try Again
      </button>
    </div>
  `;
}

// Download answer key as JSON
function downloadAnswerKeyJSON(jsonStr) {
  const answerKey = JSON.parse(jsonStr);
  const dataStr = JSON.stringify(answerKey, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `answer_key_${new Date().getTime()}.json`;
  link.click();
  URL.revokeObjectURL(url);
}
```

## CSS Styling

```css
.answer-key-section {
  background: #f8f9fa;
  border: 2px dashed #007bff;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.answer-key-section h2 {
  color: #333;
  margin-top: 0;
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
}

.upload-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.upload-btn:hover {
  background: #0056b3;
}

.file-name {
  color: #666;
  font-size: 14px;
}

.submit-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  background: #218838;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result-area {
  margin-top: 20px;
}

.success-box {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  padding: 15px;
  color: #155724;
}

.error-box {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 15px;
  color: #721c24;
}

.loading {
  color: #007bff;
  font-style: italic;
}

.answers-table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  background: white;
}

.answers-table th,
.answers-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}

.answers-table th {
  background: #f2f2f2;
  font-weight: bold;
}

.answers-table tr:nth-child(even) {
  background: #f9f9f9;
}
```

## Integration Steps

1. **Add HTML Section**
   - Copy the HTML code above
   - Add it to your frontend (e.g., `standalone.html`)
   - Place it near the MCQ upload section

2. **Add JavaScript Functions**
   - Copy the JavaScript code above
   - Add it to your frontend script section
   - Ensure it runs after DOM is loaded

3. **Add CSS Styling**
   - Copy the CSS code above
   - Add it to your frontend stylesheet
   - Customize colors/styling as needed

4. **Test**
   - Upload a sample answer key PDF
   - Verify the extraction works
   - Check the displayed results

## Example Answer Key PDF Format

For best results, format your answer key PDF like this:

```
ANSWER KEY

1. A
2. B
3. C
4. D
5. A
...
```

Or with explanations:

```
ANSWER KEY

1. Answer: A - Paris is the capital of France
2. Answer: B - 29 is a prime number
3. Answer: A - ACCA stands for Association of Chartered Certified Accountants
...
```

## API Response Structure

```json
{
  "status": "success",
  "message": "Successfully extracted answer key with 50 answers",
  "file_name": "answer_key.pdf",
  "answer_key": {
    "answers": [
      {
        "question_number": 1,
        "answer": "A",
        "explanation": "Optional explanation"
      }
    ],
    "total_questions": 50,
    "format_notes": "Simple numbered list format"
  }
}
```

## Troubleshooting

### Issue: "Only PDF files are allowed"
- Ensure you're uploading a .pdf file
- Check file extension

### Issue: "Uploaded file is empty"
- Ensure PDF has content
- Try opening the PDF in a reader first

### Issue: "Could not extract text from answer key PDF"
- PDF might be scanned without OCR
- Try converting to text-based PDF
- Ensure PDF is not corrupted

### Issue: "Could not parse answer key format"
- Answer key format might not be recognized
- Try formatting as simple numbered list (1. A, 2. B, etc.)
- Ensure clear separation between questions and answers

## Features

✅ Upload answer key PDF
✅ AI validation and parsing
✅ Automatic format detection
✅ Answer normalization (1→A, 2→B, etc.)
✅ Explanation extraction
✅ JSON export
✅ Error handling
✅ User-friendly UI

## Status
Ready for integration! 🚀
