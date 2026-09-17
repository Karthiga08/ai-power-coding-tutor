"""
Adds more lessons (with runnable coding problems where the language fits)
to each of the 5 existing courses. Idempotent: skips a lesson if one with
the same title already exists in that course, so it's safe to re-run.

Run:
    .venv/bin/python seed_extra_lessons.py
"""

import asyncio

from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.models import Course, Lesson, Problem

# course title -> list of new lessons (appended after whatever already exists)
EXTRA_LESSONS = {
    "Python Fundamentals": [
        {
            "title": "Loops and Conditionals",
            "content": "for and while loops, if/elif/else branching, and range() for counting loops.",
            "problem": {
                "title": "Print Squares",
                "description": "Using a for loop over range(1, 6), print each number's square, space-separated, on one line.",
                "starter_code": (
                    "squares = []\n"
                    "for n in range(1, 6):\n"
                    "    squares.append(str(n * n))\n"
                    "print(' '.join(squares))\n"
                ),
                "test_cases": [{"expected_output": "1 4 9 16 25"}],
            },
        },
        {
            "title": "Functions",
            "content": "Defining functions with def, parameters, return values, and default arguments.",
            "problem": {
                "title": "Add Two Numbers",
                "description": "Write a function add(a, b) that returns a + b. Call add(3, 4) and print the result.",
                "starter_code": (
                    "def add(a, b):\n"
                    "    return a + b\n"
                    "\n"
                    "print(add(3, 4))\n"
                ),
                "test_cases": [{"expected_output": "7"}],
            },
        },
        {
            "title": "Lists and Dictionaries",
            "content": "Python's two core collection types: ordered, mutable lists and key-value dictionaries.",
            "problem": {
                "title": "Sum Dictionary Values",
                "description": "Given scores = {'a': 10, 'b': 20, 'c': 30}, print the sum of its values.",
                "starter_code": (
                    "scores = {'a': 10, 'b': 20, 'c': 30}\n"
                    "print(sum(scores.values()))\n"
                ),
                "test_cases": [{"expected_output": "60"}],
            },
        },
        {
            "title": "String Manipulation",
            "content": "Slicing, concatenation, .upper()/.lower(), .split(), and .join() for working with text.",
            "problem": {
                "title": "Reverse a String",
                "description": "Reverse the string 'python' and print the result.",
                "starter_code": "text = 'python'\nprint(text[::-1])\n",
                "test_cases": [{"expected_output": "nohtyp"}],
            },
        },
    ],
    "Data Structures & Algorithms": [
        {
            "title": "Hash Tables",
            "content": "Python dicts as hash tables: O(1) average lookup, and using a set for fast membership checks.",
            "problem": {
                "title": "Two Sum",
                "description": (
                    "Given nums = [2, 7, 11, 15] and target = 9, use a set/dict to check in one pass "
                    "whether any two numbers sum to the target. Print True or False."
                ),
                "starter_code": (
                    "nums = [2, 7, 11, 15]\n"
                    "target = 9\n"
                    "seen = set()\n"
                    "found = False\n"
                    "for n in nums:\n"
                    "    if target - n in seen:\n"
                    "        found = True\n"
                    "        break\n"
                    "    seen.add(n)\n"
                    "print(found)\n"
                ),
                "test_cases": [{"expected_output": "True"}],
            },
        },
        {
            "title": "Recursion",
            "content": "Functions that call themselves: base cases, recursive cases, and the call stack.",
            "problem": {
                "title": "Factorial",
                "description": "Write a recursive function factorial(n) and print factorial(5).",
                "starter_code": (
                    "def factorial(n):\n"
                    "    if n <= 1:\n"
                    "        return 1\n"
                    "    return n * factorial(n - 1)\n"
                    "\n"
                    "print(factorial(5))\n"
                ),
                "test_cases": [{"expected_output": "120"}],
            },
        },
    ],
    "Java Programming": [
        {
            "title": "Loops and Conditionals in Java",
            "content": "for, while, and do-while loops, and if/else if/else branching in Java.",
            "problem": {
                "title": "Sum 1 to 5",
                "description": "Use a for loop to sum the integers 1 through 5 (inclusive) and print the result.",
                "starter_code": (
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        int sum = 0;\n"
                    "        for (int i = 1; i <= 5; i++) {\n"
                    "            sum += i;\n"
                    "        }\n"
                    "        System.out.println(sum);\n"
                    "    }\n"
                    "}\n"
                ),
                "test_cases": [{"expected_output": "15"}],
            },
        },
        {
            "title": "Working with Strings",
            "content": "The String class, immutability, and StringBuilder for efficient concatenation.",
            "problem": {
                "title": "Reverse a String",
                "description": 'Reverse the string "hello" using StringBuilder and print the result.',
                "starter_code": (
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        String s = \"hello\";\n"
                    "        String reversed = new StringBuilder(s).reverse().toString();\n"
                    "        System.out.println(reversed);\n"
                    "    }\n"
                    "}\n"
                ),
                "test_cases": [{"expected_output": "olleh"}],
            },
        },
    ],
    "Ruby on Rails Web Development": [
        {
            "title": "Ruby Collections: Arrays and Hashes",
            "content": "Core Ruby (not Rails-specific) collection methods: .each, .map, .select, and .sum, which Rails code leans on constantly.",
            "problem": {
                "title": "Sum an Array",
                "description": "Given nums = [1, 2, 3, 4, 5], print the sum using Ruby's built-in .sum method.",
                "starter_code": "nums = [1, 2, 3, 4, 5]\nputs nums.sum\n",
                "test_cases": [{"expected_output": "15"}],
            },
        },
        {
            "title": "Testing and Deployment",
            "content": (
                "RSpec is Rails' most common testing framework — model specs, request specs, and factories "
                "(FactoryBot) for test data. For deployment, Rails apps typically ship via Heroku, Render, or "
                "Railway: set RAILS_ENV=production, run `rails db:migrate`, and precompile assets with "
                "`rails assets:precompile`."
            ),
        },
    ],
    "AI & Machine Learning Fundamentals": [
        {
            "title": "Classification vs. Regression",
            "content": "Classification predicts a category (spam/not spam); regression predicts a continuous number (a price, a score).",
            "problem": {
                "title": "A Simple Threshold Classifier",
                "description": "Given score = 72 and a passing threshold of 60, print 'Pass' if score >= threshold, else 'Fail'.",
                "starter_code": (
                    "score = 72\n"
                    "threshold = 60\n"
                    "print('Pass' if score >= threshold else 'Fail')\n"
                ),
                "test_cases": [{"expected_output": "Pass"}],
            },
        },
        {
            "title": "Evaluating Model Performance",
            "content": "Accuracy, precision, recall, and why accuracy alone can be misleading on imbalanced data.",
            "problem": {
                "title": "Compute Accuracy",
                "description": (
                    "Given predictions = [1, 0, 1, 1, 0] and actual = [1, 0, 0, 1, 0], compute and print "
                    "the accuracy (fraction of matching entries) as a float."
                ),
                "starter_code": (
                    "predictions = [1, 0, 1, 1, 0]\n"
                    "actual = [1, 0, 0, 1, 0]\n"
                    "correct = sum(1 for p, a in zip(predictions, actual) if p == a)\n"
                    "print(correct / len(actual))\n"
                ),
                "test_cases": [{"expected_output": "0.8"}],
            },
        },
    ],
}

