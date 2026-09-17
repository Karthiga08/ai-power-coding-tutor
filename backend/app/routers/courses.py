import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_role
from app.database import get_db
from app.models import Course, Lesson, Role
from app.schemas import CourseCreate, CourseOut, LessonCreate, LessonOut

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut])
async def list_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).options(selectinload(Course.lessons)))
    return result.scalars().all()


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(course_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course).where(Course.id == course_id).options(selectinload(Course.lessons))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("", response_model=CourseOut, dependencies=[Depends(require_role(Role.admin, Role.instructor))])
async def create_course(payload: CourseCreate, db: AsyncSession = Depends(get_db)):
    course = Course(**payload.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    course.lessons = []
    return course


@router.post(
    "/{course_id}/lessons",
    response_model=LessonOut,
    dependencies=[Depends(require_role(Role.admin, Role.instructor))],
)
async def add_lesson(course_id: uuid.UUID, payload: LessonCreate, db: AsyncSession = Depends(get_db)):
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson = Lesson(course_id=course_id, **payload.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson
