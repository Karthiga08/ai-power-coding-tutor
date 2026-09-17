"""
Fixes an order_index bug from the previous seeding run (Python Fundamentals'
"Loops and Conditionals" ended up at order_index 0, colliding with
"Variables and Print" — an `x or -1` falsy-zero bug), then adds two more
lessons: Object-Oriented Programming and Error Handling.

Run:
    .venv/bin/python seed_python_oop_errors.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Course, Lesson, Problem

CORRECT_ORDER = [
    "Variables and Print",
    "Loops and Conditionals",
    "Functions",
    "Lists and Dictionaries",
    "String Manipulation",
]

NEW_LESSONS = [
    {
        "title": "Object-Oriented Programming",
        "content": (
            "Classes bundle data and behavior together. `__init__` is the constructor, `self` refers to "
            "the instance, and methods are just functions defined inside the class that take `self` as "
            "their first parameter."
        ),
        "problem": {
            "title": "Rectangle Area",
            "description": (
                "Define a class Rectangle with an __init__(self, width, height) and a method "
                "area(self) that returns width * height. Create Rectangle(4, 5) and print its area."
            ),
            "starter_code": (
                "class Rectangle:\n"
                "    def __init__(self, width, height):\n"
                "        self.width = width\n"
                "        self.height = height\n"
                "\n"
                "    def area(self):\n"
                "        return self.width * self.height\n"
                "\n"
                "r = Rectangle(4, 5)\n"
                "print(r.area())\n"
            ),
            "test_cases": [{"expected_output": "20"}],
        },
    },
    {
        "title": "Error Handling",
        "content": (
            "try/except catches exceptions so one bad input doesn't crash the whole program. except "
            "can target a specific exception type (like ZeroDivisionError or ValueError), and "
            "finally always runs, whether or not an exception occurred."
        ),
        "problem": {
            "title": "Safe Division",
            "description": (
                "Write a function safe_divide(a, b) that returns a / b, but catches ZeroDivisionError "
                "and returns the string 'Cannot divide by zero' instead. Call safe_divide(10, 0) and "
                "print the result."
            ),
            "starter_code": (
                "def safe_divide(a, b):\n"
                "    try:\n"
                "        return a / b\n"
                "    except ZeroDivisionError:\n"
                "        return 'Cannot divide by zero'\n"
                "\n"
                "print(safe_divide(10, 0))\n"
            ),
            "test_cases": [{"expected_output": "Cannot divide by zero"}],
        },
    },
]


async def main():
    async with AsyncSessionLocal() as db:
        course_result = await db.execute(select(Course).where(Course.title == "Python Fundamentals"))
        course = course_result.scalar_one_or_none()
        if not course:
            print("Python Fundamentals course not found.")
            return

        lessons_result = await db.execute(select(Lesson).where(Lesson.course_id == course.id))
        lessons_by_title = {lesson.title: lesson for lesson in lessons_result.scalars().all()}

        print("Fixing order_index collisions...")
        for i, title in enumerate(CORRECT_ORDER):
            lesson = lessons_by_title.get(title)
            if lesson and lesson.order_index != i:
                print(f"  {title}: {lesson.order_index} -> {i}")
                lesson.order_index = i

        next_index = len(CORRECT_ORDER)
        for lesson_data in NEW_LESSONS:
            if lesson_data["title"] in lessons_by_title:
                print(f"Skipping (already exists): {lesson_data['title']}")
                continue

            lesson = Lesson(
                course_id=course.id,
                title=lesson_data["title"],
                content=lesson_data["content"],
                order_index=next_index,
            )
            db.add(lesson)
            await db.flush()
            next_index += 1

            p = lesson_data["problem"]
            db.add(
                Problem(
                    lesson_id=lesson.id,
                    title=p["title"],
                    description=p["description"],
                    language="python",
                    starter_code=p["starter_code"],
                    test_cases=p["test_cases"],
                )
            )
            print(f"Added: {lesson_data['title']}")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
