import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import Progress, Quiz, QuizResult, Role, User
from app.schemas import QuizAttempt, QuizCreate, QuizOut, QuizResultOut

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


@router.get("/by-course/{course_id}", response_model=list[QuizOut])
async def list_quizzes_for_course(course_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quiz).where(Quiz.course_id == course_id))
    return result.scalars().all()


@router.get("/{quiz_id}", response_model=QuizOut)
async def get_quiz(quiz_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    quiz = await db.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("", response_model=QuizOut, dependencies=[Depends(require_role(Role.admin, Role.instructor))])
async def create_quiz(payload: QuizCreate, db: AsyncSession = Depends(get_db)):
    quiz = Quiz(**payload.model_dump())
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)
    return quiz


@router.post("/{quiz_id}/attempt", response_model=QuizResultOut)
async def attempt_quiz(
    quiz_id: uuid.UUID,
    payload: QuizAttempt,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await db.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    correct = sum(
        1
        for q, given in zip(quiz.questions, payload.answers)
        if given == q.get("correct_index")
    )
    score = round((correct / len(quiz.questions)) * 100) if quiz.questions else 0

    result = QuizResult(user_id=user.id, quiz_id=quiz_id, score=score)
    db.add(result)

    # Roll the quiz result into course progress (simple weighted average).
    existing = await db.execute(
        select(Progress).where(Progress.user_id == user.id, Progress.course_id == quiz.course_id)
    )
    progress = existing.scalar_one_or_none()
    if progress:
        progress.completion_percent = min(100.0, (progress.completion_percent + score) / 2)
    else:
        db.add(Progress(user_id=user.id, course_id=quiz.course_id, completion_percent=float(score)))

    await db.commit()
    await db.refresh(result)
    return result
