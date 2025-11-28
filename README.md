# 🎯 Aayan MCQ Hub – AI-Powered ACCA MCQ Practice

A complete AI-powered MCQ learning platform for ACCA students with automatic PDF extraction, interactive quizzes, and AI-powered hints & explanations.

## ✨ Features

- ✅ **PDF Upload & Auto-Extract** - Upload ACCA past papers, AI extracts MCQs automatically
- ✅ **Interactive Quiz** - Practice with extracted questions, track score
- ✅ **💡 AI Hints** - Get smart hints powered by Groq (free)
- ✅ **📖 AI Explanations** - Detailed explanations for each question
- ✅ **Answer Key Validation** - Upload answer keys, AI validates them
- ✅ **Dark Theme** - Beautiful dark UI with smooth animations
- ✅ **Responsive Design** - Works on desktop, tablet, mobile
- ✅ **100% Free** - No subscriptions, no paywalls

---

## 🌐 Live Deployment

### Frontend (GitHub Pages)
🔗 **https://shaikh-aayan.github.io/quiz**

### Backend (Railway)
🔗 **https://quiz-production-cf4b.up.railway.app**

### Alternative Frontend (Vercel)
🔗 **https://acca-mcq-website.vercel.app**

---

## 🚀 Quick Start (Local Development)

### 1. Start Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend runs on: `http://127.0.0.1:8000`

### 2. Open Frontend
```
Open: index.html in your browser
Or: http://127.0.0.1:8000/docs (API docs)
```

### 3. Start Using!
- Upload a PDF with MCQs
- AI extracts questions automatically
- Practice the quiz
- Get AI hints and explanations

---

## 📁 Project Structure

```
quiz/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main API
│   ├── extractor.py           # PDF extraction logic
│   ├── groq_ai.py             # Groq AI integration
│   ├── models.py              # Database models
│   ├── db.py                  # Database setup
│   ├── requirements.txt       # Dependencies
│   ├── Procfile               # Render deployment
│   └── runtime.txt            # Python version
├── frontend/                   # Frontend files
│   ├── index.html             # Main UI
│   └── public/                # Static assets
├── index.html                 # GitHub Pages entry point
├── Dockerfile                 # Docker configuration
├── railway.json               # Railway deployment config
├── .github/workflows/         # GitHub Actions
│   └── deploy.yml             # Auto-deploy workflow
├── DEPLOYMENT.md              # Deployment guide
├── FEATURES.md                # Feature documentation
└── README.md                  # This file
```

---

## 🔧 Configuration

### Environment Variables (Backend)
```bash
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./questions.db
ALLOWED_ORIGINS=*
```

### Get Groq API Key
1. Go to https://console.groq.com
2. Sign up for free
3. Create API key
4. Add to environment variables

---

## 📚 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI + Python 3.11 |
| **Frontend** | HTML5 + Tailwind CSS + Vanilla JS |
| **Database** | SQLite |
| **AI** | Groq API (llama-3.3-70b-versatile) |
| **PDF Processing** | PyMuPDF + pdfminer.six |
| **Deployment** | Railway (backend) + GitHub Pages (frontend) |

---

## 🚀 Deployment

### GitHub Pages (Frontend)
- Automatically deploys on every push
- URL: `https://shaikh-aayan.github.io/quiz`
- Zero cost, unlimited bandwidth

### Railway (Backend)
- Docker-based deployment
- Auto-scales on demand
- Free tier: 0.5GB RAM, unlimited requests
- URL: `https://quiz-production-cf4b.up.railway.app`

See `DEPLOYMENT.md` for detailed deployment instructions.

---

## 📖 API Documentation

Once backend is running, visit:
```
http://127.0.0.1:8000/docs
```

### Key Endpoints
- `POST /upload` - Upload PDF and extract MCQs
- `GET /questions` - Get all extracted questions
- `GET /quiz` - Get random questions for quiz
- `POST /assistant/explain` - Get AI explanation
- `POST /assistant/hint` - Get AI hint
- `DELETE /questions/all` - Delete all questions
- `GET /health` - Health check

---

## 🎯 How It Works

1. **Upload PDF** → User uploads ACCA past paper
2. **Extract MCQs** → AI extracts questions using Groq
3. **Validate** → AI validates extracted questions
4. **Practice Quiz** → User practices with extracted questions
5. **Get Help** → AI provides hints and explanations

---

## 💡 Features in Detail

### PDF Extraction
- Supports multiple extraction methods
- Handles scanned PDFs (OCR)
- Removes duplicates automatically
- Preserves question formatting

### Quiz Mode
- One question at a time
- Multiple choice options
- Instant feedback
- Score tracking
- Progress bar

### AI Assistance
- Smart hints based on question context
- Detailed explanations
- Answer validation
- Format detection

---

## 🔐 Security

- No API keys exposed in frontend
- Environment variables for sensitive data
- CORS configured
- Input validation on all endpoints
- SQLite database (local storage)

---

## 📊 Performance

- Backend response time: <200ms
- PDF extraction: 2-5 seconds
- Frontend load time: <1 second
- Database queries: <50ms

---

## 🤝 Contributing

Found a bug? Have a feature request?
- Open an issue on GitHub
- Submit a pull request
- Contact: aayan@example.com

---

## 📄 License

MIT License - Feel free to use, modify, and distribute

---

## 🙏 Credits

- **Groq AI** - Free AI API for MCQ extraction
- **Railway** - Free backend hosting
- **GitHub Pages** - Free frontend hosting
- **Tailwind CSS** - Beautiful UI framework

---

**Built with ❤️ by Shaikh Aayan**

**Last Updated**: November 28, 2025
