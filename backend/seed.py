"""
One-off dev seeding: an admin user, a sample course/lesson/problem, and a
quiz, so the app has something to click through immediately after startup.

Run from the backend container or a local venv with the same DATABASE_URL:
    python seed.py
"""

import asyncio

from app.auth import hash_password
from app.database import AsyncSessionLocal, Base, engine
from app.models import Course, Lesson, Problem, Quiz, Role, User


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        admin = User(
            name="Admin",
            email="admin@example.com",
            password_hash=hash_password("admin1234"),
            role=Role.admin,
        )
        db.add(admin)

        course = Course(
            title="Python Fundamentals",
            description="Learn the basics of Python programming.",
            difficulty_level="beginner",
        )
        db.add(course)
        await db.flush()

        lesson = Lesson(
            course_id=course.id,
            title="Variables and Print",
            content="Learn how to declare variables and print output in Python.",
            order_index=0,
        )
        db.add(lesson)
        await db.flush()

        problem = Problem(
            lesson_id=lesson.id,
            title="Hello, World!",
            description="Print the exact text: Hello, World!",
            starter_code='print("Hello, World!")\n',
            test_cases=[{"expected_output": "Hello, World!"}],
        )
        db.add(problem)

        quiz = Quiz(
            course_id=course.id,
            title="Python Basics Quiz",
            questions=[
                {
                    "question": "Which keyword defines a function in Python?",
                    "options": ["func", "def", "function", "lambda"],
                    "correct_index": 1,
                }
            ],
            passing_score=60,
        )
        db.add(quiz)

        await db.commit()
        print("Seeded: admin@example.com / admin1234")


if __name__ == "__main__":
    asyncio.run(main())
