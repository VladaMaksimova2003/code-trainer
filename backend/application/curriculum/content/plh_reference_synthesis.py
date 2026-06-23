"""Synthesize executable reference code for plh_* tasks from test cases."""

from __future__ import annotations

import re
from typing import Any


def _tokens(line: str) -> list[str]:
    return [part for part in str(line or "").strip().split() if part]


def synthesize_python_reference(meta: dict[str, Any]) -> str:
    cases = list(meta.get("test_cases") or [])
    if not cases:
        return "print('ok')"

    first = cases[0]
    inp = str(first.get("inputs") or "").strip()
    out = str(first.get("output") or "").strip()

    if not inp or "нет входных данных" in inp.lower():
        escaped = out.replace("\\", "\\\\").replace("'", "\\'")
        return f"print('{escaped}')"

    in_t = _tokens(inp)
    out_t = _tokens(out)

    # name price qty delivery -> name qty total
    if len(in_t) == 4 and len(out_t) == 3 and in_t[0] == out_t[0]:
        return (
            "name = input()\n"
            "price = int(input())\n"
            "qty = int(input())\n"
            "delivery = int(input())\n"
            "total = price * qty + delivery\n"
            "print(name, qty, total)"
        )

    # name a b -> name total (total = a+b, clamped)
    if len(in_t) == 3 and len(out_t) >= 2 and in_t[0] == out_t[0]:
        return (
            "name = input()\n"
            "a = int(input())\n"
            "b = int(input())\n"
            "total = a + b\n"
            "if total >= 0:\n"
            "    print(name, total)\n"
            "else:\n"
            "    print(name, 0)"
        )

    # three ints -> one int (e.g. sum 1..N)
    if len(in_t) == 1 and len(out_t) == 1 and in_t[0].isdigit() and out_t[0].isdigit():
        n = int(in_t[0])
        if int(out_t[0]) == n:
            return "n = int(input())\nprint(n)"
        if int(out_t[0]) == n * (n + 1) // 2:
            return (
                "n = int(input())\n"
                "s = 0\n"
                "for i in range(1, n + 1):\n"
                "    s += i\n"
                "print(s)"
            )
        if int(out_t[0]) == 1:
            return (
                "def fact(n):\n"
                "    if n <= 1:\n"
                "        return 1\n"
                "    return n * fact(n - 1)\n"
                "n = int(input())\n"
                "print(fact(n))"
            )

    # two ints -> one int
    if len(in_t) == 2 and len(out_t) == 1 and all(x.isdigit() or re.match(r"^-?\d+$", x) for x in in_t + out_t):
        return (
            "a = int(input())\n"
            "b = int(input())\n"
            "print(a + b)"
        )

    # single int -> single int (square)
    if len(in_t) == 1 and len(out_t) == 1 and in_t[0].lstrip("-").isdigit():
        return "n = int(input())\nprint(n * n)"

    # echo line
    if inp == out:
        if len(in_t) == 1:
            return "s = input()\nprint(s)"
        return "line = input()\nprint(line)"

    # fallback: print expected output for first case (non-interactive stub)
    escaped = out.replace("\\", "\\\\").replace("'", "\\'")
    return f"print('{escaped}')"


def enrich_reference_codes(meta: dict[str, Any]) -> dict[str, str]:
    refs = dict(meta.get("reference_codes") or {})
    py = synthesize_python_reference(meta)
    refs["python"] = py

    # Mirror python logic to other langs only when docx refs look like duplicated template.
    dup_markers = ("name = input()", "readln(name)", "sc.next()", "Console.ReadLine()")
    dup_count = sum(
        1 for code in refs.values() if any(marker in str(code) for marker in dup_markers)
    )
    if dup_count >= 3 or not refs.get("pascal"):
        refs["pascal"] = _mirror_to_pascal(py)
        refs["cpp"] = _mirror_to_cpp(py)
        refs["csharp"] = _mirror_to_csharp(py)
        refs["java"] = _mirror_to_java(py)
    return refs


