# 🚂 Railway Deployment - Quick Start (15 Minutes)

## 🎯 7 Simple Steps

### Step 1: Create Railway Account (2 min)
```
1. Go to https://railway.app
2. Click "Start a New Project"
3. Click "Deploy from GitHub repo"
4. Authorize Railway with GitHub
5. Done! ✅
```

### Step 2: Select Repository (1 min)
```
1. Find: Shaikh-Aayan/quiz
2. Click it
3. Select: main branch
4. Click "Deploy Now"
5. Done! ✅
```

### Step 3: Wait for Build (5 min)
```
Railway will:
- Detect Python project ✅
- Find requirements.txt ✅
- Find Procfile ✅
- Build automatically ✅
- Start service ✅

Just wait... ⏳
```

### Step 4: Add Environment Variables (3 min)
```
In Railway dashboard:

1. Click "Variables"
2. Add GROQ_API_KEY = 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
3. Add DATABASE_URL = sqlite:///./questions.db
4. Add ALLOWED_ORIGINS = *
5. Click "Save"
6. Done! ✅
```

### Step 5: Get Backend URL (1 min)
```
In Railway dashboard:

1. Find "Public URL" or "Domain"
2. Copy it
3. Looks like: https://your-project-production.up.railway.app
4. Save it! 📝
```

### Step 6: Update Frontend (2 min)
```bash
# Edit frontend/lib/api.ts
# Change:
const API_BASE_URL = 'https://your-project-production.up.railway.app';

# Push to GitHub:
git add frontend/lib/api.ts
git commit -m "Update API URL"
git push origin main

# Vercel auto-redeploys! ✅
```

### Step 7: Test Everything (1 min)
```bash
# Test backend
curl https://your-project-production.up.railway.app/health

# Open frontend
https://acca-mcq-website.vercel.app

# Upload sample PDF
# Test quiz
# Done! ✅
```

---

## 📊 Timeline

```
Step 1: 2 min  ⏱️
Step 2: 1 min  ⏱️
Step 3: 5 min  ⏳ (auto)
Step 4: 3 min  ⏱️
Step 5: 1 min  ⏱️
Step 6: 2 min  ⏱️
Step 7: 1 min  ⏱️
─────────────────
Total: 15 min 🚀
```

---

## 🎯 Your URLs

```
Frontend: https://acca-mcq-website.vercel.app
Backend: https://your-project-production.up.railway.app
GitHub: https://github.com/Shaikh-Aayan/quiz
```

---

## ✅ Checklist

- [ ] Railway account created
- [ ] Repository deployed
- [ ] Build successful
- [ ] Variables added
- [ ] Backend URL copied
- [ ] Frontend updated
- [ ] Vercel redeployed
- [ ] Health check passes
- [ ] Features tested
- [ ] LIVE! 🎉

---

## 💰 Cost: $0

---

## 🚀 Start Now!

**Go to https://railway.app and click "Start a New Project"**

For detailed steps, see: `RAILWAY_DEPLOYMENT_GUIDE.md`

---

**15 minutes to LIVE!** 🚂💨
