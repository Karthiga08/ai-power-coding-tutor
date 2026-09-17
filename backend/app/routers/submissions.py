import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Problem, Submission, SubmissionStatus, User
from app.schemas import SubmissionCreate, SubmissionOut
from app.services.code_runner import run_submission

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


def _check_test_cases(stdout: str, test_cases: list[dict]) -> bool:
    if not test_cases:
        return True
    actual = stdout.strip()
    return all(actual == str(tc.get("expected_output", "")).strip() for tc in test_cases)


@router.post("", response_model=SubmissionOut)
async def submit_code(
    payload: SubmissionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    problem = await db.get(Problem, payload.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    submission = Submission(
        user_id=user.id,
        problem_id=payload.problem_id,
        code=payload.code,
        status=SubmissionStatus.running,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    result = await run_submission(payload.code, language=problem.language)

    if result.timed_out or result.exit_code != 0:
        submission.status = SubmissionStatus.error
    elif _check_test_cases(result.stdout, problem.test_cases):
        submission.status = SubmissionStatus.passed
    else:
        submission.status = SubmissionStatus.failed

    submission.stdout = result.stdout
    submission.stderr = result.stderr
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/{submission_id}", response_model=SubmissionOut)
async def get_submission(
    submission_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    submission = await db.get(Submission, submission_id)
    if not submission or submission.user_id != user.id:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("", response_model=list[SubmissionOut])
async def my_submissions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Submission).where(Submission.user_id == user.id))
    return result.scalars().all()
