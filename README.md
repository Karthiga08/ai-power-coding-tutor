# AI Power Coding Tutor

An AI-driven personalized programming education platform: React + Tailwind
frontend, FastAPI backend, PostgreSQL, JWT auth, Docker-sandboxed code
execution, and an OpenAI/Gemini-backed AI tutor. Scaffolded from the project
report's architecture (chapters 4–6).

## What's implemented

- JWT auth (register/login, roles: student / instructor / admin)
- Course → Lesson → Problem hierarchy with CRUD for admins/instructors
- Multi-language code submission (Python, Java, Ruby) executed inside a
  locked-down, throwaway Docker container per language (no network, capped
  CPU/memory, hard timeout) — `backend/app/services/code_runner.py`. Java
  problems are compiled (`javac`) then run; each `Problem` has a `language`
  field selecting the runner/image.
- Context-aware AI tutor endpoint that folds in lesson content, problem
  statement, and the student's current code — `backend/app/services/ai_service.py`
- Quizzes with scoring that rolls into a course `Progress` record, and a real
  quiz-taking page (`frontend/src/pages/Quiz.jsx`) — the answer key
  (`correct_index`) is stripped server-side before a quiz reaches the
  browser (`QuizQuestionPublic` in `schemas.py`), so a student can't just
  read it out of the network tab
- Student progress chart (Recharts) and an admin analytics dashboard
- React frontend: auth pages, course browser, a problem-solving page with a
  real CodeMirror 6 editor (syntax highlighting per `problem.language`, line
  numbers, folding, autocomplete) + AI chat panel, a quiz-taking page,
  progress and admin dashboards — `frontend/src/components/CodeEditor.jsx`
- Five seeded courses: Python Fundamentals, Data Structures & Algorithms,
  Java Programming, Ruby on Rails Web Development, and AI & ML Fundamentals

## What's intentionally left for you to extend

- Alembic migrations (tables/columns are currently created via `create_all`
  plus manual `ALTER TABLE`s for local dev — fine for dev, not for schema
  evolution in production)
- Streaming AI responses (SSE/WebSocket) instead of a single blocking call
- A job queue (Celery/RQ) for code execution instead of running it inline on
  the request — matters once you have concurrent submissions
- More languages (C/C++, JavaScript, Go) — follow the same pattern as
  `docker/runner-java` / `docker/runner-ruby`: a Dockerfile plus an entry in
  `LANGUAGES` in `code_runner.py`
- Rate limiting / per-user AI usage caps

## Quickstart (Docker)

```bash
cp .env.example .env
# edit .env: set OPENAI_API_KEY or GEMINI_API_KEY, and a real JWT_SECRET

docker build -t ai-tutor-runner-python:latest ./docker/runner-python
docker build -t ai-tutor-runner-java:latest ./docker/runner-java
docker build -t ai-tutor-runner-ruby:latest ./docker/runner-ruby
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs

Seed sample data — run each in order (later scripts build on earlier ones;
each is idempotent, so re-running is safe):

```bash
docker compose exec backend python seed.py                      # admin user + Python Fundamentals course
docker compose exec backend python seed_more_courses.py         # Data Structures, Java, Rails, AI courses
docker compose exec backend python seed_java_ruby_problems.py   # runnable Java/Ruby coding problems
docker compose exec backend python seed_extra_lessons.py        # more lessons across all 5 courses
docker compose exec backend python seed_python_oop_errors.py    # OOP + error handling lessons
```

Then log in as `admin@example.com` / `admin1234`.

## Quickstart (without Docker Compose, for local dev)

You still need Docker running locally for code execution (`code_runner.py`
talks to the Docker daemon via the SDK), and a Postgres instance.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker build -t ai-tutor-runner-python:latest ../docker/runner-python
docker build -t ai-tutor-runner-java:latest ../docker/runner-java
docker build -t ai-tutor-runner-ruby:latest ../docker/runner-ruby
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Architecture

```
frontend (React + Tailwind, Vite)
   │  REST + JWT bearer
   ▼
backend (FastAPI, async SQLAlchemy)
   ├── PostgreSQL          — users, courses, submissions, quizzes, progress
   ├── OpenAI / Gemini API — AI tutor (context-aware prompts)
   └── Docker daemon       — sandboxed execution of submitted code
```

## Security note on the Docker socket mount

`docker-compose.yml` mounts `/var/run/docker.sock` into the backend
container so it can launch sandbox containers via the Docker SDK. This is
convenient for local development but gives the backend container control
of the host's Docker daemon — effectively root on the host. Do not deploy
this as-is. For production, move code execution into a separate worker
service that either runs in its own isolated VM/Firecracker sandbox or
talks to a remote, access-controlled Docker API (e.g. a dedicated
execution cluster), not the same daemon running your other containers.
