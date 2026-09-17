"""
Adds two more sorting-algorithm lessons to Data Structures & Algorithms,
alongside the existing "Sorting and Searching" (bubble sort) lesson:
Quicksort and Merge Sort, each with a real runnable Python problem.
Idempotent: skips a lesson if it already exists.

Run:
    .venv/bin/python seed_quicksort_mergesort.py
"""

import asyncio

from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.models import Course, Lesson, Problem

NEW_LESSONS = [
    {
        "title": "Quicksort",
        "content": (
            "Quicksort is a divide-and-conquer algorithm: pick a pivot, partition the array into "
            "elements less than and greater than the pivot, then recursively sort each partition. "
            "Average case is O(n log n), but a poorly chosen pivot (e.g. always the first element on "
            "an already-sorted array) degrades to O(n^2) worst case."
        ),
        "problem": {
            "title": "Implement Quicksort",
            "description": (
                "Implement quicksort(arr) using the pivot/partition approach (pick the middle element "
                "as pivot). Sort [5, 2, 4, 1, 3] and print the result, space-separated."
            ),
            "starter_code": (
                "def quicksort(arr):\n"
                "    if len(arr) <= 1:\n"
                "        return arr\n"
                "    pivot = arr[len(arr) // 2]\n"
                "    less = [x for x in arr if x < pivot]\n"
                "    equal = [x for x in arr if x == pivot]\n"
                "    greater = [x for x in arr if x > pivot]\n"
                "    return quicksort(less) + equal + quicksort(greater)\n"
                "\n"
                "\n"
                "nums = [5, 2, 4, 1, 3]\n"
                "print(' '.join(str(n) for n in quicksort(nums)))\n"
            ),
            "test_cases": [{"expected_output": "1 2 3 4 5"}],
        },
    },
    {
        "title": "Merge Sort",
        "content": (
            "Merge sort also divides and conquers, but splits the array in half rather than around a "
            "pivot: recursively sort each half, then merge the two sorted halves in linear time. This "
            "gives a guaranteed O(n log n) in every case, unlike quicksort's worst-case O(n^2), at the "
            "cost of needing extra space for the merged output."
        ),
        "problem": {
            "title": "Implement Merge Sort",
            "description": (
                "Implement merge_sort(arr), splitting the array in half and merging two sorted halves "
                "with a merge(left, right) helper. Sort [5, 2, 4, 1, 3] and print the result, "
                "space-separated."
            ),
            "starter_code": (
                "def merge(left, right):\n"
                "    result = []\n"
                "    i = j = 0\n"
                "    while i < len(left) and j < len(right):\n"
                "        if left[i] <= right[j]:\n"
                "            result.append(left[i])\n"
                "            i += 1\n"
                "        else:\n"
                "            result.append(right[j])\n"
                "            j += 1\n"
                "    result.extend(left[i:])\n"
                "    result.extend(right[j:])\n"
                "    return result\n"
                "\n"
                "\n"
                "def merge_sort(arr):\n"
                "    if len(arr) <= 1:\n"
                "        return arr\n"
                "    mid = len(arr) // 2\n"
                "    left = merge_sort(arr[:mid])\n"
                "    right = merge_sort(arr[mid:])\n"
                "    return merge(left, right)\n"
                "\n"
                "\n"
                "nums = [5, 2, 4, 1, 3]\n"
                "print(' '.join(str(n) for n in merge_sort(nums)))\n"
            ),
            "test_cases": [{"expected_output": "1 2 3 4 5"}],
        },
    },
]


async def main():
    async with AsyncSessionLocal() as db:
        course_result = await db.execute(
            select(Course).where(Course.title == "Data Structures & Algorithms")
        )
        course = course_result.scalar_one_or_none()
        if not course:
            print("Data Structures & Algorithms course not found.")
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
