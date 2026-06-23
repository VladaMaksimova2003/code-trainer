"""Curated сборка_фрагмента payloads for algo_basics chapter 1.

Policy: >=3 meaningful gaps per language (each gap maps to a chapter-1 MPLT banner).
"""
from __future__ import annotations

from typing import Any

CH1_FRAGMENT_ASSEMBLY: dict[str, dict[str, dict[str, Any]]] = {
    "task_002": {
        "python": {
            "template": (
                "n, target = {0}(int, input().split())\n"
                "\n"
                "position = 0\n"
                "\n"
                "for i in range({1}, n + 1):\n"
                "    code = int(input())\n"
                "\n"
                "    if code == target and position == {2}:\n"
                "        position = i\n"
                "\n"
                "print(position)"
            ),
            "blocks": ["map", "zip", "1", "0", "0", "1"],
            "correct_order": [0, 2, 3],
        },
        "pascal": {
            "template": (
                "var n, i, code, target, position: integer;\n"
                "begin\n"
                "  {0};\n"
                "\n"
                "  position := 0;\n"
                "\n"
                "  for i := {1} to n do\n"
                "  begin\n"
                "    readln(code);\n"
                "\n"
                "    if (code {2} target) and (position = 0) then\n"
                "      position := i;\n"
                "  end;\n"
                "\n"
                "  writeln(position);\n"
                "end."
            ),
            "blocks": [
                "readln(n, target)",
                "readln(n); readln(target)",
                "1",
                "0",
                "=",
                ":=",
            ],
            "correct_order": [0, 2, 4],
        },
        "cpp": {
            "template": (
                "#include <iostream>\n"
                "\n"
                "int main() {\n"
                "    int n, target, code;\n"
                "    int position = 0;\n"
                "\n"
                "    {0};\n"
                "\n"
                "    for (int i = {1}; i <= n; i++) {\n"
                "        std::cin >> code;\n"
                "\n"
                "        if (code {2} target && position == 0) {\n"
                "            position = i;\n"
                "        }\n"
                "    }\n"
                "\n"
                "    std::cout << position;\n"
                "    return 0;\n"
                "}"
            ),
            "blocks": [
                "std::cin >> n >> target",
                "std::cin >> n; std::cin >> target",
                "1",
                "0",
                "==",
                "=",
            ],
            "correct_order": [0, 2, 4],
        },
        "csharp": {
            "template": (
                "using System;\n"
                "\n"
                "class Program {\n"
                "    static void Main() {\n"
                "        string[] first = Console.ReadLine().Split();\n"
                "\n"
                "        int n = int.Parse(first[{0}]);\n"
                "        int target = int.Parse(first[1]);\n"
                "        int position = 0;\n"
                "\n"
                "        for (int i = {1}; i <= n; i++) {\n"
                "            int code = int.Parse(Console.ReadLine());\n"
                "\n"
                "            if (code == target && position == {2}) {\n"
                "                position = i;\n"
                "            }\n"
                "        }\n"
                "\n"
                "        Console.WriteLine(position);\n"
                "    }\n"
                "}"
            ),
            "blocks": ["first[0]", "first[1]", "1", "0", "0", "1"],
            "correct_order": [0, 2, 3],
        },
        "java": {
            "template": (
                "import java.util.*;\n"
                "\n"
                "class Main {\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "\n"
                "        {0};\n"
                "        int position = 0;\n"
                "\n"
                "        for (int i = {1}; i <= n; i++) {\n"
                "            int code = sc.nextInt();\n"
                "\n"
                "            if (code == target && position == {2}) {\n"
                "                position = i;\n"
                "            }\n"
                "        }\n"
                "\n"
                "        System.out.println(position);\n"
                "    }\n"
                "}"
            ),
            "blocks": [
                "int n = sc.nextInt(); int target = sc.nextInt()",
                "int n = sc.nextInt();",
                "1",
                "0",
                "0",
                "1",
            ],
            "correct_order": [0, 2, 4],
        },
    },
    "task_006": {
        "python": {
            "template": (
                "n = int(input())\n"
                "total = {0}\n"
                "for _ in range({1}):\n"
                "    load = int(input())\n"
                "    total += load\n"
                "print(total {2} n)"
            ),
            "blocks": ["0", "1", "n", "//", "/"],
            "correct_order": [0, 2, 3],
        },
        "pascal": {
            "template": (
                "var n, i, load, total: integer;\n"
                "begin\n"
                "  readln(n);\n"
                "  total := {0};\n"
                "  for i := {1} to {2} do\n"
                "  begin\n"
                "    readln(load);\n"
                "    total := total + load;\n"
                "  end;\n"
                "  writeln(total {3} n);\n"
                "end."
            ),
            "blocks": ["0", "0", "1", "n", "n - 1", "div", "/"],
            "correct_order": [0, 2, 3, 5],
        },
        "cpp": {
            "template": (
                "#include <iostream>\n"
                "\n"
                "int main() {\n"
                "    int n;\n"
                "    std::cin >> n;\n"
                "\n"
                "    int total = {0};\n"
                "\n"
                "    for (int i = {1}; i < n; i++) {\n"
                "        int load;\n"
                "        std::cin >> load;\n"
                "        total += load;\n"
                "    }\n"
                "\n"
                "    std::cout << total {2} n;\n"
                "    return 0;\n"
                "}"
            ),
            "blocks": ["0", "1", "0", "1", "/", "%"],
            "correct_order": [0, 2, 4],
        },
        "csharp": {
            "template": (
                "using System;\n"
                "\n"
                "class Program {\n"
                "    static void Main() {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        int total = {0};\n"
                "\n"
                "        for (int i = {1}; i < n; i++) {\n"
                "            int load = int.Parse(Console.ReadLine());\n"
                "            total += load;\n"
                "        }\n"
                "\n"
                "        Console.WriteLine(total {2} n);\n"
                "    }\n"
                "}"
            ),
            "blocks": ["0", "1", "0", "1", "/", "%"],
            "correct_order": [0, 2, 4],
        },
        "java": {
            "template": (
                "import java.util.*;\n"
                "\n"
                "class Main {\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "\n"
                "        int n = sc.nextInt();\n"
                "        int total = {0};\n"
                "\n"
                "        for (int i = {1}; i < n; i++) {\n"
                "            int load = sc.nextInt();\n"
                "            total += load;\n"
                "        }\n"
                "\n"
                "        System.out.println(total {2} n);\n"
                "    }\n"
                "}"
            ),
            "blocks": ["0", "1", "0", "1", "/", "%"],
            "correct_order": [0, 2, 4],
        },
    },
    "task_129": {
        "python": {
            "template": (
                "n = int(input())\n"
                "if n < 0:\n"
                "    n = {0}\n"
                "s = {1}\n"
                "while n > 0:\n"
                "    s += n {2} 10\n"
                "    n //= 10\n"
                "print(s)"
            ),
            "blocks": ["-n", "n", "0", "1", "%", "//"],
            "correct_order": [0, 2, 4],
        },
        "pascal": {
            "template": (
                "var n, s, d: integer;\n"
                "begin\n"
                "  readln(n);\n"
                "  if n < 0 then n := {0};\n"
                "  s := {1};\n"
                "  while n > 0 do\n"
                "  begin\n"
                "    d := n {2} 10;\n"
                "    s := s + d;\n"
                "    n := n div 10;\n"
                "  end;\n"
                "  writeln(s);\n"
                "end."
            ),
            "blocks": ["-n", "n", "0", "1", "mod", "div", "/"],
            "correct_order": [0, 2, 4],
        },
        "cpp": {
            "template": (
                "#include <iostream>\n"
                "\n"
                "int main() {\n"
                "    int n, s = {0};\n"
                "    std::cin >> n;\n"
                "    if (n < 0) n = {1};\n"
                "    while (n > 0) {\n"
                "        s += n {2} 10;\n"
                "        n /= 10;\n"
                "    }\n"
                "    std::cout << s;\n"
                "    return 0;\n"
                "}"
            ),
            "blocks": ["0", "1", "-n", "n", "%", "/"],
            "correct_order": [0, 3, 4],
        },
        "csharp": {
            "template": (
                "using System;\n"
                "\n"
                "class Program {\n"
                "    static void Main() {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        if (n < 0) n = {0};\n"
                "        int s = {1};\n"
                "        while (n > 0) {\n"
                "            s += n {2} 10;\n"
                "            n /= 10;\n"
                "        }\n"
                "        Console.WriteLine(s);\n"
                "    }\n"
                "}"
            ),
            "blocks": ["-n", "n", "0", "1", "%", "/"],
            "correct_order": [0, 2, 4],
        },
        "java": {
            "template": (
                "import java.util.*;\n"
                "\n"
                "class Main {\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        int n = sc.nextInt();\n"
                "        if (n < 0) n = {0};\n"
                "        int s = {1};\n"
                "        while (n > 0) {\n"
                "            s += n {2} 10;\n"
                "            n /= 10;\n"
                "        }\n"
                "        System.out.println(s);\n"
                "    }\n"
                "}"
            ),
            "blocks": ["-n", "n", "0", "1", "%", "/"],
            "correct_order": [0, 2, 4],
        },
    },
}


def gap_count_for_template(template: str) -> int:
    return sum(1 for idx in range(8) if ("{" + str(idx) + "}") in str(template))
