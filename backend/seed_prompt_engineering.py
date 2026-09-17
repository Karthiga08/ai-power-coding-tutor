"""
Adds two prompt engineering lessons to AI & Machine Learning Fundamentals,
building on "Using LLM APIs Effectively": Prompt Engineering Fundamentals
and Few-Shot Prompting, each with a runnable problem that actually
constructs a prompt string (the same pattern build_prompt() in this
platform's own ai_service.py uses). Idempotent: skips a lesson if it
already exists.

Run:
    .venv/bin/python seed_prompt_engineering.py
"""

import asyncio

from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.models import Course, Lesson, Problem

NEW_LESSONS = [
    {
        "title": "Prompt Engineering Fundamentals",
        "content": (
            "A prompt's clarity and structure directly shape output quality. Effective prompts are "
            "specific about the task, provide only the context the model actually needs, and constrain "
            "the output format when one is expected. Separating a system-level instruction (the model's "
            "overall behavior) from the user-level request (the specific ask) — exactly the SYSTEM_PROMPT "
            "+ build_prompt() split this platform's own AI tutor service uses — keeps prompts easier to "
            "reason about and reuse."
        ),
        "problem": {
            "title": "Build a Zero-Shot Prompt",
            "description": (
                "Write a function build_prompt(task, input_text) that returns the string "
                '"Task: {task}\\nInput: {input_text}\\nOutput:". '
                'Call it with task="Summarize the following text" and '
                'input_text="AI is transforming software." and print the result.'
            ),
            "starter_code": (
                "def build_prompt(task, input_text):\n"
                '    return f"Task: {task}\\nInput: {input_text}\\nOutput:"\n'
                "\n"
                "\n"
                'print(build_prompt("Summarize the following text", "AI is transforming software."))\n'
            ),
            "test_cases": [
                {
                    "expected_output": (
                        "Task: Summarize the following text\n"
                        "Input: AI is transforming software.\n"
                        "Output:"
                    )
                }
            ],
        },
    },
    {
        "title": "Few-Shot Prompting",
        "content": (
            "Zero-shot prompting asks the model to perform a task with no examples. Few-shot prompting "
            "instead shows the model 2-3 example input/output pairs before the real query — often "
            "improving consistency and getting the model to follow an unusual or structured output "
            "format more reliably, at the cost of a longer (and more expensive) prompt."
        ),
        "problem": {
            "title": "Build a Few-Shot Prompt",
            "description": (
                "Given examples = [('2+2', '4'), ('3+5', '8')] and question = '10+7', build a few-shot "
                "prompt: each example formatted as 'Q: {q}\\nA: {a}', joined by newlines, followed by "
                "'Q: {question}\\nA:' on its own line. Print the result."
            ),
            "starter_code": (
                "examples = [('2+2', '4'), ('3+5', '8')]\n"
                "question = '10+7'\n"
                "\n"
                "parts = [f'Q: {q}\\nA: {a}' for q, a in examples]\n"
                "parts.append(f'Q: {question}\\nA:')\n"
                "\n"
                "prompt = '\\n'.join(parts)\n"
                "print(prompt)\n"
            ),
            "test_cases": [
                {"expected_output": "Q: 2+2\nA: 4\nQ: 3+5\nA: 8\nQ: 10+7\nA:"}
            ],
        },
    },
]


async def main():
    async with AsyncSessionLocal() as db:
        course_result = await db.execute(
            select(Course).where(Course.title == "AI & Machine Learning Fundamentals")
        )
        course = course_result.scalar_one_or_none()
        if not course:
            print("AI & Machine Learning Fundamentals course not found.")
            return

        existing_result = await db.execute(select(Lesson).where(Lesson.course_id == course.id))
        existing_titles = {lesson.title for lesson in existing_result.scalars().all()}

        max_order = await db.execute(
            select(func.max(Lesson.order_index)).where(Lesson.course_id == course.id)
        )
        max_value = max_order.scalar()
        next_index = 0 if max_value is None else max_value + 1

        for lesson_data in NEW_LESSONS:
            if lesson_data["title"] in existing_titles:
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
