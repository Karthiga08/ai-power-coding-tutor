# Free hosting (no credit card)

| Part | Service | Free-tier limits |
|---|---|---|
| Frontend (React) | **Vercel** | None that matter here |
| Backend (FastAPI) | **Render** free web service | Sleeps after 15 min idle (first request then takes 30–60 s); 512 MB RAM |
| Database | **Neon** Postgres | ~0.5–1 GB storage, plenty for this app |
| Code execution | **Judge0 CE** via RapidAPI | Free plan has a small daily quota (check the current number on RapidAPI) |
| AI tutor | **Gemini API** | Rate-limited free tier |

Render's free tier has no Docker daemon, so the backend runs submissions on
Judge0 instead of local sandbox containers (`CODE_RUNNER_BACKEND=judge0`).
For unlimited code execution, use the single-VM setup in `DEPLOY_HETZNER.md`.

Free-tier terms change often. If a service asks for a card, it's usually an
anti-abuse check; you can skip that service and pick an alternative.

## 1. Database: Neon

1. Sign up at <https://neon.tech> (GitHub login works) and create a project, e.g. `ai-tutor`.
2. Copy the **connection string** from the dashboard. It looks like
   `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`.
   Paste it as-is; the backend converts it for asyncpg.

## 2. Seed the course content (from your laptop)

Render's free tier has no shell, so seed Neon directly:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='<your Neon connection string>'
python seed.py                      # creates tables + admin user
python seed_more_courses.py
python seed_java_ruby_problems.py
python seed_extra_lessons.py
python seed_python_oop_errors.py
python seed_more_quiz_questions.py
python seed_prompt_engineering.py
python seed_quicksort_mergesort.py
python seed_remaining_problems.py
python seed_trees_graphs_impl.py
```

**Change the admin password.** `seed.py` creates `admin@example.com` / `admin1234`,
and anyone can read those credentials in this public repo. With `DATABASE_URL` still exported, run:

```bash
python -c "
import asyncio, getpass
from sqlalchemy import update
from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.models import User
pw = getpass.getpass('New admin password: ')
async def main():
    async with AsyncSessionLocal() as db:
        await db.execute(update(User).where(User.email == 'admin@example.com').values(password_hash=hash_password(pw)))
        await db.commit()
asyncio.run(main())
"
```

## 3. Code execution: Judge0 API key

1. Sign up at <https://rapidapi.com> and open **Judge0 CE**: <https://rapidapi.com/judge0-official/api/judge0-ce>.
2. Subscribe to the free **Basic** plan.
3. Copy your **X-RapidAPI-Key** from the endpoint page. This is `JUDGE0_API_KEY`.

No-signup alternative: Judge0's public instance at `https://ce.judge0.com` currently
accepts requests without a key. To use it, set `JUDGE0_URL=https://ce.judge0.com` on Render and
leave `JUDGE0_API_KEY` empty. It's meant for trying Judge0 out, with no guarantees on
limits or uptime, so prefer the RapidAPI key for anything students rely on.

## 4. AI: Gemini API key

Create a key at <https://aistudio.google.com/apikey>. This is `GEMINI_API_KEY`.

## 5. Backend: Render

1. Sign up at <https://render.com> with GitHub.
2. **New → Blueprint**, pick this repo. Render reads `render.yaml`.
3. Fill in the prompted values:
   - `DATABASE_URL`: Neon connection string
   - `GEMINI_API_KEY`: from step 4
   - `JUDGE0_API_KEY`: from step 3
   - `CORS_ORIGINS`: put `http://localhost:5173` for now; you'll update it after step 6
4. Deploy. When it's live, open `https://<service>.onrender.com/api/health` and check that it returns `{"status":"ok"}`.

## 6. Frontend: Vercel

1. Sign up at <https://vercel.com> with GitHub, then **Add New → Project**, and import this repo.
2. Set **Root Directory** to `frontend`. Vercel detects Vite automatically.
3. Under **Environment Variables**, add `VITE_API_URL` = `https://<service>.onrender.com` (no trailing slash).
4. Deploy, then copy the URL, e.g. `https://ai-power-coding-tutor.vercel.app`.

## 7. Connect them

In Render → your service → **Environment**, set `CORS_ORIGINS` to your Vercel URL
(comma-separate several: `https://a.vercel.app,https://b.com`). Save; Render redeploys.

Open the Vercel URL, log in, and solve a problem to check that Run/Submit works end-to-end.

## Updates

Push to `main`: Render and Vercel both redeploy automatically.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| First page load hangs ~1 min | Render free service waking up. Normal. |
| Browser console shows a CORS error | `CORS_ORIGINS` on Render doesn't exactly match the Vercel URL (check `https`, no trailing slash). |
| Submit shows `Sandbox error: Judge0 returned 429` | Daily Judge0 quota used up; it resets the next day. |
| Submit shows `Sandbox error: Judge0 returned 401/403` | `JUDGE0_API_KEY` is wrong, or you're not subscribed to the Basic plan. |
| Java problem fails to compile | Judge0, like the Docker runner, requires `public class Main`. |
