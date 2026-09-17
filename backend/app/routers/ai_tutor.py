from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import AIInteraction, Lesson, Problem, User
from app.schemas import AIAskRequest, AIAskResponse
from app.services.ai_service import ask_ai_tutor, build_prompt

router = APIRouter(prefix="/api/ai", tags=["ai-tutor"])


@router.post("/ask", response_model=AIAskResponse)
async def ask(
    payload: AIAskRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson_content = None
    problem_description = None

    if payload.problem_id:
        problem = await db.get(Problem, payload.problem_id)
        if problem:
            problem_description = problem.description
            lesson = await db.get(Lesson, problem.lesson_id)
            lesson_content = lesson.content if lesson else None

    prompt = build_prompt(
        message=payload.message,
        context_type=payload.context_type,
        lesson_content=lesson_content,
        problem_description=problem_description,
        code=payload.code,
    )
    response_text = await ask_ai_tutor(prompt)

    db.add(
        AIInteraction(
            user_id=user.id,
            context_type=payload.context_type,
            prompt=payload.message,
            response=response_text,
        )
    )
    await db.commit()

    return AIAskResponse(response=response_text)


@router.get("/history")
async def history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AIInteraction).where(AIInteraction.user_id == user.id).order_by(AIInteraction.created_at.desc())
    )
    return result.scalars().all()
