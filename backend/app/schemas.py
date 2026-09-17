import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import Role, SubmissionStatus


# ---- Auth ----
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatsOut(UserOut):
    total_submissions: int
    passed_submissions: int
    pass_rate: float
    average_quiz_score: float


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Courses / Lessons / Problems ----
class LessonOut(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    order_index: int

    class Config:
        from_attributes = True


class LessonCreate(BaseModel):
    title: str
    content: str = ""
    order_index: int = 0


class CourseCreate(BaseModel):
    title: str
    description: str = ""
    difficulty_level: str = "beginner"


class CourseOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    difficulty_level: str
    lessons: list[LessonOut] = []

    class Config:
        from_attributes = True


class ProblemCreate(BaseModel):
    lesson_id: uuid.UUID
    title: str
    description: str = ""
    language: str = "python"
    starter_code: str = ""
    test_cases: list[dict] = []


class ProblemOut(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    title: str
    description: str
    language: str
    starter_code: str
    test_cases: list[dict]

    class Config:
        from_attributes = True


# ---- Submissions ----
class SubmissionCreate(BaseModel):
    problem_id: uuid.UUID
    code: str


class SubmissionOut(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    status: SubmissionStatus
    stdout: str
    stderr: str
    ai_feedback: str
    submitted_at: datetime

    class Config:
        from_attributes = True


# ---- AI Tutor ----
class AIAskRequest(BaseModel):
    context_type: str = "doubt"  # "doubt" | "code_review"
    message: str
    course_id: uuid.UUID | None = None
    problem_id: uuid.UUID | None = None
    code: str | None = None


class AIAskResponse(BaseModel):
    response: str


# ---- Quizzes ----
class QuizCreate(BaseModel):
    course_id: uuid.UUID
    title: str
    questions: list[dict]
    passing_score: int = 60


class QuizQuestionPublic(BaseModel):
    """A question without its correct_index — this is what students see
    before submitting, so the answer key never reaches the browser."""

    question: str
    options: list[str]


class QuizOut(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    questions: list[QuizQuestionPublic]
    passing_score: int

    class Config:
        from_attributes = True


class QuizAttempt(BaseModel):
    answers: list[int]


class QuizResultOut(BaseModel):
    id: uuid.UUID
    quiz_id: uuid.UUID
    score: int
    attempted_at: datetime

    class Config:
        from_attributes = True


# ---- Progress / Analytics ----
class ProgressOut(BaseModel):
    course_id: uuid.UUID
    completion_percent: float
    updated_at: datetime

    class Config:
        from_attributes = True
