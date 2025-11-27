# Step-by-Step Deployment Guide (With Screenshots)

## 📋 Complete Walkthrough

### STEP 1: Create GitHub Account & Repository (3 min)

#### 1.1 Create GitHub Account
1. Go to https://github.com
2. Click "Sign up"
3. Enter email, password, username
4. Verify email
5. Done! ✅

#### 1.2 Create New Repository
1. Click "+" icon (top right)
2. Select "New repository"
3. Fill in:
   - **Repository name**: `acca-mcq-website`
   - **Description**: `ACCA MCQ Extraction and Quiz Platform`
   - **Public** (so Render can access it)
4. Click "Create repository"
5. Copy the repository URL
6. Done! ✅

#### 1.3 Push Your Code
Open PowerShell in your project folder:

```powershell
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ACCA MCQ Website"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/acca-mcq-website.git

# Rename branch to main
git branch -M main

# Push
git push -u origin main
```

Wait for upload to complete. Done! ✅

---

### STEP 2: Deploy Backend to Render (5 min)

#### 2.1 Create Render Account
1. Go to https://render.com
2. Click "Get Started"
3. Click "Sign up with GitHub"
4. Authorize Render to access GitHub
5. Done! ✅

#### 2.2 Create Web Service
1. Go to https://dashboard.render.com
2. Click "New +" button (top right)
3. Select "Web Service"
4. Select your GitHub repository
5. Click "Connect"
6. Done! ✅

#### 2.3 Configure Service
Fill in the form:

```
Name: acca-mcq-backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

7. Scroll down
8. Click "Create Web Service"
9. Wait for deployment (5-10 minutes)
10. Done! ✅

#### 2.4 Add Environment Variables
1. Go to your service dashboard
2. Click "Environment" (left sidebar)
3. Click "Add Environment Variable"
4. Add these variables:

```
GROQ_API_KEY = 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
DATABASE_URL = sqlite:///./questions.db
ALLOWED_ORIGINS = *
```

5. Click "Save"
6. Service will redeploy
7. Done! ✅

#### 2.5 Get Backend URL
1. Go to your service page
2. Look for the URL at the top
3. Copy it (e.g., `https://acca-mcq-backend.onrender.com`)
4. Save it somewhere
5. Done! ✅

---

### STEP 3: Update Frontend (2 min)

#### 3.1 Edit API URL
1. Open `frontend/lib/api.ts` in your editor
2. Find this line:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
```
3. Change it to:
```typescript
const API_BASE_URL = 'https://acca-mcq-backend.onrender.com';
```
4. Save the file
5. Done! ✅

#### 3.2 Push Changes
```powershell
git add frontend/lib/api.ts
git commit -m "Update API URL for production"
git push
```

Wait for push to complete. Done! ✅

---

### STEP 4: Deploy Frontend to Vercel (5 min)

#### 4.1 Create Vercel Account
1. Go to https://vercel.com
2. Click "Sign Up"
3. Click "Continue with GitHub"
4. Authorize Vercel to access GitHub
5. Done! ✅

#### 4.2 Import Project
1. Go to https://vercel.com/new
2. Select your GitHub repository
3. Click "Import"
4. Done! ✅

#### 4.3 Configure Project
1. **Framework Preset**: Select "Next.js"
2. **Root Directory**: Select `frontend`
3. **Build Command**: `npm run build`
4. **Output Directory**: `.next`
5. Click "Environment Variables"
6. Add:
```
REACT_APP_API_URL = https://acca-mcq-backend.onrender.com
```
7. Click "Deploy"
8. Wait for deployment (2-5 minutes)
9. Done! ✅

#### 4.4 Get Frontend URL
1. Wait for deployment to complete
2. You'll see "Congratulations!"
3. Copy the URL (e.g., `https://acca-mcq-website.vercel.app`)
4. Save it
5. Done! ✅

---

### STEP 5: Test Everything (5 min)

#### 5.1 Test Backend Health
Open PowerShell:
```powershell
curl https://acca-mcq-backend.onrender.com/health
```

