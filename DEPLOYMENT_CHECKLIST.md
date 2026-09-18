# 🚀 Cloud Deployment Checklist - AI Power Coding Tutor

## Pre-Deployment Setup (Local)

### Code Preparation
- [ ] All changes committed to Git
- [ ] No uncommitted files (`git status` is clean)
- [ ] `.env` file is in `.gitignore`
- [ ] All environment variables documented in `.env.example`
- [ ] No hardcoded secrets in code
- [ ] Database migrations reviewed
- [ ] Tests pass locally:
  ```bash
  cd backend && pytest
  cd frontend && npm run build
  ```

### Generate Secrets
- [ ] Generate JWT Secret (32+ chars): `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Generate DB password (16+ chars): `python3 -c "import secrets; print(secrets.token_urlsafe(16))"`
- [ ] Obtain AI API keys:
  - [ ] Google Gemini API key (recommended - cheaper)
  - [ ] OpenAI API key (optional, if using OpenAI)

---

## Step 1: Prepare Accounts

### Cloud Services
- [ ] Vercel account created (https://vercel.com/signup)
- [ ] Render account created (https://render.com/signup)
- [ ] GitHub repository is public or Render has access

### AI Services
- [ ] Google Gemini account with API key (https://ai.google.dev)
  - [ ] API key copied and saved securely
  - [ ] Billing configured (if exceeding free tier)
- [ ] OpenAI account (optional, if using OpenAI instead)
  - [ ] API key copied and saved securely

---

## Step 2: Deploy Database

### Render PostgreSQL Setup
- [ ] Visit https://render.com/dashboard
- [ ] Click "New +" → "PostgreSQL"
- [ ] Configuration Details:
  - [ ] Name: `ai-tutor-db`
  - [ ] Database: `ai_coding_tutor`
  - [ ] User: `tutor`
  - [ ] Region: Selected (closest to users)
  - [ ] PostgreSQL Version: 15+
  - [ ] Plan: Free (or Starter for production)
- [ ] Database created and ready
- [ ] Connection string saved securely:
  ```
  postgresql+asyncpg://tutor:PASSWORD@HOST:5432/ai_coding_tutor
  ```
- [ ] Connection tested from local machine (optional):
  ```bash
  psql postgresql://tutor:password@HOST:5432/ai_coding_tutor -c "SELECT 1"
  ```

---

## Step 3: Deploy Backend API

### Create Render Web Service
- [ ] Visit https://render.com/dashboard
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub:
  - [ ] Click "Connect GitHub"
  - [ ] Authorize Render
  - [ ] Select your project repository
- [ ] Service Configuration:
  - [ ] Name: `ai-tutor-backend`
  - [ ] Branch: `main`
  - [ ] Root Directory: `backend`
  - [ ] Runtime: `Python 3`
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - [ ] Plan: Free (test) or Starter (production)

### Environment Variables on Render
- [ ] Click "Advanced" → Add environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://tutor:PASSWORD@HOST:5432/ai_coding_tutor` | From Step 2 |
| `JWT_SECRET` | 32+ character random string | Generate with python3 -c |
| `AI_PROVIDER` | `gemini` | Gemini is cheaper than OpenAI |
| `GEMINI_API_KEY` | Your Gemini API key | From AI services setup |
| `OPENAI_API_KEY` | (leave empty) | If not using OpenAI |
| `CORS_ORIGINS` | `http://localhost:5173` | Update later with Vercel URL |
| `ENVIRONMENT` | `production` | For production deployments |

- [ ] All required variables added (no empty critical ones)
- [ ] Web service deployed
- [ ] Deployment successful (check Events tab)
- [ ] Service URL noted: `https://ai-tutor-backend.onrender.com`
- [ ] Health check passes:
  ```bash
  curl https://ai-tutor-backend.onrender.com/api/health
  # Should return: {"status":"ok"}
  ```

---

## Step 4: Deploy Frontend

