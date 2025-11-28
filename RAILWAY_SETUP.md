# Railway Environment Setup

## Problem
The `GROQ_API_KEY` is not being loaded on Railway because `.env` files are not deployed to production.

## Solution
You need to set the environment variable directly in Railway's dashboard:

### Steps:
1. Go to: https://railway.app/project/YOUR_PROJECT_ID
2. Click on your service (quiz-production)
3. Go to **Variables** tab
4. Add a new variable:
   - **Key**: `GROQ_API_KEY`
   - **Value**: `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`
5. Click **Save**
6. Railway will automatically redeploy with the new environment variable

### Verification
After redeployment, upload a PDF and check the logs. You should see:
```
✅ Groq API key found, attempting to identify answer for: ...
✅ Answer: A (index 0)
```

Instead of:
```
❌ GROQ_API_KEY not set!
```

## Alternative: Hardcode in Dockerfile (NOT RECOMMENDED)
If you want to hardcode it in the Dockerfile (security risk):
```dockerfile
ENV GROQ_API_KEY=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
```
