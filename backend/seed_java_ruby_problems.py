"""
Adds real, auto-graded Java and Ruby coding problems to the lessons created
by seed_more_courses.py, now that the Java and Ruby sandbox runner images
exist. Idempotent: skips a lesson if it already has a problem attached.

Run:
    .venv/bin/python seed_java_ruby_problems.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Lesson, Problem

# lesson title -> problem definition
JAVA_PROBLEMS = {
    "Java Basics and Syntax": {
        "title": "Hello, Java!",
        "description": "Print the exact text: Hello, Java! using System.out.println.",
        "starter_code": (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"Hello, Java!\");\n"
            "    }\n"
            "}\n"
        ),
        "test_cases": [{"expected_output": "Hello, Java!"}],
    },
    "Object-Oriented Programming in Java": {
        "title": "A Simple Class",
        "description": (
            "Define a class Dog with a String field name and a method bark() that "
            "prints \"<name> says Woof!\". In main, create a Dog named \"Rex\" and call bark()."
        ),
        "starter_code": (
            "public class Main {\n"
            "    static class Dog {\n"
            "        String name;\n"
            "        Dog(String name) { this.name = name; }\n"
            "        void bark() { System.out.println(name + \" says Woof!\"); }\n"
            "    }\n"
            "\n"
            "    public static void main(String[] args) {\n"
            "        Dog d = new Dog(\"Rex\");\n"
            "        d.bark();\n"
            "    }\n"
            "}\n"
        ),
        "test_cases": [{"expected_output": "Rex says Woof!"}],
    },
}

RUBY_PROBLEMS = {
    "Introduction to Ruby on Rails": {
        "title": "Hello, Ruby!",
        "description": "Print the exact text: Hello, Ruby! using puts.",
        "starter_code": 'puts "Hello, Ruby!"\n',
        "test_cases": [{"expected_output": "Hello, Ruby!"}],
    },
    "Views and Forms": {
        "title": "String Interpolation",
        "description": 'Set name = "Rails" and print "Hello, #{name}!" using Ruby string interpolation.',
        "starter_code": 'name = "Rails"\nputs "Hello, #{name}!"\n',
        "test_cases": [{"expected_output": "Hello, Rails!"}],
    },
}


async def _add_problems(db, mapping: dict, language: str):
    for lesson_title, problem_data in mapping.items():
        lesson_result = await db.execute(select(Lesson).where(Lesson.title == lesson_title))
        lesson = lesson_result.scalar_one_or_none()
        if not lesson:
            print(f"Skipping (lesson not found): {lesson_title}")
            continue

        existing = await db.execute(select(Problem).where(Problem.lesson_id == lesson.id))
        if existing.scalar_one_or_none():
            print(f"Skipping (already has a problem): {lesson_title}")
            continue

        db.add(
            Problem(
                lesson_id=lesson.id,
                title=problem_data["title"],
                description=problem_data["description"],
                language=language,
                starter_code=problem_data["starter_code"],
                test_cases=problem_data["test_cases"],
            )
        )
        print(f"Added {language} problem to: {lesson_title}")


async def main():
    async with AsyncSessionLocal() as db:
        await _add_problems(db, JAVA_PROBLEMS, "java")
        await _add_problems(db, RUBY_PROBLEMS, "ruby")
        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
