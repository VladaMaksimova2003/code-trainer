"""Demo tasks for преподавательское демо (автор: Admin)."""
from __future__ import annotations

from shared.enums import AssignmentType


def _linear_diagram(*steps: tuple[str, str]) -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []
    for index, (block_type, text) in enumerate(steps):
        node_id = str(index + 1)
        nodes.append(
            {
                "id": node_id,
                "type": block_type,
                "text": text,
                "position": {"x": 240, "y": 50 + index * 120},
            }
        )
        if index > 0:
            edges.append(
                {
                    "id": f"e{index}",
                    "source": str(index),
                    "target": node_id,
                }
            )
    return {"nodes": nodes, "edges": edges, "flow": []}


def _even_odd_diagram() -> dict:
    return {
        "nodes": [
            {"id": "1", "type": "start", "text": "Начало", "position": {"x": 240, "y": 40}},
            {"id": "2", "type": "input", "text": "n", "position": {"x": 240, "y": 150}},
            {"id": "3", "type": "decision", "text": "n % 2 == 0", "position": {"x": 240, "y": 270}},
            {"id": "4", "type": "output", "text": "Even", "position": {"x": 80, "y": 400}},
            {"id": "5", "type": "output", "text": "Odd", "position": {"x": 400, "y": 400}},
            {"id": "6", "type": "end", "text": "Конец", "position": {"x": 240, "y": 520}},
        ],
        "edges": [
            {"id": "e1", "source": "1", "target": "2"},
            {"id": "e2", "source": "2", "target": "3"},
            {"id": "e3", "source": "3", "target": "4"},
            {"id": "e4", "source": "3", "target": "5"},
            {"id": "e5", "source": "4", "target": "6"},
            {"id": "e6", "source": "5", "target": "6"},
        ],
        "flow": [],
    }


FLOW_SPEC = {
    "allowed_blocks": ["start", "input", "process", "decision", "loop", "output", "end"],
}


