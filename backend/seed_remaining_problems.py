"""
Adds a coding problem to every lesson that's still missing one, across all
5 courses. Idempotent: skips a lesson that already has a problem.

Run:
    .venv/bin/python seed_remaining_problems.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Lesson, Problem

# lesson title -> (language, problem definition)
NEW_PROBLEMS = {
    # --- Data Structures & Algorithms ---
    "Linked Lists": (
        "python",
        {
            "title": "Build and Traverse a Linked List",
            "description": (
                "Implement a Node class and build a singly linked list from [1, 2, 3] by appending "
                "each value. Traverse it from the head and print the values, space-separated."
            ),
            "starter_code": (
                "class Node:\n"
                "    def __init__(self, value):\n"
                "        self.value = value\n"
                "        self.next = None\n"
                "\n"
                "\n"
                "def build_linked_list(values):\n"
                "    head = None\n"
                "    tail = None\n"
                "    for v in values:\n"
                "        node = Node(v)\n"
                "        if head is None:\n"
                "            head = tail = node\n"
                "        else:\n"
                "            tail.next = node\n"
                "            tail = node\n"
                "    return head\n"
                "\n"
                "\n"
                "def traverse(head):\n"
                "    result = []\n"
                "    node = head\n"
                "    while node:\n"
                "        result.append(str(node.value))\n"
                "        node = node.next\n"
                "    return result\n"
                "\n"
                "\n"
                "head = build_linked_list([1, 2, 3])\n"
                "print(' '.join(traverse(head)))\n"
            ),
            "test_cases": [{"expected_output": "1 2 3"}],
        },
    ),
    "Trees and Graphs": (
        "python",
        {
            "title": "Count Tree Nodes",
            "description": (
                "Given a tree represented as nested dicts ({'value': ..., 'children': [...]}), write a "
                "recursive count_nodes(node) function and print the total node count for the given "
                "4-node tree."
            ),
            "starter_code": (
                "tree = {\n"
                "    'value': 1,\n"
                "    'children': [\n"
                "        {'value': 2, 'children': []},\n"
                "        {'value': 3, 'children': [\n"
                "            {'value': 4, 'children': []}\n"
                "        ]}\n"
                "    ]\n"
                "}\n"
                "\n"
                "\n"
                "def count_nodes(node):\n"
                "    if node is None:\n"
                "        return 0\n"
                "    return 1 + sum(count_nodes(child) for child in node['children'])\n"
                "\n"
                "\n"
                "print(count_nodes(tree))\n"
            ),
            "test_cases": [{"expected_output": "4"}],
        },
    ),
    # --- Java Programming ---
    "Collections Framework": (
        "java",
        {
            "title": "Sort an ArrayList",
            "description": "Add 3, 1, 2 to an ArrayList<Integer>, sort it with Collections.sort, and print the result space-separated.",
            "starter_code": (
                "import java.util.ArrayList;\n"
                "import java.util.Collections;\n"
                "\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        ArrayList<Integer> nums = new ArrayList<>();\n"
                "        nums.add(3);\n"
                "        nums.add(1);\n"
                "        nums.add(2);\n"
                "        Collections.sort(nums);\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int i = 0; i < nums.size(); i++) {\n"
                "            if (i > 0) sb.append(\" \");\n"
                "            sb.append(nums.get(i));\n"
                "        }\n"
                "        System.out.println(sb.toString());\n"
                "    }\n"
                "}\n"
            ),
            "test_cases": [{"expected_output": "1 2 3"}],
        },
    ),
    "Exception Handling": (
        "java",
        {
            "title": "Safe Division in Java",
            "description": (
                "Write a safeDivide(a, b) method that returns a / b as a String, but catches "
                "ArithmeticException and returns 'Cannot divide by zero' instead. Call safeDivide(10, 0)."
            ),
            "starter_code": (
                "public class Main {\n"
                "    static String safeDivide(int a, int b) {\n"
                "        try {\n"
                "            return String.valueOf(a / b);\n"
                "        } catch (ArithmeticException e) {\n"
                "            return \"Cannot divide by zero\";\n"
                "        }\n"
                "    }\n"
                "\n"
                "    public static void main(String[] args) {\n"
                "        System.out.println(safeDivide(10, 0));\n"
                "    }\n"
                "}\n"
            ),
            "test_cases": [{"expected_output": "Cannot divide by zero"}],
        },
    ),
    # --- Ruby on Rails Web Development ---
    # Rails itself isn't runnable in the sandbox (no server, no DB) — these
    # problems model the underlying idea in plain, runnable Ruby instead.
    "MVC Architecture": (
        "ruby",
        {
            "title": "A Minimal Model with Validation",
            "description": (
                "Define a User class with a name attribute and a valid? method that returns true if "
                "name is present and non-blank (the kind of check an ActiveRecord model does). Create "
                "User.new(\"Ada\") and print whether it's valid."
            ),
            "starter_code": (
                "class User\n"
                "  attr_accessor :name\n"
                "\n"
                "  def initialize(name)\n"
                "    @name = name\n"
                "  end\n"
                "\n"
                "  def valid?\n"
                "    !@name.nil? && !@name.strip.empty?\n"
                "  end\n"
                "end\n"
                "\n"
                "user = User.new(\"Ada\")\n"
                "puts user.valid?\n"
            ),
            "test_cases": [{"expected_output": "true"}],
        },
    ),
    "ActiveRecord and Migrations": (
        "ruby",
        {
            "title": "Query an In-Memory Table",
            "description": (
                "Given users = an array of hashes with :id and :name, use Array#find (the plain-Ruby "
                "equivalent of ActiveRecord's find_by) to find the user named 'Grace' and print their id."
            ),
            "starter_code": (
                "users = [{ id: 1, name: 'Ada' }, { id: 2, name: 'Grace' }]\n"
                "found = users.find { |u| u[:name] == 'Grace' }\n"
                "puts found[:id]\n"
            ),
            "test_cases": [{"expected_output": "2"}],
        },
    ),
    "Routing and Controllers": (
        "ruby",
        {
            "title": "Match a Route",
            "description": (
                "Given routes, a hash mapping paths to 'Controller#action' strings, print the value "
                "for the '/posts' key."
            ),
            "starter_code": (
                "routes = {\n"
                "  '/posts' => 'PostsController#index',\n"
                "  '/users' => 'UsersController#index'\n"
                "}\n"
                "\n"
                "puts routes['/posts']\n"
            ),
            "test_cases": [{"expected_output": "PostsController#index"}],
        },
    ),
    "Testing and Deployment": (
        "ruby",
        {
            "title": "A Minimal Assertion",
            "description": (
                "RSpec's expect(actual).to eq(expected) is, underneath, just an equality check. Write "
                "expect_equal(actual, expected) returning 'PASS' or 'FAIL', and call it with 2 + 2 and 4."
            ),
            "starter_code": (
                "def expect_equal(actual, expected)\n"
                "  actual == expected ? 'PASS' : 'FAIL'\n"
                "end\n"
                "\n"
                "puts expect_equal(2 + 2, 4)\n"
            ),
            "test_cases": [{"expected_output": "PASS"}],
        },
    ),
    # --- AI & Machine Learning Fundamentals ---
    "What is Artificial Intelligence?": (
        "python",
        {
            "title": "A Rule-Based 'AI'",
            "description": (
                "Before machine learning, many 'AI' systems were just rules. Write "
                "simple_ai_response(message) that returns 'Hi there!' if 'hello' appears in the "
                "(lowercased) message, else 'I do not understand.'. Call it with 'Hello, AI!'."
            ),
            "starter_code": (
                "def simple_ai_response(message):\n"
                "    if 'hello' in message.lower():\n"
                "        return 'Hi there!'\n"
                "    return 'I do not understand.'\n"
                "\n"
                "\n"
                "print(simple_ai_response('Hello, AI!'))\n"
            ),
            "test_cases": [{"expected_output": "Hi there!"}],
        },
    ),
    "Neural Networks, Briefly": (
        "python",
        {
            "title": "A Single Neuron",
            "description": (
                "Implement neuron(inputs, weights, bias): compute the weighted sum plus bias, then "
                "apply a step activation (1 if the total is > 0, else 0). Call it with "
                "inputs=[1, 0, 1], weights=[0.5, -0.5, 0.5], bias=-0.2."
            ),
            "starter_code": (
                "def neuron(inputs, weights, bias):\n"
                "    total = sum(i * w for i, w in zip(inputs, weights)) + bias\n"
                "    return 1 if total > 0 else 0\n"
                "\n"
                "\n"
                "inputs = [1, 0, 1]\n"
                "weights = [0.5, -0.5, 0.5]\n"
                "bias = -0.2\n"
                "print(neuron(inputs, weights, bias))\n"
            ),
            "test_cases": [{"expected_output": "1"}],
        },
    ),
    "Using LLM APIs Effectively": (
        "python",
        {
            "title": "Count Prompt Words",
            "description": (
                "Staying within an LLM's context window means being aware of prompt length. Write "
                "word_count(text) and print the word count of "
                "'Explain how neural networks work in simple terms'."
            ),
            "starter_code": (
                "def word_count(text):\n"
                "    return len(text.split())\n"
                "\n"
                "\n"
                "prompt = 'Explain how neural networks work in simple terms'\n"
                "print(word_count(prompt))\n"
            ),
            "test_cases": [{"expected_output": "8"}],
        },
    ),
}


async def main():
    async with AsyncSessionLocal() as db:
        for lesson_title, (language, p) in NEW_PROBLEMS.items():
            result = await db.execute(select(Lesson).where(Lesson.title == lesson_title))
            lesson = result.scalar_one_or_none()
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
                    title=p["title"],
                    description=p["description"],
                    language=language,
                    starter_code=p["starter_code"],
                    test_cases=p["test_cases"],
                )
            )
            print(f"Added ({language}): {lesson_title}")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
