from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import ai_tutor, analytics, auth, courses, problems, quizzes, submissions, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience only — use Alembic migrations in production.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="AI Power Coding Tutor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(problems.router)
app.include_router(submissions.router)
app.include_router(ai_tutor.router)
app.include_router(quizzes.router)
app.include_router(analytics.router)
app.include_router(users.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