Should return:
```json
{"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

✅ Backend is working!

#### 5.2 Test Frontend
1. Open `https://acca-mcq-website.vercel.app` in browser
2. Should load without errors
3. Check browser console (F12) for errors
4. ✅ Frontend is working!

#### 5.3 Test MCQ Upload
1. Click "Upload MCQ PDF"
2. Select `sample_mcqs.pdf` from your computer
3. Click "Upload"
4. Should extract 3 questions
5. Verify all questions display
6. ✅ MCQ upload works!

#### 5.4 Test Answer Key Upload
1. Click "Upload Answer Key"
2. Create a simple PDF with:
```
1. A
2. B
3. B
```
3. Upload it
4. Should validate and show answers
5. ✅ Answer key upload works!

#### 5.5 Test Quiz
1. Click "Start Quiz"
2. Should load questions
3. Answer a question
4. Click "Submit"
5. Should show feedback
6. ✅ Quiz works!

---

## 🎉 You're Done!

Your website is now LIVE!

### Your URLs:
```
Frontend: https://acca-mcq-website.vercel.app
Backend: https://acca-mcq-backend.onrender.com
```

### Share with Users:
Send them: `https://acca-mcq-website.vercel.app`

### Monitor:
- Render Dashboard: https://dashboard.render.com
- Vercel Dashboard: https://vercel.com/dashboard

---

## 🔧 Troubleshooting

### Backend not responding?
1. Wait 30-60 seconds (Render spins up)
2. Check Render dashboard logs
3. Verify environment variables are set
4. Try refreshing

### CORS error?
1. Check API URL in frontend
2. Verify ALLOWED_ORIGINS in Render
3. Redeploy backend

### PDF not uploading?
1. Check backend logs
2. Verify file is valid PDF
3. Try smaller PDF

### Frontend not loading?
1. Check Vercel deployment logs
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try hard refresh (Ctrl+F5)

---

## 📊 Performance Tips

### Keep Backend Active
Render free tier spins down after 15 minutes. To keep it active:

1. Add this to your frontend (optional):
```javascript
// Ping backend every 10 minutes
setInterval(() => {
  fetch('https://acca-mcq-backend.onrender.com/health')
    .catch(err => console.log('Ping failed:', err));
}, 10 * 60 * 1000);
```

2. Or upgrade to Render Pro ($7/month)

### Monitor Usage
1. Check Render logs weekly
2. Monitor Vercel analytics
3. Track API calls
4. Upgrade if needed

---

## 💰 Cost Breakdown

| Service | Cost | Why |
|---------|------|-----|
| Vercel | FREE | Unlimited frontend hosting |
| Render | FREE | Unlimited backend (0.5GB RAM) |
| Groq API | FREE | 1000 requests/day |
| Domain | $0 | Using free .vercel.app domain |
| **TOTAL** | **$0** | ✅ Completely Free |

---

## 🚀 Next Steps

### Immediate
1. ✅ Test all features
2. ✅ Share with friends
3. ✅ Gather feedback

### This Week
1. Monitor logs
2. Fix any issues
3. Optimize performance

### This Month
1. Add more features
2. Improve UI/UX
3. Scale if needed

### Future
1. Add custom domain ($10-15/year)
2. Upgrade to paid tiers if needed
3. Add more features
4. Grow user base

---

## 📞 Support

### Documentation
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
- FastAPI: https://fastapi.tiangolo.com

### Community
- GitHub Issues: https://github.com
- Stack Overflow: https://stackoverflow.com
- Reddit: r/webdev

---

## ✅ Deployment Checklist

- [ ] GitHub account created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Backend deployed
- [ ] Environment variables set
- [ ] Frontend API URL updated
- [ ] Vercel account created
- [ ] Frontend deployed
- [ ] Backend health check passes
- [ ] Frontend loads
- [ ] MCQ upload works
- [ ] Answer key upload works
- [ ] Quiz works
- [ ] All features tested
- [ ] URLs saved
- [ ] Shared with users

---

## 🎊 Congratulations!

Your ACCA MCQ Website is now **LIVE** and **FREE**! 🎉

**Frontend**: https://acca-mcq-website.vercel.app
**Backend**: https://acca-mcq-backend.onrender.com

**Share it with the world!** 🌍
