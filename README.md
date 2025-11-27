# 🎯 Aayan MCQ Hub – AI-Powered ACCA MCQ Practice

A complete AI-powered MCQ learning platform for ACCA students.

## ✨ Features

- ✅ Upload PDFs & auto-extract MCQs
- ✅ Interactive quiz with scoring
- ✅ 💡 AI Hints (free via Groq)
- ✅ 📖 AI Explanations (free via Groq)
- ✅ 💬 AI Feedback (free via Groq)
- ✅ Dark theme with animations
- ✅ Responsive design
- ✅ Production ready

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
python main.py
```
Runs on: `http://127.0.0.1:8000`

### 2. Open Frontend
```
file:///e:/ACCA-MCQ-Website/frontend/standalone.html
```

### 3. Start Using!
- Upload PDF
- Extract MCQs
- Practice quiz
- Get AI help

---

## 📁 Project Structure

```
ACCA-MCQ-Website/
├── backend/              # FastAPI backend
│   ├── main.py
│   ├── extractor.py
│   ├── groq_ai.py
│   ├── requirements.txt
│   └── .env
├── frontend/             # Standalone HTML
│   └── standalone.html
└── README.md
```

---

## 🔧 Configuration

Backend `.env`:
```
GROQ_API_KEY=your_key_here
DATABASE_URL=sqlite:///./mcq_db.db
```

---

## 📚 Tech Stack

- **Backend**: FastAPI + Groq AI + SQLite
- **Frontend**: Standalone HTML (no build)
- **Database**: SQLite
- **AI**: Groq API (free tier)

---

**Built with ❤️ by Aayan**