# Matches each course's coding-problem language to the language its lessons teach.
COURSE_LANGUAGE = {
    "Python Fundamentals": "python",
    "Data Structures & Algorithms": "python",
    "Java Programming": "java",
    "Ruby on Rails Web Development": "ruby",
    "AI & Machine Learning Fundamentals": "python",
}


async def main():
    async with AsyncSessionLocal() as db:
        for course_title, lessons in EXTRA_LESSONS.items():
            course_result = await db.execute(select(Course).where(Course.title == course_title))
            course = course_result.scalar_one_or_none()
            if not course:
                print(f"Skipping (course not found): {course_title}")
                continue

            max_order = await db.execute(
                select(func.max(Lesson.order_index)).where(Lesson.course_id == course.id)
            )
            max_value = max_order.scalar()
            next_index = 0 if max_value is None else max_value + 1
            language = COURSE_LANGUAGE[course_title]

            for lesson_data in lessons:
                existing = await db.execute(
                    select(Lesson).where(
                        Lesson.course_id == course.id, Lesson.title == lesson_data["title"]
                    )
                )
                if existing.scalar_one_or_none():
                    print(f"Skipping (already exists): {course_title} / {lesson_data['title']}")
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

                if "problem" in lesson_data:
                    p = lesson_data["problem"]
                    db.add(
                        Problem(
                            lesson_id=lesson.id,
                            title=p["title"],
                            description=p["description"],
                            language=language,
                            starter_code=p["starter_code"],
                            test_cases=p["test_cases"],
                        )
                    )

                print(f"Added: {course_title} / {lesson_data['title']}")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