### Create Vercel Project
- [ ] Visit https://vercel.com/dashboard
- [ ] Click "Add New..." → "Project"
- [ ] Import GitHub Repository:
  - [ ] Search for your project
  - [ ] Click "Import"
- [ ] Project Configuration:
  - [ ] Framework: Select "Vite"
  - [ ] Root Directory: `frontend`
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `dist`
  - [ ] Install Command: `npm ci`

### Environment Variables on Vercel
- [ ] Go to "Settings" → "Environment Variables"
- [ ] Add variable:
  - [ ] Name: `VITE_API_URL`
  - [ ] Value: `https://ai-tutor-backend.onrender.com`
  - [ ] Environment: Production, Preview, Development
- [ ] Save and redeploy

### Deployment
- [ ] Click "Deploy"
- [ ] Wait for deployment to complete (2-3 minutes)
- [ ] Deployment successful (check status)
- [ ] Frontend URL noted: `https://your-project.vercel.app`
- [ ] Frontend loads without errors
- [ ] Can reach backend API from frontend console

---

## Step 5: Update CORS Configuration

### Update Backend CORS
- [ ] Go to Render dashboard
- [ ] Click `ai-tutor-backend` service
- [ ] Go to "Settings" → "Environment"
- [ ] Update `CORS_ORIGINS`:
  ```
  https://your-project.vercel.app
  ```
- [ ] Click "Save Changes"
- [ ] Service auto-redeployed
- [ ] Wait for new deployment to complete

---

## Step 6: Configure CI/CD (GitHub Actions)

### Add GitHub Secrets
- [ ] Go to GitHub: Settings → Secrets and variables → Actions
- [ ] Add secrets:

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `RENDER_DEPLOY_HOOK` | From Render service "Deploy" tab | Render Dashboard → Service → Deploy |
| `VERCEL_TOKEN` | From Vercel Account Settings | Vercel → Settings → Tokens |
| `VERCEL_ORG_ID` | From Vercel Team settings | Vercel → Team Settings |
| `VERCEL_PROJECT_ID` | From Vercel Project settings | Vercel → Project → Settings → General |

### GitHub Actions Workflow
- [ ] `.github/workflows/deploy.yml` exists
- [ ] Workflow file reviewed for correctness
- [ ] Test run completed successfully:
  ```bash
  git commit --allow-empty -m "Test CI/CD"
  git push origin main
  ```
- [ ] Check GitHub Actions → Workflow status
- [ ] Both Render and Vercel auto-deployed

---

## Step 7: Post-Deployment Verification

### Frontend Tests
- [ ] Frontend loads without errors
- [ ] Navigation works
- [ ] Can access course list
- [ ] API calls succeed (check browser Network tab)
- [ ] No 403/CORS errors in console

### Backend Tests
- [ ] Health check endpoint works: `GET /api/health`
- [ ] Database connected (check Render logs)
- [ ] Authentication works: `POST /api/auth/login`
- [ ] No errors in Render logs

### Database Tests
- [ ] Database accessible from backend
- [ ] Initial data seeded (if applicable)
- [ ] Can query tables: `SELECT COUNT(*) FROM users;`

### AI Service Tests
- [ ] Gemini/OpenAI API keys valid
- [ ] At least 1 test request succeeds
- [ ] API rate limits understood

---

## Step 8: Monitoring Setup

### Enable Render Monitoring
- [ ] Go to Render dashboard
- [ ] Enable notifications for:
  - [ ] Deployment failures
  - [ ] Service restarts
  - [ ] Database errors

### Enable Vercel Monitoring
- [ ] Go to Vercel dashboard
- [ ] Enable:
  - [ ] Deployment notifications
  - [ ] Performance alerts
  - [ ] Error tracking

### Monitor Logs
- [ ] Render backend logs monitored regularly
- [ ] Vercel deployment logs reviewed
- [ ] Database query logs checked
- [ ] Error rate monitored

---

## Step 9: Security Hardening

