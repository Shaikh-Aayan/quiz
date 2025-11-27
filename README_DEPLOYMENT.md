# 🚀 ACCA MCQ Website - Deployment Guide

## ⚡ Quick Start (20 Minutes)

```
Your Website → GitHub → Render (Backend) → Vercel (Frontend) → LIVE! 🎉
```

---

## 📋 What You Need

- ✅ GitHub account (free)
- ✅ Render account (free)
- ✅ Vercel account (free)
- ✅ Groq API key (already have it)

---

## 🎯 3 Simple Steps

### Step 1: Push to GitHub (2 min)
```bash
git init
git add .
git commit -m "ACCA MCQ Website"
git remote add origin https://github.com/YOUR_USERNAME/acca-mcq-website.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend (5 min)
1. Go to https://render.com
2. Sign up with GitHub
3. Create new Web Service
4. Select your repository
5. Set environment variables
6. Deploy!

**Your Backend URL**: `https://acca-mcq-backend.onrender.com`

### Step 3: Deploy Frontend (5 min)
1. Update API URL in `frontend/lib/api.ts`
2. Go to https://vercel.com
3. Import your GitHub repository
4. Deploy!

**Your Frontend URL**: `https://acca-mcq-website.vercel.app`

---

## ✅ Verify Deployment

```bash
# Test backend
curl https://acca-mcq-backend.onrender.com/health

# Open frontend
https://acca-mcq-website.vercel.app
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Your Website                       │
│            (Vercel - Free Tier)                     │
│  https://acca-mcq-website.vercel.app               │
└────────────────────┬────────────────────────────────┘
                     │
                     │ API Calls
                     ↓
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                    │
│            (Render - Free Tier)                     │
│  https://acca-mcq-backend.onrender.com             │
│                                                     │
│  ├─ PDF Extraction                                 │
│  ├─ AI Validation (Groq)                           │
│  ├─ Answer Key Upload                              │
│  ├─ Quiz Functionality                             │
│  └─ SQLite Database                                │
└─────────────────────────────────────────────────────┘
```

---

## 💰 Cost

| Component | Cost |
|-----------|------|
| Frontend (Vercel) | FREE |
| Backend (Render) | FREE |
| Database (SQLite) | FREE |
| API (Groq) | FREE (1000 req/day) |
| **Total** | **$0** |

---

## 🎯 Features Ready

✅ Upload MCQ PDF
✅ Extract questions with AI
✅ Upload answer key
✅ Validate answers
✅ Take quiz
✅ Get explanations
✅ Responsive design
✅ Error handling

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `STEP_BY_STEP_DEPLOY.md` | Detailed walkthrough |
| `QUICK_DEPLOY.md` | 5-minute version |
| `DEPLOYMENT_GUIDE.md` | Complete reference |
| `DEPLOYMENT_SUMMARY.md` | Overview |
| `DEPLOYMENT_COMPLETE.md` | Final checklist |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend slow | Wait 30 sec (Render spins up) |
| CORS error | Check API URL in frontend |
| PDF not uploading | Check backend logs |
| Frontend not loading | Clear cache, hard refresh |

---

## 🚀 Next Steps

1. **Read**: `STEP_BY_STEP_DEPLOY.md`
2. **Create**: GitHub, Render, Vercel accounts
3. **Deploy**: Follow the steps
4. **Test**: Verify all features
5. **Share**: Send URL to users

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

## ✨ Status

✅ Backend: Production Ready
✅ Frontend: Production Ready
✅ Deployment: Ready
✅ Documentation: Complete

**Time to Deploy**: 20 minutes
**Cost**: $0
**Status**: 🚀 READY TO GO LIVE!

---

**Start with `STEP_BY_STEP_DEPLOY.md` →**
