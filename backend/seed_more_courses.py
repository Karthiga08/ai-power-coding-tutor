"""
Adds more courses (Data Structures, Ruby on Rails, Java, AI/ML) on top of
whatever is already seeded. Idempotent: skips a course if one with the same
title already exists, so it's safe to re-run.

Run:
    .venv/bin/python seed_more_courses.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Course, Lesson, Problem, Quiz


COURSES = [
    {
        "title": "Data Structures & Algorithms",
        "description": "Core data structures and algorithmic thinking, taught with runnable Python examples.",
        "difficulty_level": "intermediate",
        "lessons": [
            {
                "title": "Arrays and Lists",
                "content": "Python lists as dynamic arrays: indexing, slicing, append/pop, and their time complexity.",
                "problem": {
                    "title": "Reverse a List",
                    "description": "Given the list [1, 2, 3, 4, 5], print its elements reversed, space-separated, on one line.",
                    "starter_code": (
                        "numbers = [1, 2, 3, 4, 5]\n"
                        "reversed_numbers = numbers[::-1]\n"
                        "print(' '.join(str(n) for n in reversed_numbers))\n"
                    ),
                    "test_cases": [{"expected_output": "5 4 3 2 1"}],
                },
            },
            {
                "title": "Stacks and Queues",
                "content": "LIFO vs FIFO. Implementing a stack and a queue using Python lists and collections.deque.",
                "problem": {
                    "title": "Balanced Parentheses",
                    "description": "Using a stack, check whether the string '(()())' has balanced parentheses. Print True or False.",
                    "starter_code": (
                        "def is_balanced(s):\n"
                        "    stack = []\n"
                        "    for ch in s:\n"
                        "        if ch == '(':\n"
                        "            stack.append(ch)\n"
                        "        elif ch == ')':\n"
                        "            if not stack:\n"
                        "                return False\n"
                        "            stack.pop()\n"
                        "    return not stack\n"
                        "\n"
                        "print(is_balanced('(()())'))\n"
                    ),
                    "test_cases": [{"expected_output": "True"}],
                },
            },
            {
                "title": "Linked Lists",
                "content": "Singly linked lists: nodes, traversal, insertion, and deletion, and how they differ from arrays.",
            },
            {
                "title": "Trees and Graphs",
                "content": "Binary trees, tree traversal (in-order, pre-order, post-order), and an introduction to graphs.",
            },
            {
                "title": "Sorting and Searching",
                "content": "Bubble sort, merge sort, and binary search, with time-complexity comparisons.",
                "problem": {
                    "title": "Bubble Sort",
                    "description": "Sort the list [5, 2, 4, 1, 3] in ascending order using bubble sort and print it space-separated.",
                    "starter_code": (
                        "nums = [5, 2, 4, 1, 3]\n"
                        "n = len(nums)\n"
                        "for i in range(n):\n"
                        "    for j in range(n - i - 1):\n"
                        "        if nums[j] > nums[j + 1]:\n"
                        "            nums[j], nums[j + 1] = nums[j + 1], nums[j]\n"
                        "print(' '.join(str(n) for n in nums))\n"
                    ),
                    "test_cases": [{"expected_output": "1 2 3 4 5"}],
                },
            },
        ],
        "quiz": {
            "title": "Data Structures Basics Quiz",
            "questions": [
                {
                    "question": "Which data structure follows Last-In-First-Out (LIFO) order?",
                    "options": ["Queue", "Stack", "Array", "Tree"],
                    "correct_index": 1,
                },
                {
                    "question": "What is the average time complexity of binary search on a sorted array?",
                    "options": ["O(n)", "O(n^2)", "O(log n)", "O(1)"],
                    "correct_index": 2,
                },
            ],
            "passing_score": 60,
        },
    },
    {
        "title": "Java Programming",
        "description": "Java fundamentals: syntax, object-oriented programming, and the standard collections framework.",
        "difficulty_level": "beginner",
        "lessons": [
            {
                "title": "Java Basics and Syntax",
                "content": (
                    "Java is statically typed and compiled to bytecode for the JVM. A minimal program:\n\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        System.out.println(\"Hello, World!\");\n"
                    "    }\n"
                    "}\n\n"
                    "Every file's public class name must match the filename, and execution starts at main()."
                ),
            },
            {
                "title": "Object-Oriented Programming in Java",
                "content": "Classes, objects, constructors, inheritance, interfaces, and encapsulation with access modifiers (private/protected/public).",
            },
            {
                "title": "Collections Framework",
                "content": "ArrayList, HashMap, HashSet, and List/Map/Set interfaces — when to use each and their Big-O characteristics.",
            },
            {
                "title": "Exception Handling",
                "content": "Checked vs unchecked exceptions, try/catch/finally, and try-with-resources.",
            },
        ],
        "quiz": {
            "title": "Java Basics Quiz",
            "questions": [
                {
                    "question": "Which keyword is used to create a subclass in Java?",
                    "options": ["implements", "extends", "inherits", "super"],
                    "correct_index": 1,
                },
                {
                    "question": "Which collection does not allow duplicate elements?",
                    "options": ["ArrayList", "LinkedList", "HashSet", "HashMap"],
                    "correct_index": 2,
                },
            ],
            "passing_score": 60,
        },
    },
    {
        "title": "Ruby on Rails Web Development",
        "description": "Building web applications with Ruby on Rails: MVC, ActiveRecord, routing, and views.",
        "difficulty_level": "intermediate",
        "lessons": [
            {
                "title": "Introduction to Ruby on Rails",
                "content": "Rails is a convention-over-configuration MVC web framework written in Ruby. `rails new app_name` scaffolds a full project.",
            },
            {
                "title": "MVC Architecture",
                "content": "Models (data + business logic), Views (templates), Controllers (request handling) — how a request flows through each.",
            },
            {
                "title": "ActiveRecord and Migrations",
                "content": "ActiveRecord is Rails' ORM. Migrations version your schema: `rails generate migration AddEmailToUsers email:string`.",
            },
            {
                "title": "Routing and Controllers",
                "content": "config/routes.rb maps URLs to controller actions. RESTful routes: index, show, new, create, edit, update, destroy.",
            },
            {
                "title": "Views and Forms",
                "content": "ERB templates, form_with helpers, and strong parameters for safely handling form submissions.",
            },
        ],
        "quiz": {
            "title": "Rails Basics Quiz",
            "questions": [
                {
                    "question": "Which part of MVC is responsible for business logic and data?",
                    "options": ["View", "Controller", "Model", "Router"],
                    "correct_index": 2,
                },
                {
                    "question": "What does ActiveRecord provide?",
                    "options": [
                        "A CSS framework",
                        "An ORM for mapping models to database tables",
                        "A JavaScript bundler",
                        "A testing framework",
                    ],
                    "correct_index": 1,
                },
            ],
            "passing_score": 60,
        },
    },
    {
        "title": "AI & Machine Learning Fundamentals",
        "description": "Core AI/ML concepts and practical, runnable Python examples — the same ideas this platform's own AI tutor is built on.",
        "difficulty_level": "intermediate",
        "lessons": [
            {
                "title": "What is Artificial Intelligence?",
                "content": "AI, machine learning, and deep learning as nested subfields. Supervised vs. unsupervised vs. reinforcement learning.",
            },
            {
                "title": "Working with Data",
                "content": "Features and labels, training/validation/test splits, and why data quality matters more than model choice.",
                "problem": {
                    "title": "Compute the Mean",
                    "description": "Given the list of scores [72, 85, 90, 61, 78], compute and print their average as a float.",
                    "starter_code": (
                        "scores = [72, 85, 90, 61, 78]\n"
                        "average = sum(scores) / len(scores)\n"
                        "print(average)\n"
                    ),
                    "test_cases": [{"expected_output": "77.2"}],
                },
            },
            {
                "title": "Neural Networks, Briefly",
                "content": "Neurons, weights, activation functions, and gradient descent — the intuition, without the calculus.",
            },
            {
                "title": "Using LLM APIs Effectively",
                "content": "Prompt structure, system vs. user messages, temperature, and context — exactly what this platform's AI Tutor feature does under the hood.",
            },
        ],
        "quiz": {
            "title": "AI Fundamentals Quiz",
            "questions": [
                {
                    "question": "Which type of learning uses labeled input/output pairs?",
                    "options": ["Unsupervised learning", "Supervised learning", "Reinforcement learning", "Clustering"],
                    "correct_index": 1,
                },
                {
                    "question": "In an LLM API call, what does the 'system' message typically set?",
                    "options": [
                        "The user's question",
                        "The model's overall behavior/instructions",
                        "The response format only",
                        "Nothing, it's ignored",
                    ],
                    "correct_index": 1,
                },
            ],
            "passing_score": 60,
        },
    },
]


async def main():
    async with AsyncSessionLocal() as db:
        for course_data in COURSES:
            existing = await db.execute(select(Course).where(Course.title == course_data["title"]))
            if existing.scalar_one_or_none():
                print(f"Skipping (already exists): {course_data['title']}")
                continue

            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                difficulty_level=course_data["difficulty_level"],
            )
            db.add(course)
            await db.flush()

            for i, lesson_data in enumerate(course_data["lessons"]):
                lesson = Lesson(
                    course_id=course.id,
                    title=lesson_data["title"],
                    content=lesson_data["content"],
                    order_index=i,
                )
                db.add(lesson)
                await db.flush()

                if "problem" in lesson_data:
                    p = lesson_data["problem"]
                    db.add(
                        Problem(
                            lesson_id=lesson.id,
                            title=p["title"],
                            description=p["description"],
                            starter_code=p["starter_code"],
                            test_cases=p["test_cases"],
                        )
                    )

            if "quiz" in course_data:
                q = course_data["quiz"]
                db.add(
                    Quiz(
                        course_id=course.id,
                        title=q["title"],
                        questions=q["questions"],
                        passing_score=q["passing_score"],
                    )
                )

            print(f"Added: {course_data['title']}")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