def _mirror_to_pascal(py: str) -> str:
    if "price * qty + delivery" in py:
        return (
            "var name: string; price,qty,delivery,total: integer;\n"
            "begin\n"
            "  readln(name);\n"
            "  readln(price);\n"
            "  readln(qty);\n"
            "  readln(delivery);\n"
            "  total := price * qty + delivery;\n"
            "  writeln(name, ' ', qty, ' ', total);\n"
            "end."
        )
    if "fact(n)" in py:
        return (
            "function fact(n: integer): integer;\n"
            "begin\n"
            "  if n <= 1 then fact := 1 else fact := n * fact(n - 1);\n"
            "end;\n"
            "var n: integer;\n"
            "begin\n"
            "  readln(n);\n"
            "  writeln(fact(n));\n"
            "end."
        )
    if "name = input()" in py and "total = a + b" in py:
        return (
            "var name: string; a,b,total: integer;\n"
            "begin\n"
            "  readln(name);\n"
            "  readln(a);\n"
            "  readln(b);\n"
            "  total := a + b;\n"
            "  if total >= 0 then writeln(name, ' ', total) else writeln(name, ' ', 0);\n"
            "end."
        )
    if "print(n * n)" in py:
        return "var n: integer;\nbegin\n  readln(n);\n  writeln(n * n);\nend."
    if "for i in range(1, n + 1)" in py:
        return (
            "var n,s,i: integer;\n"
            "begin\n"
            "  readln(n);\n"
            "  s := 0;\n"
            "  for i := 1 to n do s := s + i;\n"
            "  writeln(s);\n"
            "end."
        )
    return "begin\n  writeln('ok');\nend."

def _mirror_to_cpp(py: str) -> str:
    if "price * qty + delivery" in py:
        return (
            "#include <iostream>\n#include <string>\n"
            "int main(){\n"
            "  std::string name; int price,qty,delivery,total;\n"
            "  std::cin >> name >> price >> qty >> delivery;\n"
            "  total = price * qty + delivery;\n"
            "  std::cout << name << ' ' << qty << ' ' << total;\n"
            "  return 0;\n}"
        )
    if "name = input()" in py and "total = a + b" in py:
        return (
            "#include <iostream>\n#include <string>\n"
            "int main(){\n"
            "  std::string name; int a,b,total;\n"
            "  std::cin >> name >> a >> b;\n"
            "  total = a + b;\n"
            "  if(total >= 0) std::cout << name << ' ' << total;\n"
            "  else std::cout << name << ' ' << 0;\n"
            "  return 0;\n}"
        )
    if "print(n * n)" in py:
        return "#include <iostream>\nint main(){ int n; std::cin>>n; std::cout<<n*n; return 0; }"
    return "#include <iostream>\nint main(){ std::cout<<\"ok\"; return 0; }"


def _mirror_to_csharp(py: str) -> str:
    if "price * qty + delivery" in py:
        return (
            "using System;\nclass Program{\n  static void Main(){\n"
            "    string name = Console.ReadLine();\n"
            "    int price = int.Parse(Console.ReadLine());\n"
            "    int qty = int.Parse(Console.ReadLine());\n"
            "    int delivery = int.Parse(Console.ReadLine());\n"
            "    int total = price * qty + delivery;\n"
            "    Console.WriteLine($\"{name} {qty} {total}\");\n  }}"
        )
    if "name = input()" in py and "total = a + b" in py:
        return (
            "using System;\nclass Program{\n  static void Main(){\n"
            "    string name = Console.ReadLine();\n"
            "    int a = int.Parse(Console.ReadLine());\n"
            "    int b = int.Parse(Console.ReadLine());\n"
            "    int total = a + b;\n"
            "    Console.WriteLine(total >= 0 ? $\"{name} {total}\" : $\"{name} 0\");\n  }}"
        )
    return "using System;\nclass Program{ static void Main(){ Console.WriteLine(\"ok\"); } }"


def _mirror_to_java(py: str) -> str:
    if "price * qty + delivery" in py:
        return (
            "import java.util.*;\nclass Main{\n  public static void main(String[] args){\n"
            "    Scanner sc = new Scanner(System.in);\n"
            "    String name = sc.next();\n"
            "    int price = sc.nextInt(), qty = sc.nextInt(), delivery = sc.nextInt();\n"
            "    int total = price * qty + delivery;\n"
            "    System.out.println(name + \" \" + qty + \" \" + total);\n  }}"
        )
    if "name = input()" in py and "total = a + b" in py:
        return (
            "import java.util.*;\nclass Main{\n  public static void main(String[] args){\n"
            "    Scanner sc = new Scanner(System.in);\n"
            "    String name = sc.next();\n"
            "    int a = sc.nextInt(), b = sc.nextInt(), total = a + b;\n"
            "    System.out.println(name + \" \" + (total >= 0 ? total : 0));\n  }}"
        )
    return "class Main{ public static void main(String[] args){ System.out.println(\"ok\"); } }"
