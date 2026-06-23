#!/usr/bin/env python3
"""
Script to load initial tasks into the database.

Run this after migrations to populate tasks.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database configuration
from shared.config import Settings
from infrastructure.db.models.task import Task
from shared.enums import TaskType, Difficulty


# Initial tasks data - extracted from legacy task_catalog.py
INITIAL_TASKS = [
    {
        "id": 1,
        "title": "Sum of Numbers",
        "description": "Напишите функцию, которая принимает N чисел и выводит их сумму.",
        "difficulty": Difficulty.EASY,
        "task_type": TaskType.ALGORITHM,
        "constructions": ["for_loop", "binary_expression"],
        "test_cases": [
            {"inputs": "3\n1 2 3", "output": "6"},
            {"inputs": "2\n10 20", "output": "30"},
            {"inputs": "4\n-1 0 1 2", "output": "2"},
        ],
        "code_examples": {
            "cpp": (
                "#include <iostream>\n"
                "using namespace std;\n"
                "int main() {\n"
                "    int n; cin >> n;\n"
                "    int sum = 0, x;\n"
                "    for (int i = 0; i < n; i++) { cin >> x; sum += x; }\n"
                "    cout << sum << endl;\n"
                "    return 0;\n"
                "}"
            ),
            "python": (
                "n = int(input())\n"
                "nums = list(map(int, input().split()))\n"
                "total = 0\n"
                "for num in nums:\n"
                "    total += num\n"
                "print(total)"
            ),
        },
    },
    {
        "id": 2,
        "title": "Max in Array",
        "description": "Переведите код с C++ на Python. Найдите максимум из N чисел.",
        "difficulty": Difficulty.EASY,
        "task_type": TaskType.TRANSLATION,
        "test_cases": [
            {"inputs": "3\n1 5 3", "output": "5"},
            {"inputs": "4\n-1 -5 -3 -2", "output": "-1"},
            {"inputs": "1\n42", "output": "42"},
        ],
        "code_examples": {
            "cpp": (
                "#include <iostream>\n"
                "using namespace std;\n"
                "int main() {\n"
                "    int n; cin >> n;\n"
                "    int mx, x; cin >> mx;\n"
                "    for (int i = 1; i < n; i++) {\n"
                "        cin >> x;\n"
                "        if (x > mx) mx = x;\n"
                "    }\n"
                "    cout << mx << endl;\n"
                "    return 0;\n"
                "}"
            ),
            "python": (
                "n = int(input())\n"
                "nums = list(map(int, input().split()))\n"
                "print(max(nums))"
            ),
        },
    },
    {
        "id": 3,
        "title": "Fibonacci",
        "description": "Вычислите N-е число Фибоначчи (0-индексация).",
        "difficulty": Difficulty.MEDIUM,
        "task_type": TaskType.ALGORITHM,
        "test_cases": [
            {"inputs": "0", "output": "0"},
            {"inputs": "1", "output": "1"},
            {"inputs": "7", "output": "13"},
            {"inputs": "10", "output": "55"},
        ],
        "code_examples": {
            "cpp": (
                "#include <iostream>\n"
                "using namespace std;\n"
                "int fib(int n) {\n"
                "    if (n <= 1) return n;\n"
                "    return fib(n-1) + fib(n-2);\n"
                "}\n"
                "int main() {\n"
                "    int n; cin >> n;\n"
                "    cout << fib(n) << endl;\n"
                "    return 0;\n"
                "}"
            ),
            "python": (
                "def fib(n):\n"
                "    if n <= 1:\n"
                "        return n\n"
                "    return fib(n-1) + fib(n-2)\n\n"
                "n = int(input())\n"
                "print(fib(n))"
            ),
        },
    },
    {
        "id": 4,
        "title": "Код по блок-схеме: чётное / нечётное",
        "description": "По блок-схеме напишите программу: ввод N, вывод Even или Odd.",
        "difficulty": Difficulty.EASY,
        "task_type": TaskType.DIAGRAM,
        "test_cases": [
            {"inputs": "4", "output": "Even"},
            {"inputs": "3", "output": "Odd"},
            {"inputs": "0", "output": "Even"},
        ],
        "code_examples": {
            "python": (
                "n = int(input())\n"
                "if n % 2 == 0:\n"
                "    print('Even')\n"
                "else:\n"
                "    print('Odd')"
            ),
            "cpp": (
                "#include <iostream>\n"
                "using namespace std;\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    if (n % 2 == 0)\n"
                "        cout << \"Even\" << endl;\n"
                "    else\n"
                "        cout << \"Odd\" << endl;\n"
                "    return 0;\n"
                "}"
            ),
        },
        "flow_spec": {
            "student_reference_languages": ["cpp"],
            "allowed_blocks": [
                "start",
                "input",
                "decision",
                "process",
                "loop",
                "output",
                "end",
            ],
            "required_sequence": [
                "start",
                "input",
                "decision",
                "output",
                "output",
                "end",
            ],
            "required_text_checks": [
                {"type": "input", "contains_any": ["n"]},
                {
                    "type": "decision",
                    "contains_any": ["mod 2 == 0", "% 2 == 0", "n % 2 == 0"],
                },
                {"type": "output", "contains_any": ["even"]},
                {"type": "output", "contains_any": ["odd"]},
            ],
        },
    },
    {
        "id": 5,
        "title": "Код по блок-схеме: таблица умножения",
        "description": "По блок-схеме напишите программу: ввод N, таблица N×i для i от 1 до 10.",
        "difficulty": Difficulty.EASY,
        "task_type": TaskType.DIAGRAM,
        "test_cases": [
            {
                "inputs": "2",
                "output": (
                    "2 * 1 = 2\n2 * 2 = 4\n2 * 3 = 6\n2 * 4 = 8\n2 * 5 = 10\n"
                    "2 * 6 = 12\n2 * 7 = 14\n2 * 8 = 16\n2 * 9 = 18\n2 * 10 = 20"
                ),
            },
        ],
        "code_examples": {
            "python": (
                "n = int(input())\n"
                "for i in range(1, 11):\n"
                "    print(f'{n} * {i} = {n * i}')"
            )
        },
        "flow_spec": {
            "allowed_blocks": [
                "start",
                "input",
                "decision",
                "process",
                "loop",
                "output",
                "end",
            ],
            "required_sequence": [
                "start",
                "input",
                "process",
                "decision",
                "output",
                "process",
                "end",
            ],
            "required_text_checks": [
                {"type": "input", "contains_any": ["n"]},
                {"type": "process", "contains_any": ["i = 1", "i=1"]},
                {"type": "decision", "contains_any": ["i <= 10", "i≤10", "i < 11"]},
                {"type": "output", "contains_any": ["print", "n * i", "n*i"]},
                {"type": "process", "contains_any": ["i = i + 1", "i=i+1", "i++"]},
            ],
        },
    },
    {
        "id": 6,
        "title": "Код по блок-схеме: палиндром",
        "description": "По блок-схеме напишите программу: проверка палиндрома без учёта регистра.",
        "difficulty": Difficulty.MEDIUM,
        "task_type": TaskType.DIAGRAM,
        "test_cases": [
            {"inputs": "Level", "output": "Palindrome"},
            {"inputs": "hello", "output": "Not palindrome"},
        ],
        "code_examples": {
            "python": (
                "s = input().strip()\n"
                "normalized = s.lower()\n"
                "if normalized == normalized[::-1]:\n"
                "    print('Palindrome')\n"
                "else:\n"
                "    print('Not palindrome')"
            )
        },
        "flow_spec": {
            "allowed_blocks": [
                "start",
                "input",
                "decision",
                "process",
                "loop",
                "output",
                "end",
            ],
            "required_sequence": [
                "start",
                "input",
                "process",
                "process",
                "decision",
                "decision",
                "process",
                "process",
                "decision",
                "output",
                "output",
                "end",
            ],
            "required_text_checks": [
                {"type": "input", "contains_any": ["s", "string", "строк"]},
                {"type": "process", "contains_any": ["tolower", "lower", "ниж"]},
                {
                    "type": "process",
                    "contains_any": ["left = 0", "right = len", "right=len"],
                },
                {"type": "decision", "contains_any": ["left < right", "left<right"]},
                {
                    "type": "decision",
                    "contains_any": ["s[left] == s[right]", "s[left]==s[right]"],
                },
                {
                    "type": "process",
                    "contains_any": [
                        "ispalindrome = false",
                        "ispalindrome=false",
                        "false",
                    ],
                },
                {
                    "type": "process",
                    "contains_any": ["left++", "right--", "left = left + 1"],
                },
                {"type": "decision", "contains_any": ["ispalindrome"]},
                {"type": "output", "contains_any": ["palindrome"]},
                {"type": "output", "contains_any": ["not palindrome", "not"]},
            ],
        },
    },
    {
        "id": 7,
        "title": "Код по блок-схеме: пузырьковая сортировка",
        "description": "По блок-схеме напишите программу: сортировка массива, вывод после каждого прохода.",
        "difficulty": Difficulty.HARD,
        "task_type": TaskType.DIAGRAM,
        "test_cases": [
            {"inputs": "3\n3 2 1", "output": "2 1 3\n1 2 3"},
            {"inputs": "2\n2 1", "output": "1 2"},
        ],
        "code_examples": {
            "python": (
                "n = int(input())\n"
                "arr = list(map(int, input().split()))\n"
                "for i in range(n - 1):\n"
                "    for j in range(0, n - 1 - i):\n"
                "        if arr[j] > arr[j + 1]:\n"
                "            arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
                "    print(*arr)"
            )
        },
        "flow_spec": {
            "allowed_blocks": [
                "start",
                "input",
                "decision",
                "process",
                "loop",
                "output",
                "end",
            ],
            "required_sequence": [
                "start",
                "input",
                "input",
                "process",
                "decision",
                "process",
                "decision",
                "decision",
                "process",
                "process",
                "output",
                "process",
                "end",
            ],
            "required_text_checks": [
                {"type": "input", "contains_any": ["n"]},
                {"type": "input", "contains_any": ["array", "arr", "a[]"]},
                {"type": "process", "contains_any": ["i = 0", "i=0"]},
                {"type": "decision", "contains_any": ["i < n - 1", "i<n-1", "i < n-1"]},
                {"type": "process", "contains_any": ["j = 0", "j=0"]},
                {
                    "type": "decision",
                    "contains_any": ["j < n - i - 1", "j<n-i-1", "j < n-i-1"],
                },
                {
                    "type": "decision",
                    "contains_any": ["a[j] > a[j+1]", "arr[j] > arr[j+1]", ">"],
                },
                {"type": "process", "contains_any": ["swap", "arr[j], arr[j+1]"]},
                {"type": "process", "contains_any": ["j++", "j = j + 1", "j=j+1"]},
                {"type": "output", "contains_any": ["print array", "print", "array"]},
                {"type": "process", "contains_any": ["i++", "i = i + 1", "i=i+1"]},
            ],
        },
    },
    {
        "id": 8,
        "title": "Perfect Grade Students",
        "description": 'В университете проводятся курсы программирования. Преподаватель хочет узнать, сколько студентов сдали все контрольные работы на "отлично". Для этого ему дан список студентов с количеством сданных контрольных работ и их оценками.',
        "difficulty": Difficulty.MEDIUM,
        "task_type": TaskType.ALGORITHM,
        "test_cases": [
            {"inputs": "3\n2 5 5\n3 5 5 5\n2 4 5", "output": "2"},
            {"inputs": "2\n4 5 5 5 5\n3 5 5 4", "output": "1"},
            {"inputs": "1\n1 5", "output": "1"},
        ],
        "code_examples": {
            "python": (
                "n = int(input())\n"
                "count = 0\n"
                "for i in range(n):\n"
                "    data = list(map(int, input().split()))\n"
                "    num_grades = data[0]\n"
                "    grades = data[1:]\n"
                "    all_perfect = True\n"
                "    for grade in grades:\n"
                "        if grade != 5:\n"
                "            all_perfect = False\n"
                "            break\n"
                "    if all_perfect:\n"
                "        count += 1\n"
                "print(count)"
            ),
            "cpp": (
                "#include <iostream>\n"
                "using namespace std;\n"
                "int main() {\n"
                "    int n;\n"
                "    cin >> n;\n"
                "    int count = 0;\n"
                "    for (int i = 0; i < n; i++) {\n"
                "        int num_grades;\n"
                "        cin >> num_grades;\n"
                "        bool all_perfect = true;\n"
                "        for (int j = 0; j < num_grades; j++) {\n"
                "            int grade;\n"
                "            cin >> grade;\n"
                "            if (grade != 5) {\n"
                "                all_perfect = false;\n"
                "            }\n"
                "        }\n"
                "        if (all_perfect) {\n"
                "            count++;\n"
                "        }\n"
                "    }\n"
                "    cout << count << endl;\n"
                "    return 0;\n"
                "}"
            ),
        },
    },
]


def load_initial_tasks():
    """Load initial tasks into the database."""
    # Create engine and session
    settings = Settings()
    engine = create_engine(settings.db.dsn)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Check if tasks already exist
        existing_tasks = (
            session.query(Task)
            .filter(Task.id.in_([t["id"] for t in INITIAL_TASKS]))
            .count()
        )

        if existing_tasks > 0:
            print(f"⚠️  {existing_tasks} tasks already exist. Skipping load.")
            return

        # Add each task
        for task_data in INITIAL_TASKS:
            task = Task(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data["description"],
                difficulty=task_data["difficulty"],
                task_type=task_data["task_type"],
                test_cases=task_data.get("test_cases", []),
                code_examples=task_data.get("code_examples", {}),
                flow_spec=task_data.get("flow_spec", {}),
                teacher_id=None,  # System tasks have no author
            )
            session.add(task)

        session.commit()
        print(f"✅ Successfully loaded {len(INITIAL_TASKS)} tasks into the database!")

    except Exception as e:
        print(f"❌ Error loading tasks: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    load_initial_tasks()
