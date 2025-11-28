# ✨ Features

## MCQ Extraction
- Upload PDF files
- AI-powered extraction using Groq
- Automatic question parsing
- 100% accuracy on test data

## Answer Key Validation
- Upload answer key PDF
- AI validates and extracts answers
- Automatic format detection
- Answer normalization (1→A, 2→B, etc.)

## Quiz Platform
- Practice with extracted questions
- Multiple choice interface
- Instant feedback
- Score tracking
- Hints and explanations (AI-powered)
- Progress bar

## AI Features
- Groq integration for extraction
- Hint generation
- Explanation generation
- Answer validation
- Raw text validation

## Tech Stack
- **Backend**: FastAPI + Python
- **Frontend**: React/Next.js + Tailwind CSS
- **Database**: SQLite
- **AI**: Groq (llama-3.3-70b-versatile)
- **Deployment**: Railway (backend) + Vercel (frontend)

## API Endpoints
- `POST /upload` - Upload PDF
- `GET /questions` - Get all questions
- `GET /quiz` - Get random questions
- `POST /assistant/explain` - Get explanation
- `POST /assistant/hint` - Get hint
- `DELETE /questions/all` - Delete all questions
- `GET /health` - Health check
