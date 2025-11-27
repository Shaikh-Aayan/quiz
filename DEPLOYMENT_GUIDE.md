# Complete Free Deployment Guide - ACCA MCQ Website

## Overview
Deploy your full-stack application (React frontend + FastAPI backend + SQLite database) completely free using:
- **Frontend**: Vercel (free tier)
- **Backend**: Render.com (free tier) or Railway.app (free tier)
- **Database**: SQLite (included with backend)

## Option 1: RECOMMENDED - Vercel + Render (Easiest)

### Step 1: Prepare Backend for Deployment

#### 1.1 Create `requirements.txt` (already exists)
Verify it has all dependencies:
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-dotenv==1.0.0
groq==0.4.1
PyMuPDF==1.23.8
pdfminer.six==20221105
pytesseract==0.3.10
pdf2image==1.16.3
Pillow==10.1.0
requests==2.31.0
python-multipart==0.0.6
```

#### 1.2 Create `Procfile` (for Render)
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 1.3 Create `.gitignore`
```
__pycache__/
*.pyc
.env
.env.local
*.db
.venv/
venv/
node_modules/
dist/
build/
.DS_Store
```

#### 1.4 Create `runtime.txt` (for Python version)
```
python-3.11.7
```

### Step 2: Deploy Backend to Render.com (FREE)

#### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Connect your GitHub account

#### 2.2 Push Code to GitHub
```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit - ACCA MCQ Website"

# Create new repo on GitHub
# Then push
git remote add origin https://github.com/YOUR_USERNAME/acca-mcq-website.git
git branch -M main
git push -u origin main
```

#### 2.3 Deploy on Render
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Fill in details:
   - **Name**: `acca-mcq-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes)
7. Copy your backend URL: `https://acca-mcq-backend.onrender.com`

#### 2.4 Set Environment Variables on Render
1. Go to your service settings
2. Click "Environment"
3. Add variables:
   ```
   GROQ_API_KEY=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
   DATABASE_URL=sqlite:///./questions.db
   ALLOWED_ORIGINS=*
   ```

### Step 3: Build Frontend for Production

#### 3.1 Update API URL in Frontend
Edit `frontend/lib/api.ts`:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://acca-mcq-backend.onrender.com';
```

#### 3.2 Create `.env.production`
```
REACT_APP_API_URL=https://acca-mcq-backend.onrender.com
```

#### 3.3 Build Frontend
```bash
cd frontend
npm install
npm run build
```

### Step 4: Deploy Frontend to Vercel (FREE)

#### 4.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub
3. Connect your GitHub account

#### 4.2 Deploy on Vercel
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Select "Next.js" as framework
4. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add Environment Variables:
   ```
   REACT_APP_API_URL=https://acca-mcq-backend.onrender.com
   ```
6. Click "Deploy"
7. Wait for deployment (2-5 minutes)
8. Get your frontend URL: `https://acca-mcq-website.vercel.app`

### Step 5: Update CORS Settings

Update `backend/main.py`:
```python
origins = [
    "https://acca-mcq-website.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push changes:
```bash
git add .
git commit -m "Update CORS for production"
git push
```

Render will auto-redeploy!

---

## Option 2: Railway.app (Alternative Backend)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Connect your GitHub account

### Step 2: Deploy Backend
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Python
5. Add environment variables in Railway dashboard
6. Deploy automatically

### Step 3: Get Backend URL
- Railway provides: `https://your-project.railway.app`

---

## Option 3: Heroku Alternative (Paid but cheap)

### Note: Heroku free tier ended Nov 2022
- Cheapest option: $5/month
- Alternative: Use Render or Railway (both free)

---

## Complete Deployment Checklist

### Backend Preparation
- [ ] `requirements.txt` updated
- [ ] `Procfile` created
- [ ] `.gitignore` created
- [ ] `runtime.txt` created
- [ ] Code pushed to GitHub
- [ ] Environment variables set on Render/Railway

### Frontend Preparation
- [ ] API URL updated to production backend
- [ ] `.env.production` created
- [ ] Frontend built locally (`npm run build`)
- [ ] Code pushed to GitHub

### Deployment
- [ ] Backend deployed to Render/Railway
- [ ] Frontend deployed to Vercel
- [ ] CORS settings updated
- [ ] Environment variables configured
- [ ] Testing completed

