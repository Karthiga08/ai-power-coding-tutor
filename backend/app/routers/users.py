from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.models import QuizResult, Role, Submission, SubmissionStatus, User
from app.schemas import UserOut, UserStatsOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_role(Role.admin))])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.get(
    "/with-stats",
    response_model=list[UserStatsOut],
    dependencies=[Depends(require_role(Role.admin))],
)
async def list_users_with_stats(db: AsyncSession = Depends(get_db)):
    submission_stats = (
        select(
            Submission.user_id,
            func.count(Submission.id).label("total_submissions"),
            func.count(Submission.id).filter(Submission.status == SubmissionStatus.passed).label(
                "passed_submissions"
            ),
        )
        .group_by(Submission.user_id)
        .subquery()
    )
    quiz_stats = (
        select(
            QuizResult.user_id,
            func.avg(QuizResult.score).label("average_quiz_score"),
        )
        .group_by(QuizResult.user_id)
        .subquery()
    )

    result = await db.execute(
        select(
            User,
            func.coalesce(submission_stats.c.total_submissions, 0),
            func.coalesce(submission_stats.c.passed_submissions, 0),
            func.coalesce(quiz_stats.c.average_quiz_score, 0),
        )
        .outerjoin(submission_stats, submission_stats.c.user_id == User.id)
        .outerjoin(quiz_stats, quiz_stats.c.user_id == User.id)
        .order_by(User.created_at.desc())
    )

    return [
        UserStatsOut(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            total_submissions=total_submissions,
            passed_submissions=passed_submissions,
            pass_rate=round(passed_submissions / total_submissions * 100, 1) if total_submissions else 0,
            average_quiz_score=round(float(average_quiz_score), 1),
        )
        for user, total_submissions, passed_submissions, average_quiz_score in result.all()
    ]