### Secrets Management
- [ ] No secrets in GitHub (verified with: `git log -p | grep -i "secret\|password\|key"`)
- [ ] All sensitive values in Render/Vercel environment variables
- [ ] JWT secret is strong (32+ random characters)
- [ ] Database password is strong (16+ random characters)

### CORS Security
- [ ] `CORS_ORIGINS` is specific (not `*`)
- [ ] Only production frontend URL allowed
- [ ] Verified with CORS test:
  ```bash
  curl -H "Origin: https://evil.com" https://api.onrender.com/api/health
  # Should NOT include Access-Control-Allow-Origin header
  ```

### HTTPS
- [ ] Frontend: HTTPS enabled (automatic on Vercel)
- [ ] Backend: HTTPS enabled (automatic on Render)
- [ ] All API calls use HTTPS

### Authentication
- [ ] JWT tokens have expiration
- [ ] Refresh tokens implemented
- [ ] Passwords are hashed (bcrypt)
- [ ] No default credentials in production

---

## Step 10: Documentation

### Update Documentation
- [ ] README.md updated with production URLs
- [ ] DEPLOYMENT_GUIDE.md reviewed and complete
- [ ] Environment variables documented in `.env.example`
- [ ] API documentation accessible (FastAPI Swagger at `/docs`)

### Team Communication
- [ ] Production URL shared with team
- [ ] Database access procedures documented
- [ ] Incident response plan documented
- [ ] On-call rotation established

---

## Performance Optimization

### Frontend
- [ ] Build size optimized (check Vercel Analytics)
- [ ] Images compressed
- [ ] Code splitting enabled
- [ ] Caching headers configured
- [ ] Core Web Vitals checked

### Backend
- [ ] Database indexes created for common queries
- [ ] Slow query log reviewed
- [ ] API response times < 500ms (average)
- [ ] Error rate < 0.1%

### Database
- [ ] Connection pooling configured
- [ ] Query plans optimized
- [ ] Backup strategy verified

### AI Services
- [ ] Rate limiting implemented
- [ ] Response caching where applicable
- [ ] API quota monitoring enabled
- [ ] Cost tracking enabled

---

## Cost Monitoring

### Set Budget Alerts
- [ ] Google Gemini API: Enable billing alerts in Google Cloud Console
- [ ] OpenAI (if used): Enable usage alerts
- [ ] Render: Enable cost alerts if on paid plan
- [ ] Vercel: Free tier, but monitor usage

### Estimated Monthly Costs
- [ ] Vercel Frontend: $0/month (free tier)
- [ ] Render Backend: $0-7/month (free/starter)
- [ ] Render PostgreSQL: $0-15/month (free/starter)
- [ ] AI API: $10-100/month (usage-dependent)
- [ ] **Total**: $10-122/month

---

## Rollback Plan

### If Deployment Fails
- [ ] Check GitHub Actions logs
- [ ] Review recent commits for breaking changes
- [ ] Render auto-rollback: Previous build available
- [ ] Vercel auto-rollback: Previous deployment available
- [ ] Manual rollback: Revert commit and push

### Database Issues
- [ ] Backup available from Render
- [ ] Can restore from backup if needed
- [ ] Migration tested before running on production

---

## Final Sign-Off

- [ ] All steps completed
- [ ] All verification tests passed
- [ ] Team notified
- [ ] Documentation complete
- [ ] Monitoring active
- [ ] Ready for production traffic

**Deployment Date**: ___________
**Deployed By**: ___________
**Sign-off By**: ___________

---

## Useful Commands

```bash
# Check deployment status
curl https://ai-tutor-backend.onrender.com/api/health

# View recent commits
git log --oneline -10

# SSH into Render shell (if needed)
# Via Render dashboard → Shell tab

# Check Vercel deployment
# Via Vercel dashboard → Deployments tab

# Monitor real-time logs
# Render: Dashboard → Service → Logs (tail)
# Vercel: Dashboard → Project → Deployments → Logs
```

---

**Last Updated**: 2026-09-18
**Version**: 1.0
