# AI Power Coding Tutor - Cloud Deployment Guide

## Overview

This guide covers deploying the AI Power Coding Tutor to production using:
- **Frontend**: Vercel (React + Vite)
- **Backend**: Render (FastAPI)
- **Database**: PostgreSQL on Render
- **AI Services**: Google Gemini API (recommended) or OpenAI API

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Prepare Repository](#step-1-prepare-repository)
3. [Step 2: Deploy Database](#step-2-deploy-database)
4. [Step 3: Deploy Backend](#step-3-deploy-backend)
5. [Step 4: Deploy Frontend](#step-4-deploy-frontend)
6. [Step 5: Configure CI/CD](#step-5-configure-cicd)
7. [Environment Variables](#environment-variables)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, you need:

### Accounts
- [ ] GitHub account (for repository)
- [ ] Vercel account (https://vercel.com)
- [ ] Render account (https://render.com)
- [ ] Google Gemini API account (https://ai.google.dev) OR OpenAI account (https://platform.openai.com)

### Local Setup
- [ ] Git installed
- [ ] Python 3.11+
- [ ] Node.js 18+
- [ ] Docker Desktop (for testing locally)

### Generated Secrets
- [ ] JWT Secret (32+ random characters)
- [ ] Database password (16+ characters)
- [ ] AI API keys

**Generate secrets:**
```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

---

## Step 1: Prepare Repository

### 1.1 Clean Up Local Environment Files

```bash
cd /Users/apple/project

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore

git add .gitignore
git commit -m "Update .gitignore for environment files"
```

### 1.2 Verify All Changes Are Committed

```bash
git status  # Should show clean working directory
```

### 1.3 Push to GitHub

```bash
git push origin main
```

---

## Step 2: Deploy Database

### 2.1 Create PostgreSQL on Render

1. Go to https://render.com/dashboard
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `ai-tutor-db`
   - **Database**: `ai_coding_tutor`
   - **User**: `tutor`
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 15
   - **Plan**: Free (or Starter for production)

4. Click "Create Database"
5. Wait for database to be ready (2-3 minutes)
6. Copy the **External Database URL** (looks like: `postgresql://tutor:password@host:5432/ai_coding_tutor`)

### 2.2 Save Database Credentials

Store these securely (LastPass, 1Password, etc.):
```
Host: [from connection string]
Database: ai_coding_tutor
User: tutor
Password: [from connection string]
Connection String: postgresql+asyncpg://tutor:password@host:5432/ai_coding_tutor
```

---

## Step 3: Deploy Backend

### 3.1 Create Web Service on Render

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Select "Deploy from Git"
4. Click "Connect GitHub"
   - Authorize Render to access GitHub
   - Select your `project` repository
   - Click "Connect"

### 3.2 Configure Web Service

**Basic Settings:**
- **Name**: `ai-tutor-backend`
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- **Plan**: Free (or Starter for production)

### 3.3 Add Environment Variables

Click "Advanced" → "Add Environment Variable"

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql+asyncpg://tutor:PASSWORD@HOST:5432/ai_coding_tutor` |
| `JWT_SECRET` | Generate 32+ character secret |
| `AI_PROVIDER` | `gemini` |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `OPENAI_API_KEY` | (leave empty if using Gemini) |
| `CORS_ORIGINS` | `https://your-frontend-url.vercel.app` |
| `ENVIRONMENT` | `production` |

**Important**: Update these values with real secrets!

### 3.4 Deploy

1. Click "Create Web Service"
2. Monitor deployment in the "Events" tab
3. Once complete, note the service URL (e.g., `https://ai-tutor-backend.onrender.com`)

### 3.5 Test Backend

```bash
curl https://ai-tutor-backend.onrender.com/api/health
# Should return: {"status":"ok"}
```

---

## Step 4: Deploy Frontend

### 4.1 Deploy to Vercel

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Select "Import Git Repository"
4. Search for and select your GitHub repository
5. Click "Import"

### 4.2 Configure Project

**Framework Settings:**
- **Framework**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 4.3 Add Environment Variables

Go to "Settings" → "Environment Variables"

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://ai-tutor-backend.onrender.com` |

### 4.4 Deploy

1. Click "Deploy"
2. Wait for deployment to complete (2-3 minutes)
3. Click the deployed URL to verify the frontend loads

### 4.5 Update Backend CORS

Now that you have the Vercel URL, update the backend:

1. Go to Render dashboard
2. Click your backend service
3. Go to "Settings" → "Environment"
4. Update `CORS_ORIGINS`:
   ```
   https://your-frontend-url.vercel.app
   ```
5. Click "Save Changes" (will auto-redeploy)

---

## Step 5: Configure CI/CD

### 5.1 Add GitHub Secrets

Go to GitHub repository → "Settings" → "Secrets and variables" → "Actions"

Add these secrets:

| Secret | Value |
|--------|-------|
| `RENDER_DEPLOY_HOOK` | From Render service "Deploy" tab → "Deploy Hook" |
| `VERCEL_TOKEN` | From Vercel Account Settings → Tokens |
| `VERCEL_ORG_ID` | From Vercel Team settings |
| `VERCEL_PROJECT_ID` | From Vercel Project settings |

### 5.2 GitHub Actions Already Configured

The `.github/workflows/deploy.yml` file is already set up to:
- Automatically test backend on every push
- Automatically test frontend on every push
- Deploy to Render on push to `main`
- Deploy to Vercel on push to `main`

Push a test commit to verify:
```bash
git commit --allow-empty -m "Test CI/CD pipeline"
git push origin main
```

Monitor progress:
1. Go to "Actions" tab in GitHub
2. Watch the workflow run
3. Check Vercel and Render dashboards for deployments

---

## Environment Variables

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `JWT_SECRET` | Secret key for JWT tokens | 32+ random chars |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |
| `AI_PROVIDER` | AI service provider | `gemini` or `openai` |
| `GEMINI_API_KEY` | Google Gemini API key | Your API key |
| `OPENAI_API_KEY` | OpenAI API key | Your API key |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |
| `GEMINI_MODEL` | Gemini model name | `gemini-3.6-flash` |
| `CORS_ORIGINS` | Allowed frontend URLs | `https://example.vercel.app` |
| `ENVIRONMENT` | App environment | `production` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://ai-tutor-backend.onrender.com` |

### Generate Secure Secrets

```bash
# JWT Secret (32+ characters)
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"

# Database password
python3 -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(16))"
```

---

## Monitoring & Maintenance

### 4.1 View Logs

**Render Backend Logs:**
1. Go to https://render.com/dashboard
2. Click your backend service
3. Go to "Logs" tab
4. View real-time logs

**Vercel Frontend Logs:**
1. Go to https://vercel.com/dashboard
2. Click your project
3. Go to "Logs" section

### 4.2 Monitor Performance

**Backend Metrics:**
- Average response time
- Error rate
- Database query performance

**Frontend Metrics:**
- Page load time
- Core Web Vitals
- Build size

### 4.3 Database Backups

Render automatically backs up PostgreSQL. To manually backup:

```bash
# Export database
pg_dump postgresql://tutor:password@host:5432/ai_coding_tutor > backup.sql

# Restore database
psql postgresql://tutor:password@host:5432/ai_coding_tutor < backup.sql
```

### 4.4 Update Dependencies

```bash
# Backend
cd backend
pip list --outdated
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm outdated
npm update
```

---

## Troubleshooting

### Frontend Not Loading

**Issue**: Blank page or connection errors

**Solution**:
1. Check browser console for errors
2. Verify `VITE_API_URL` environment variable
3. Check Vercel deployment logs
4. Verify backend is running: `curl https://ai-tutor-backend.onrender.com/api/health`

### API Connection Errors

**Issue**: `CORS error` or `Connection refused`

**Solution**:
1. Check backend is running (Render dashboard)
2. Verify `CORS_ORIGINS` includes frontend URL
3. Check backend logs for errors
4. Wait 30 seconds for backend to wake up (free tier)

### Database Connection Errors

**Issue**: `Connection refused` or `no pg_hba.conf entry`

**Solution**:
1. Verify `DATABASE_URL` is correct
2. Check database is running (Render dashboard)
3. Verify database password
4. Run migrations: `alembic upgrade head`

### Slow Performance

**Issue**: Slow API responses or timeouts

**Solution**:
1. Upgrade from free tier to Starter
2. Optimize database queries
3. Add caching (Redis)
4. Reduce API call frequency
5. Use cheaper AI model (Gemini vs OpenAI)

### Deployment Failures

**Issue**: GitHub Actions workflow fails

**Solution**:
1. Check GitHub Actions logs
2. Verify all environment variables are set
3. Check for syntax errors in code
4. Run tests locally first:
   ```bash
   cd backend && pytest tests/
   cd frontend && npm run build
   ```

---

## Cost Estimation

| Service | Free Tier | Starter | Notes |
|---------|-----------|---------|-------|
| Vercel | $0/month | $20/month | Frontend hosting |
| Render | $0/month (sleeps) | $7/month | Backend API |
| Render PostgreSQL | $0/month (500MB) | $15/month | Database |
| Gemini API | $0 (15 req/min) | Pay-as-you-go | AI service |
| **Total** | **$0/month** | **$22+/month** | Production ready |

---

## Production Checklist

- [ ] Database created and migrated
- [ ] Backend deployed and health check working
- [ ] Frontend deployed and connected to backend
- [ ] Environment variables configured
- [ ] GitHub secrets added
- [ ] CI/CD pipeline tested
- [ ] Logs monitored for errors
- [ ] CORS configuration correct
- [ ] HTTPS enabled (automatic)
- [ ] Backups configured
- [ ] Performance baseline established
- [ ] Error monitoring set up
- [ ] Team notified of live URL

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**Last Updated**: 2026-09-18
**Version**: 1.0
