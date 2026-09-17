"""
Expands each course's quiz (currently 1-2 thin questions from the initial
seed) to cover everything added to that course since: loops/functions/OOP/
error handling for Python, trees/graphs/sorting for Data Structures, etc.

Appends to the existing `questions` list rather than replacing it, and skips
a course's quiz if its question count already looks expanded (>= 6), so
it's safe to re-run.

Run:
    .venv/bin/python seed_more_quiz_questions.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Quiz

NEW_QUESTIONS = {
    "Python Basics Quiz": [
        {
            "question": "What does range(1, 4) produce when iterated?",
            "options": ["1, 2, 3", "1, 2, 3, 4", "0, 1, 2, 3", "2, 3, 4"],
            "correct_index": 0,
        },
        {
            "question": "Which data type is mutable in Python?",
            "options": ["tuple", "string", "list", "int"],
            "correct_index": 2,
        },
        {
            "question": "Which slice expression reverses a string?",
            "options": ["s.reverse()", "s[::-1]", "s.reversed", "reverse(s)"],
            "correct_index": 1,
        },
        {
            "question": "In a Python class, what does __init__ do?",
            "options": [
                "Deletes an object",
                "Initializes a new instance",
                "Defines a class-level constant",
                "Imports a module",
            ],
            "correct_index": 1,
        },
        {
            "question": "Which exception is raised when dividing by zero?",
            "options": ["ValueError", "TypeError", "ZeroDivisionError", "IndexError"],
            "correct_index": 2,
        },
    ],
    "Data Structures Basics Quiz": [
        {
            "question": "Which data structure follows First-In-First-Out (FIFO) order?",
            "options": ["Stack", "Queue", "Tree", "Graph"],
            "correct_index": 1,
        },
        {
            "question": "What is the main advantage of a linked list over an array?",
            "options": [
                "Faster indexing",
                "Efficient insertion/deletion without shifting elements",
                "Uses less memory in every case",
                "Better cache locality",
            ],
            "correct_index": 1,
        },
        {
            "question": "In a binary search tree, what does an in-order traversal produce?",
            "options": ["Reverse order", "Random order", "Sorted order", "Level order"],
            "correct_index": 2,
        },
        {
            "question": "Which traversal strategy does BFS use to explore a graph?",
            "options": ["Depth-first, one branch at a time", "Level by level, using a queue", "Random order", "Always sorted order"],
            "correct_index": 1,
        },
        {
            "question": "What is the worst-case time complexity of Quicksort?",
            "options": ["O(n log n)", "O(n)", "O(n^2)", "O(log n)"],
            "correct_index": 2,
        },
        {
            "question": "What time complexity does Merge Sort guarantee in every case?",
            "options": ["O(n)", "O(n log n)", "O(n^2)", "O(1)"],
            "correct_index": 1,
        },
    ],
    "Java Basics Quiz": [
        {
            "question": "What is the parent class of all classes in Java?",
            "options": ["Main", "Object", "Class", "System"],
            "correct_index": 1,
        },
        {
            "question": "Which block always executes in Java exception handling, whether or not an exception occurred?",
            "options": ["catch", "try", "finally", "throw"],
            "correct_index": 2,
        },
        {
            "question": "Which loop guarantees its body runs at least once?",
            "options": ["for", "while", "do-while", "for-each"],
            "correct_index": 2,
        },
        {
            "question": "Which class is best suited for building up a string in a loop?",
            "options": ["String", "StringBuilder", "ArrayList", "Integer"],
            "correct_index": 1,
        },
    ],
    "Rails Basics Quiz": [
        {
            "question": "Which HTTP verb does a RESTful 'create' action respond to?",
            "options": ["GET", "POST", "PUT", "DELETE"],
            "correct_index": 1,
        },
        {
            "question": "What does form_with primarily help generate in Rails views?",
            "options": [
                "Database migrations",
                "HTML forms tied to a model",
                "Route definitions",
                "Test fixtures",
            ],
            "correct_index": 1,
        },
        {
            "question": "Which Ruby Array method sums its elements?",
            "options": [".total", ".sum", ".add", ".reduce_sum"],
            "correct_index": 1,
        },
        {
            "question": "Which testing framework is most commonly associated with Rails?",
            "options": ["JUnit", "pytest", "RSpec", "Mocha"],
            "correct_index": 2,
        },
    ],
    "AI Fundamentals Quiz": [
        {
            "question": "Which best describes a neural network's 'weights'?",
            "options": [
                "Fixed constants that never change",
                "Learnable parameters adjusted during training",
                "The dataset itself",
                "A type of activation function",
            ],
            "correct_index": 1,
        },
        {
            "question": "Predicting a house's price (a continuous number) is an example of:",
            "options": ["Classification", "Regression", "Clustering", "Reinforcement learning"],
            "correct_index": 1,
        },
        {
            "question": "Why can accuracy alone be misleading on an imbalanced dataset?",
            "options": [
                "It's always 100% accurate",
                "A model that only predicts the majority class can still score high accuracy",
                "Accuracy can't be computed for imbalanced data",
                "It only applies to regression",
            ],
            "correct_index": 1,
        },
        {
            "question": "In an LLM API call, what does 'temperature' generally control?",
            "options": [
                "The physical GPU temperature",
                "Response randomness/creativity",
                "The number of tokens returned",
                "API rate limits",
            ],
            "correct_index": 1,
        },
    ],
}


async def main():
    async with AsyncSessionLocal() as db:
        for quiz_title, new_questions in NEW_QUESTIONS.items():
            result = await db.execute(select(Quiz).where(Quiz.title == quiz_title))
            quiz = result.scalar_one_or_none()
            if not quiz:
                print(f"Skipping (quiz not found): {quiz_title}")
                continue

            if len(quiz.questions) >= 6:
                print(f"Skipping (already expanded, {len(quiz.questions)} questions): {quiz_title}")
                continue

            before = len(quiz.questions)
            quiz.questions = quiz.questions + new_questions
            print(f"{quiz_title}: {before} -> {len(quiz.questions)} questions")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
