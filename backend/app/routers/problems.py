import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.models import Problem, Role
from app.schemas import ProblemCreate, ProblemOut

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("/{problem_id}", response_model=ProblemOut)
async def get_problem(problem_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    problem = await db.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.get("/by-lesson/{lesson_id}", response_model=list[ProblemOut])
async def list_problems_for_lesson(lesson_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Problem).where(Problem.lesson_id == lesson_id))
    return result.scalars().all()


@router.post("", response_model=ProblemOut, dependencies=[Depends(require_role(Role.admin, Role.instructor))])
async def create_problem(payload: ProblemCreate, db: AsyncSession = Depends(get_db)):
    problem = Problem(**payload.model_dump())
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem
