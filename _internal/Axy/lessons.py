lessons_index = {
    "variables": (
        "Variables in Python store data.\n\n"
        "Basic syntax:\n"
        "```python\n"
        "name = \"Alex\"\n"
        "age = 25\n"
        "score = 95.5\n"
        "```\n"
        "Rules:\n"
        "• Must start with letter or underscore\n"
        "• Case-sensitive (Age ≠ age)\n"
        "• Use descriptive names\n\n"
        "Try it: create three variables about yourself and print them."
    ),

    "lists": (
        "Lists hold ordered collections of items.\n\n"
        "```python\n"
        "fruits = [\"apple\", \"banana\", \"orange\"]\n"
        "numbers = [1, 5, 9, 23]\n"
        "mixed = [42, \"hello\", True]\n"
        "```\n"
        "Common operations:\n"
        "• Add:    fruits.append(\"grape\")\n"
        "• Access: fruits[0] → \"apple\"\n"
        "• Length: len(fruits)\n"
        "• Slice:  fruits[1:3] → [\"banana\", \"orange\"]\n\n"
        "Exercise: create a list of your three favorite hobbies and print the second one."
    ),

    "loops": (
        "Two main loops in Python:\n\n"
        "1. for-loop (when you know how many times)\n"
        "```python\n"
        "for i in range(5):\n"
        "    print(i)          # 0 1 2 3 4\n"
        "```\n\n"
        "2. while-loop (repeat until condition is false)\n"
        "```python\n"
        "count = 0\n"
        "while count < 3:\n"
        "    print(\"hello\")\n"
        "    count += 1\n"
        "```\n"
        "Tip: always make sure while loops can end, or you get infinite loops."
    ),

    "functions": (
        "Functions let you reuse code.\n\n"
        "Definition:\n"
        "```python\n"
        "def greet(name):\n"
        "    return f\"Hello, {name}!\"\n"
        "\n"
        "result = greet(\"Maria\")\n"
        "print(result)  # Hello, Maria!\n"
        "```\n"
        "Key points:\n"
        "• def keyword\n"
        "• Parameters in parentheses\n"
        "• return sends a value back (optional)\n\n"
        "Try writing a function that takes a number and returns its square."
    ),
}
# ==============================================================================
# Copyright (c) 2026 Axo. All rights reserved.
# 
# This software is proprietary and confidential.
# Unauthorized copying, distribution, modification, or use of this file,
# via any medium, is strictly prohibited without the express written 
# consent of the developer.
# 
# AXY - Local Python Mentor
# ==============================================================================