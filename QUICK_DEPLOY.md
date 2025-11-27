# Quick Deploy in 5 Minutes ⚡

## TL;DR - Fastest Path to Live

### Prerequisites (5 min)
1. GitHub account (free) - https://github.com
2. Render account (free) - https://render.com
3. Vercel account (free) - https://vercel.com
4. Groq API key (already have it)

### Step 1: Push to GitHub (2 min)

```bash
# In your project root
git init
git add .
git commit -m "ACCA MCQ Website"
git remote add origin https://github.com/YOUR_USERNAME/acca-mcq-website.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Render (3 min)

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Fill in:
   - Name: `acca-mcq-backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create"
6. Wait for deployment
7. **Copy your URL** (e.g., `https://acca-mcq-backend.onrender.com`)

### Step 3: Add Environment Variables (1 min)

In Render dashboard → Your service → Environment:
```
GROQ_API_KEY=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
DATABASE_URL=sqlite:///./questions.db
ALLOWED_ORIGINS=*
```

### Step 4: Update Frontend (2 min)

Edit `frontend/lib/api.ts`:
```typescript
const API_BASE_URL = 'https://acca-mcq-backend.onrender.com';
```

Push to GitHub:
```bash
git add frontend/lib/api.ts
git commit -m "Update API URL"
git push
```

### Step 5: Deploy Frontend to Vercel (2 min)

1. Go to https://vercel.com/new
2. Import GitHub repo
3. Select `frontend` as root directory
4. Click "Deploy"
5. Wait for deployment
6. **Your site is LIVE!** 🎉

---

## Verify Deployment

### Test Backend
```bash
curl https://acca-mcq-backend.onrender.com/health
```

### Test Frontend
Open: `https://your-project.vercel.app`

### Upload Test PDF
1. Click "Upload MCQ PDF"
2. Select `sample_mcqs.pdf`
3. Should extract 3 questions
4. ✅ Success!

---

## Common Issues & Quick Fixes

| Issue | Fix |
|-------|-----|
| Backend not responding | Wait 30 sec (Render spins up) |
| CORS error | Check API URL in frontend |
| PDF not uploading | Check backend logs |
| Vercel deploy fails | Check `frontend` folder exists |
| Render deploy fails | Check `requirements.txt` exists |

---

## Your Live URLs

After deployment:
- **Frontend**: `https://YOUR-PROJECT.vercel.app`
- **Backend**: `https://acca-mcq-backend.onrender.com`
- **API Health**: `https://acca-mcq-backend.onrender.com/health`

---

## Next Steps

1. ✅ Test all features
2. ✅ Share with users
3. ✅ Monitor logs
4. ✅ Upgrade if needed

**Total time: ~15 minutes** ⏱️

**Cost: $0** 💰

**Status: LIVE** 🚀
