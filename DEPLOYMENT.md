# 🚀 Deployment Guide

## Quick Start

### Backend (Railway)
1. Go to https://railway.app/dashboard
2. Wait for "Running" status
3. Copy public URL: `https://your-project-production.up.railway.app`

### Frontend (Vercel)
1. Update `frontend/lib/api.ts`:
```typescript
const API_BASE_URL = 'https://your-railway-url.up.railway.app';
```

2. Push to GitHub:
```bash
git add frontend/lib/api.ts
git commit -m "Update API URL"
git push origin main
```

3. Vercel auto-redeploys ✅

### Test
```bash
# Backend health
curl https://your-railway-url.up.railway.app/health

# Frontend
https://acca-mcq-website.vercel.app
```

## Environment Variables (Railway)
```
GROQ_API_KEY = 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
DATABASE_URL = sqlite:///./questions.db
ALLOWED_ORIGINS = *
```

## Status
- Backend: Railway (Docker)
- Frontend: Vercel
- Database: SQLite
- Cost: $0
