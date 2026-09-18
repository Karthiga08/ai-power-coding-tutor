# 🚀 Quick Reference Card - Deployment

## Your Generated Secrets (Save in Password Manager!)

```
JWT_SECRET: wyC24snSeBpIMkW1lv440dDp6rm3iLpjyPBW6HlaBu8
DATABASE PASSWORD: _8NiopcQSXSeezzSbKe7qg
```

---

## Step-by-Step Deployment Checklist

### ☐ Step 1: Get AI API Key (5 min)
```
1. Go to: https://ai.google.dev
2. Click "Get API Key" → "Create API Key"
3. Copy the API key and save in password manager
```

### ☐ Step 2: Deploy Database on Render (5 min)
```
1. Go to: https://render.com/dashboard
2. Click: New + → PostgreSQL
3. Fill:
   - Name: ai-tutor-db
   - Database: ai_coding_tutor
   - User: tutor
   - Password: _8NiopcQSXSeezzSbKe7qg
   - Region: Choose closest to you
   - Version: 15+
   - Plan: Free
4. Wait for creation (2-3 min)
5. Copy External Connection String → Save in password manager
```

### ☐ Step 3: Deploy Backend on Render (10 min)
```
1. Go to: https://render.com/dashboard
2. Click: New + → Web Service
3. Click: Connect GitHub → Authorize → Select repository
4. Fill:
   - Name: ai-tutor-backend
   - Branch: main
   - Root Directory: backend
   - Runtime: Python 3
   - Build: pip install -r requirements.txt
   - Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   - Plan: Free
5. Click: Advanced → Add Environment Variables:
   DATABASE_URL=postgresql+asyncpg://tutor:PASSWORD@HOST:5432/ai_coding_tutor
   JWT_SECRET=wyC24snSeBpIMkW1lv440dDp6rm3iLpjyPBW6HlaBu8
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your-gemini-api-key
   CORS_ORIGINS=http://localhost:5173
   ENVIRONMENT=production
6. Click: Create Web Service
7. Wait for deployment (5 min)
8. Save Backend URL: https://ai-tutor-backend.onrender.com
9. Test: curl https://ai-tutor-backend.onrender.com/api/health
```

### ☐ Step 4: Deploy Frontend on Vercel (10 min)
```
1. Go to: https://vercel.com/dashboard
2. Click: Add New → Project
3. Click: Import Git Repository
4. Select: Your repository
5. Fill:
   - Framework: Vite
   - Root Directory: frontend
   - Build Command: npm run build
   - Output Directory: dist
6. Click: Deploy
7. Wait for deployment (3 min)
8. Save Frontend URL: https://your-project.vercel.app
9. Go to: Settings → Environment Variables
10. Add: VITE_API_URL=https://ai-tutor-backend.onrender.com
11. Click: Deploy again
```

### ☐ Step 5: Update Backend CORS (2 min)
```
1. Go to: https://render.com/dashboard
2. Click: ai-tutor-backend service
3. Go to: Settings → Environment
4. Update: CORS_ORIGINS=https://your-project.vercel.app
5. Click: Save Changes (auto-redeployed)
```

### ☐ Step 6: Test Everything (5 min)
```
✓ Test Frontend: Open https://your-project.vercel.app
✓ Test Backend: curl https://ai-tutor-backend.onrender.com/api/health
✓ Test Login: Try logging in from frontend
✓ Check Console: No CORS errors in browser developer tools
```

---

## Environment Variables Reference

### Backend (.env on Render)
```bash
DATABASE_URL=postgresql+asyncpg://tutor:PASSWORD@HOST:5432/ai_coding_tutor
JWT_SECRET=wyC24snSeBpIMkW1lv440dDp6rm3iLpjyPBW6HlaBu8
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

AI_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
OPENAI_API_KEY=(leave empty)

CORS_ORIGINS=https://your-frontend-url.vercel.app
ENVIRONMENT=production
```

### Frontend (.env on Vercel)
```bash
VITE_API_URL=https://your-backend.onrender.com
```

---

## Important URLs

| Service | URL |
|---------|-----|
| **Render Dashboard** | https://render.com/dashboard |
| **Vercel Dashboard** | https://vercel.com/dashboard |
| **Google Gemini** | https://ai.google.dev |
| **GitHub** | https://github.com/Karthiga08/ai-power-coding-tutor |

---

## Documentation Files

📖 **DEPLOYMENT_GUIDE.md** - Complete step-by-step guide (READ THIS)
✅ **DEPLOYMENT_CHECKLIST.md** - Detailed checklist with all details
📋 **DEPLOYMENT_SUMMARY.md** - Architecture and resource overview

---

## Estimated Timeline

| Step | Time | Notes |
|------|------|-------|
| Step 1: AI API Key | 5 min | Google Gemini signup |
| Step 2: Database | 5 min | Render PostgreSQL |
| Step 3: Backend | 10 min | Render Web Service |
| Step 4: Frontend | 10 min | Vercel deployment |
| Step 5: CORS | 2 min | Backend configuration |
| Step 6: Testing | 5 min | Verify everything works |
| **Total** | **~37 min** | Plus waiting for services (10-15 min) |

---

## Useful Commands

```bash
# Test backend health
curl https://your-backend.onrender.com/api/health

# View GitHub repository
https://github.com/Karthiga08/ai-power-coding-tutor

# SSH into Render shell (if needed)
# Via Render dashboard → Service → Shell tab

# View logs
# Render: Dashboard → Service → Logs
# Vercel: Dashboard → Deployments → Logs
```

---

## Cost Summary

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Vercel | FREE | Global CDN |
| Render Backend | FREE | Sleeps after 15 min |
| Render DB | FREE | 500 MB storage |
| Gemini API | FREE | 15 requests/min |
| **TOTAL** | **$0/month** | Perfect for testing |

---

## Need Help?

1. **For step-by-step guidance**: Read `DEPLOYMENT_GUIDE.md`
2. **For detailed checklist**: Use `DEPLOYMENT_CHECKLIST.md`
3. **For troubleshooting**: See `DEPLOYMENT_GUIDE.md` → Troubleshooting section
4. **For architecture details**: Read `DEPLOYMENT_SUMMARY.md`

---

**Last Updated**: 2026-09-18
**Status**: ✅ Ready to Deploy
