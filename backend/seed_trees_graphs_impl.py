"""
Adds two implementation-focused lessons to Data Structures & Algorithms,
building on the existing conceptual "Trees and Graphs" lesson: an actual
binary search tree (Node class, insert, in-order traversal) and an actual
graph (adjacency list, BFS). Idempotent: skips a lesson if it already exists.

Run:
    .venv/bin/python seed_trees_graphs_impl.py
"""

import asyncio

from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.models import Course, Lesson, Problem

NEW_LESSONS = [
    {
        "title": "Binary Tree Implementation",
        "content": (
            "A binary search tree (BST) node holds a value plus left/right child pointers. Inserting "
            "recursively walks left or right depending on whether the new value is smaller or larger "
            "than the current node, until it finds an empty spot. An in-order traversal (left, node, "
            "right) visits a BST's values in sorted order — a useful property that's easy to take for "
            "granted until you've implemented it yourself."
        ),
        "problem": {
            "title": "BST In-Order Traversal",
            "description": (
                "Implement a Node class and an insert(root, value) function to build a binary search "
                "tree from [5, 3, 8, 1, 4], then implement inorder(root, result) to collect an in-order "
                "traversal. Print the traversal, space-separated (it should come out sorted)."
            ),
            "starter_code": (
                "class Node:\n"
                "    def __init__(self, value):\n"
                "        self.value = value\n"
                "        self.left = None\n"
                "        self.right = None\n"
                "\n"
                "\n"
                "def insert(root, value):\n"
                "    if root is None:\n"
                "        return Node(value)\n"
                "    if value < root.value:\n"
                "        root.left = insert(root.left, value)\n"
                "    else:\n"
                "        root.right = insert(root.right, value)\n"
                "    return root\n"
                "\n"
                "\n"
                "def inorder(root, result):\n"
                "    if root:\n"
                "        inorder(root.left, result)\n"
                "        result.append(root.value)\n"
                "        inorder(root.right, result)\n"
                "\n"
                "\n"
                "root = None\n"
                "for v in [5, 3, 8, 1, 4]:\n"
                "    root = insert(root, v)\n"
                "\n"
                "result = []\n"
                "inorder(root, result)\n"
                "print(' '.join(str(v) for v in result))\n"
            ),
            "test_cases": [{"expected_output": "1 3 4 5 8"}],
        },
    },
    {
        "title": "Graph Implementation",
        "content": (
            "A graph can be represented as an adjacency list: a dict mapping each node to a list of its "
            "neighbors. Breadth-first search (BFS) explores level by level using a queue (collections.deque) "
            "and a 'seen' set to avoid revisiting nodes — the same shape of algorithm as finding the "
            "shortest path in an unweighted graph."
        ),
        "problem": {
            "title": "Graph BFS Traversal",
            "description": (
                "Given graph = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []}, implement a BFS "
                "starting from 'A' using collections.deque, and print the order nodes are visited in, "
                "space-separated."
            ),
            "starter_code": (
                "from collections import deque\n"
                "\n"
                "graph = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []}\n"
                "\n"
                "\n"
                "def bfs(graph, start):\n"
                "    visited = [start]\n"
                "    seen = {start}\n"
                "    queue = deque([start])\n"
                "    while queue:\n"
                "        node = queue.popleft()\n"
                "        for neighbor in graph[node]:\n"
                "            if neighbor not in seen:\n"
                "                seen.add(neighbor)\n"
                "                visited.append(neighbor)\n"
                "                queue.append(neighbor)\n"
                "    return visited\n"
                "\n"
                "\n"
                "order = bfs(graph, 'A')\n"
                "print(' '.join(order))\n"
            ),
            "test_cases": [{"expected_output": "A B C D"}],
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

        existing_titles_result = await db.execute(select(Lesson).where(Lesson.course_id == course.id))
        existing_titles = {lesson.title for lesson in existing_titles_result.scalars().all()}

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
