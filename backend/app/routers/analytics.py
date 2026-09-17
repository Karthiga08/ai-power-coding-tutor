from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import Progress, QuizResult, Role, Submission, SubmissionStatus, User
from app.schemas import ProgressOut

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/me", response_model=list[ProgressOut])
async def my_progress(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Progress).where(Progress.user_id == user.id))
    return result.scalars().all()


@router.get("/admin", dependencies=[Depends(require_role(Role.admin))])
async def platform_analytics(db: AsyncSession = Depends(get_db)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_submissions = (await db.execute(select(func.count(Submission.id)))).scalar_one()
    passed_submissions = (
        await db.execute(select(func.count(Submission.id)).where(Submission.status == SubmissionStatus.passed))
    ).scalar_one()
    avg_quiz_score = (await db.execute(select(func.avg(QuizResult.score)))).scalar() or 0

    return {
        "total_users": total_users,
        "total_submissions": total_submissions,
        "passed_submissions": passed_submissions,
        "pass_rate": round(passed_submissions / total_submissions * 100, 1) if total_submissions else 0,
        "average_quiz_score": round(float(avg_quiz_score), 1),
    }