def showcase_tasks() -> list[dict]:
    """Демо-задания: 4 типа × 3 сложности."""
    items: list[dict] = []

    # --- Сборка из блоков (препод задаёт код, выделяет фрагменты в блоки) ---
    items.extend(
        [
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "easy",
                "language": "python",
                "title": "Сумма двух чисел",
                "description": "Расставьте блоки, чтобы программа считывала два числа и выводила их сумму.",
                "original_code": "a = int(input())\nb = int(input())\nprint(a + b)",
                "template": "a = int(input())\nb = int(input())\n{0}",
                "blocks": ["print(a + b)"],
                "correct_order": [0],
                "patterns": ["assign", "io", "binary_expression"],
                "test_cases": [{"inputs": "2\n3", "output": "5"}, {"inputs": "10\n-4", "output": "6"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "medium",
                "language": "cpp",
                "title": "Максимум из трёх",
                "description": "Соберите программу, которая находит наибольшее из трёх целых чисел.",
                "original_code": (
                    "#include <iostream>\n"
                    "using namespace std;\n"
                    "int main() {\n"
                    "    int a, b, c;\n"
                    "    cin >> a >> b >> c;\n"
                    "    int m = a;\n"
                    "    if (b > m) m = b;\n"
                    "    if (c > m) m = c;\n"
                    "    cout << m << endl;\n"
                    "    return 0;\n"
                    "}"
                ),
                "template": None,
                "blocks": [
                    "    return 0;",
                    "    int a, b, c;",
                    "int main() {",
                    "    if (c > m) m = c;",
                    "using namespace std;",
                    "    cout << m << endl;",
                    "#include <iostream>",
                    "    cin >> a >> b >> c;",
                    "    if (b > m) m = b;",
                    "    int m = a;",
                    "}",
                ],
                "correct_order": [6, 4, 2, 1, 7, 9, 8, 3, 5, 0, 10],
                "patterns": ["if_statement", "assign", "io"],
                "test_cases": [{"inputs": "1 5 3", "output": "5"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "hard",
                "language": "java",
                "title": "Факториал",
                "description": "Вставьте блоки в шаблон: программа должна вычислить факториал числа n.",
                "original_code": (
                    "import java.util.Scanner;\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int n = sc.nextInt();\n"
                    "        long f = 1;\n"
                    "        for (int i = 2; i <= n; i++) f *= i;\n"
                    "        System.out.println(f);\n"
                    "    }\n"
                    "}"
                ),
                "template": (
                    "import java.util.Scanner;\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int n = sc.nextInt();\n"
                    "        long f = 1;\n"
                    "        {0}\n"
                    "        System.out.println(f);\n"
                    "    }\n"
                    "}"
                ),
                "blocks": ["for (int i = 2; i <= n; i++) f *= i;"],
                "correct_order": [0],
                "patterns": ["for_loop", "io"],
                "test_cases": [{"inputs": "5", "output": "120"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "easy",
                "language": "pascal",
                "title": "Приветствие",
                "description": "Вставьте блок вывода в заготовку программы.",
                "original_code": "program Hello;\nbegin\n  writeln('Hello');\nend.",
                "template": "program Hello;\nbegin\n  {0}\nend.",
                "blocks": ["writeln('Hello');"],
                "correct_order": [0],
                "patterns": ["io"],
                "test_cases": [{"inputs": "", "output": "Hello"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "medium",
                "language": "csharp",
                "title": "Чётность числа",
                "description": "Вставьте ветви условия в заготовку программы.",
                "original_code": (
                    "using System;\n"
                    "class Program {\n"
                    "    static void Main() {\n"
                    "        int n = int.Parse(Console.ReadLine());\n"
                    "        if (n % 2 == 0) Console.WriteLine(\"Even\");\n"
                    "        else Console.WriteLine(\"Odd\");\n"
                    "    }\n"
                    "}"
                ),
                "template": (
                    "using System;\n"
                    "class Program {\n"
                    "    static void Main() {\n"
                    "        int n = int.Parse(Console.ReadLine());\n"
                    "        {0}\n"
                    "        {1}\n"
                    "    }\n"
                    "}"
                ),
                "blocks": [
                    'if (n % 2 == 0) Console.WriteLine("Even");',
                    'else Console.WriteLine("Odd");',
                ],
                "correct_order": [0, 1],
                "patterns": ["if_statement", "io"],
                "test_cases": [{"inputs": "4", "output": "Even"}, {"inputs": "7", "output": "Odd"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "easy",
                "language": "python",
                "title": "Среднее арифметическое",
                "description": "Допишите цикл в заготовку: программа считывает n чисел и выводит среднее.",
                "original_code": (
                    "n = int(input())\n"
                    "total = 0\n"
                    "for _ in range(n):\n"
                    "    total += int(input())\n"
                    "print(total / n)"
                ),
                "template": (
                    "n = int(input())\n"
                    "total = 0\n"
                    "{0}\n"
                    "print(total / n)"
                ),
                "blocks": ["for _ in range(n):\n    total += int(input())"],
                "correct_order": [0],
                "patterns": ["for_loop", "io", "binary_expression"],
                "test_cases": [{"inputs": "3\n2\n4\n6", "output": "4.0"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "medium",
                "language": "cpp",
                "title": "Абсолютное значение",
                "description": "Вставьте условие в готовый каркас программы на C++.",
                "original_code": (
                    "#include <iostream>\n"
                    "using namespace std;\n"
                    "int main() {\n"
                    "    int x;\n"
                    "    cin >> x;\n"
                    "    if (x < 0) x = -x;\n"
                    "    cout << x << endl;\n"
                    "    return 0;\n"
                    "}"
                ),
                "template": (
                    "#include <iostream>\n"
                    "using namespace std;\n"
                    "int main() {\n"
                    "    int x;\n"
                    "    cin >> x;\n"
                    "    {0}\n"
                    "    cout << x << endl;\n"
                    "    return 0;\n"
                    "}"
                ),
                "blocks": ["if (x < 0) x = -x;"],
                "correct_order": [0],
                "patterns": ["if_statement", "io"],
                "test_cases": [{"inputs": "-5", "output": "5"}, {"inputs": "3", "output": "3"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "medium",
                "language": "java",
                "title": "Сумма массива",
                "description": "Подставьте блоки чтения и цикла в шаблон программы.",
                "original_code": (
                    "import java.util.Scanner;\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int n = sc.nextInt();\n"
                    "        int sum = 0;\n"
                    "        for (int i = 0; i < n; i++) sum += sc.nextInt();\n"
                    "        System.out.println(sum);\n"
                    "    }\n"
                    "}"
                ),
                "template": (
                    "import java.util.Scanner;\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int n = sc.nextInt();\n"
                    "        int sum = 0;\n"
                    "        {0}\n"
                    "        System.out.println(sum);\n"
                    "    }\n"
                    "}"
                ),
                "blocks": ["for (int i = 0; i < n; i++) sum += sc.nextInt();"],
                "correct_order": [0],
                "patterns": ["for_loop", "io"],
                "test_cases": [{"inputs": "3\n1 2 3", "output": "6"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "hard",
                "language": "csharp",
                "title": "Степень числа",
                "description": "Вставьте тело цикла и обновление результата в заготовку.",
                "original_code": (
                    "using System;\n"
                    "class Program {\n"
                    "    static void Main() {\n"
                    "        int a = int.Parse(Console.ReadLine());\n"
                    "        int n = int.Parse(Console.ReadLine());\n"
                    "        long p = 1;\n"
                    "        for (int i = 0; i < n; i++) p *= a;\n"
                    "        Console.WriteLine(p);\n"
                    "    }\n"
                    "}"
                ),
                "template": (
                    "using System;\n"
                    "class Program {\n"
                    "    static void Main() {\n"
                    "        int a = int.Parse(Console.ReadLine());\n"
                    "        int n = int.Parse(Console.ReadLine());\n"
                    "        long p = 1;\n"
                    "        {0}\n"
                    "        Console.WriteLine(p);\n"
                    "    }\n"
                    "}"
                ),
                "blocks": ["for (int i = 0; i < n; i++) p *= a;"],
                "correct_order": [0],
                "patterns": ["for_loop", "io"],
                "test_cases": [{"inputs": "2\n3", "output": "8"}],
            },
            {
                "assignment_type": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
                "difficulty": "hard",
                "language": "pascal",
                "title": "Подсчёт делителей",
                "description": "Вставьте цикл и условие в шаблон программы.",
                "original_code": (
                    "program Divisors;\nvar n, i, cnt: integer;\nbegin\n"
                    "  readln(n);\n"
                    "  cnt := 0;\n"
                    "  for i := 1 to n do\n"
                    "    if n mod i = 0 then cnt := cnt + 1;\n"
                    "  writeln(cnt);\n"
                    "end."
                ),
                "template": (
                    "program Divisors;\nvar n, i, cnt: integer;\nbegin\n"
                    "  readln(n);\n"
                    "  cnt := 0;\n"
                    "  {0}\n"
                    "  writeln(cnt);\n"
                    "end."
                ),
                "blocks": [
                    "for i := 1 to n do\n    if n mod i = 0 then cnt := cnt + 1;"
                ],
                "correct_order": [0],
                "patterns": ["for_loop", "if_statement", "io"],
                "test_cases": [{"inputs": "6", "output": "4"}],
            },
        ]
    )

    # --- Перевод фрагмента (исходный код задан преподавателем) ---
    items.extend(
        [
            {
                "assignment_type": AssignmentType.TASK_TRANSLATE_SNIPPET.value,
                "difficulty": "easy",
                "language": "python",
                "title": "Суммирование элементов",
                "description": "Переведите фрагмент, который накапливает сумму элементов коллекции.",
                "source_code": "total = 0\nfor x in data:\n    total += x",
                "patterns": ["for_loop", "assign"],
                "test_cases": [],
            },
            {
                "assignment_type": AssignmentType.TASK_TRANSLATE_SNIPPET.value,
                "difficulty": "medium",
                "language": "cpp",
                "title": "Знак числа",
                "description": "Переведите фрагмент с проверкой знака числа.",
                "source_code": (
                    "if (x > 0) {\n"
                    "    cout << \"positive\";\n"
                    "} else {\n"
                    "    cout << \"non-positive\";\n"
                    "}"
                ),
                "patterns": ["if_statement", "io"],
                "test_cases": [],
            },
            {
                "assignment_type": AssignmentType.TASK_TRANSLATE_SNIPPET.value,
                "difficulty": "hard",
                "language": "java",
                "title": "Вложенные циклы",
                "description": "Переведите фрагмент с вложенными циклами.",
                "source_code": (
                    "for (int i = 0; i < n; i++) {\n"
                    "    for (int j = 0; j < m; j++) {\n"
                    "        System.out.print(i * j + \" \");\n"
                    "    }\n"
                    "}"
                ),
                "patterns": ["nested_loops", "for_loop", "io"],
                "test_cases": [],
            },
        ]
    )

    # --- Перевод программы ---
    items.extend(
        [
            {
                "assignment_type": AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
                "difficulty": "easy",
                "language": "python",
                "title": "Квадрат числа",
                "description": "Переведите программу, которая считывает число и выводит его квадрат.",
                "source_code": "n = int(input())\nprint(n * n)",
                "patterns": ["assign", "io", "binary_expression"],
                "test_cases": [{"inputs": "5", "output": "25"}],
            },
            {
                "assignment_type": AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
                "difficulty": "medium",
                "language": "cpp",
                "title": "Минимум из двух",
                "description": "Переведите программу поиска меньшего из двух чисел.",
                "source_code": (
                    "#include <iostream>\n"
                    "using namespace std;\n"
                    "int main() {\n"
                    "    int a, b; cin >> a >> b;\n"
                    "    cout << min(a, b) << endl;\n"
                    "    return 0;\n"
                    "}"
                ),
                "patterns": ["io", "assign"],
                "test_cases": [{"inputs": "8 3", "output": "3"}],
            },
            {
                "assignment_type": AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
                "difficulty": "hard",
                "language": "pascal",
                "title": "Таблица умножения",
                "description": "Переведите программу, выводящую таблицу умножения на 9.",
                "source_code": (
                    "program Mul9;\nvar i: integer;\nbegin\n"
                    "  for i := 1 to 9 do\n"
                    "    writeln('9 * ', i, ' = ', 9 * i);\n"
                    "end."
                ),
                "patterns": ["for_loop", "io"],
                "test_cases": [{"inputs": "", "output": "9 * 1 = 9"}],
            },
        ]
    )

    # --- Блок-схема в код ---
    items.extend(
        [
            {
                "assignment_type": AssignmentType.TASK_FLOWCHART_TO_CODE.value,
                "difficulty": "easy",
                "language": "python",
                "title": "Удвоить число",
                "description": "По блок-схеме напишите программу: ввод n, вывод удвоенного значения.",
                "diagram": _linear_diagram(
                    ("start", "Начало"),
                    ("input", "n"),
                    ("process", "r = n * 2"),
                    ("output", "print(r)"),
                    ("end", "Конец"),
                ),
                "reference_code": "n = int(input())\nprint(n * 2)",
                "expose_reference_code": True,
                "patterns": ["assign", "io"],
                "test_cases": [{"inputs": "7", "output": "14"}],
            },
            {
                "assignment_type": AssignmentType.TASK_FLOWCHART_TO_CODE.value,
                "difficulty": "medium",
                "language": "cpp",
                "title": "Чётное или нечётное",
                "description": "Реализуйте алгоритм из блок-схемы.",
                "diagram": _even_odd_diagram(),
                "reference_code": (
                    "#include <iostream>\n"
                    "using namespace std;\n"
                    "int main() {\n"
                    "    int n; cin >> n;\n"
                    "    if (n % 2 == 0) cout << \"Even\" << endl;\n"
                    "    else cout << \"Odd\" << endl;\n"
                    "    return 0;\n"
                    "}"
                ),
                "expose_reference_code": False,
                "patterns": ["if_statement", "io"],
                "test_cases": [{"inputs": "4", "output": "Even"}, {"inputs": "3", "output": "Odd"}],
            },
            {
                "assignment_type": AssignmentType.TASK_FLOWCHART_TO_CODE.value,
                "difficulty": "hard",
                "language": "java",
                "title": "Сумма от 1 до n",
                "description": "По блок-схеме с циклом вычислите сумму чисел от 1 до n.",
                "diagram": _linear_diagram(
                    ("start", "Начало"),
                    ("input", "n"),
                    ("process", "sum = 0, i = 1"),
                    ("loop", "i <= n"),
                    ("process", "sum += i, i++"),
                    ("output", "print(sum)"),
                    ("end", "Конец"),
                ),
                "reference_code": "",
                "expose_reference_code": False,
                "patterns": ["for_loop", "assign", "io"],
                "test_cases": [{"inputs": "5", "output": "15"}],
            },
        ]
    )

    return items