### Post-Deployment
- [ ] Test MCQ upload on live site
- [ ] Test answer key upload
- [ ] Test quiz functionality
- [ ] Monitor logs for errors
- [ ] Set up auto-redeploy on push

---

## Testing Your Deployment

### 1. Test Backend Health
```bash
curl https://acca-mcq-backend.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

### 2. Test Frontend
1. Open https://acca-mcq-website.vercel.app
2. Upload a sample PDF
3. Verify questions are extracted
4. Test quiz functionality

### 3. Monitor Logs
- **Render**: Dashboard → Logs
- **Vercel**: Dashboard → Deployments → Logs
- **Railway**: Dashboard → Logs

---

## Troubleshooting

### Issue: "CORS error" or "Cannot reach backend"
**Solution:**
1. Check backend URL is correct
2. Verify CORS settings in `main.py`
3. Ensure backend is running (check Render logs)
4. Redeploy backend

### Issue: "Database not found"
**Solution:**
1. SQLite creates automatically on first run
2. Check Render logs for errors
3. Verify `DATABASE_URL` environment variable

### Issue: "Groq API key not working"
**Solution:**
1. Verify API key in `.env` file
2. Check it's set in Render/Railway environment
3. Ensure key has no extra spaces
4. Test with curl:
```bash
curl -H "Authorization: Bearer YOUR_KEY" https://api.groq.com/health
```

### Issue: "PDF extraction not working"
**Solution:**
1. Check Tesseract is installed (Render includes it)
2. Verify PDF is valid
3. Check backend logs for errors
4. Try with a different PDF

### Issue: "Frontend not updating after push"
**Solution:**
1. Vercel auto-deploys on push
2. Check deployment status on Vercel dashboard
3. Clear browser cache (Ctrl+Shift+Delete)
4. Try hard refresh (Ctrl+F5)

---

## Performance Optimization

### Frontend (Vercel)
- ✅ Automatic CDN caching
- ✅ Image optimization
- ✅ Code splitting
- ✅ Automatic compression

### Backend (Render Free)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ First request takes 30-60 seconds
- ✅ Unlimited requests when active
- ✅ 0.5 GB RAM
- ✅ Shared CPU

**Tip**: Keep backend active with periodic pings

---

## Cost Breakdown

| Service | Cost | Tier |
|---------|------|------|
| Vercel (Frontend) | FREE | Hobby |
| Render (Backend) | FREE | Free |
| Railway (Backend Alt) | FREE | Free |
| Groq API | FREE | 1000 req/day |
| Total | **FREE** | ✅ |

---

## Upgrade Path (If Needed)

### When to Upgrade
- More than 1000 Groq requests/day → Paid Groq plan
- Need persistent database → Render Postgres ($7/month)
- Need more backend resources → Render Pro ($7/month)
- Need custom domain → Vercel Pro ($20/month)

### Recommended Upgrades
1. **Custom Domain**: $10-15/year (Namecheap)
2. **Render Pro**: $7/month (better performance)
3. **Groq Pro**: $5/month (more API calls)

---

## Monitoring & Maintenance

### Set Up Monitoring
1. **Render**: Enable notifications
2. **Vercel**: Enable deployment notifications
3. **Email alerts**: Set up for failures

### Regular Maintenance
- [ ] Check logs weekly
- [ ] Monitor API usage
- [ ] Update dependencies monthly
- [ ] Test extraction quality
- [ ] Backup database (if needed)

---

## Final Steps

1. **Test Everything**
   - Upload MCQ PDF
   - Upload answer key
   - Take quiz
   - Check all features work

2. **Share Your Site**
   - Frontend URL: `https://acca-mcq-website.vercel.app`
   - Share with users
   - Gather feedback

3. **Monitor Performance**
   - Check logs daily first week
   - Monitor API usage
   - Optimize if needed

4. **Scale When Ready**
   - Upgrade to paid tiers
   - Add more features
   - Expand user base

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **GitHub Pages**: https://pages.github.com

---

## Status
✅ Ready to deploy!
✅ All services are free
✅ Complete automation available
✅ Scalable architecture

**Your site will be live in 30 minutes!** 🚀
