"""Per-task 'known language' code snippets for Pascal Course v3.1.1.

Each entry: slot_id -> (python, cpp, java, csharp)
All snippets demonstrate the SAME concept the task teaches, in each language.
"""
from __future__ import annotations

_C: dict[str, tuple[str, str, str, str]] = {
    # ── 1. program_skeleton ────────────────────────────────────────────────
    "psk_01": (
        "print('Hello, World!')",
        '#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello!" << endl;\n    return 0;\n}',
        'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello!");\n    }\n}',
        'using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello!");\n    }\n}',
    ),
    "psk_02": (
        "x = 1\nprint(x)  # нет ; в Python",
        "int x = 1;\ncout << x;  // ; обязательна в C++",
        "int x = 1;\nSystem.out.println(x);  // ; обязательна",
        "int x = 1;\nConsole.WriteLine(x);  // ; обязательна",
    ),
    "psk_03": (
        "# Нет жёсткой структуры в Python\nprint('start')\nprint('end')",
        "int main() {\n    // тело программы\n    return 0;\n}",
        "public static void main(String[] args) {\n    // тело программы\n}",
        "static void Main() {\n    // тело программы\n}",
    ),
    "psk_04": (
        "def main():\n    pass\n\nmain()  # явный вызов точки входа",
        "int main() {\n    return 0;  // точка входа\n}",
        "public static void main(String[] args) { }  // точка входа",
        "static void Main(string[] args) { }  // точка входа",
    ),
    "psk_05": (
        "print('start')\nprint('end')  # последовательность",
        "int main() {\n    // start → end\n    return 0;\n}",
        "public static void main(String[] args) {\n    // start → end\n}",
        "static void Main() {\n    // start → end\n}",
    ),
    "psk_06": (
        "print('start')\nprint('end')",
        "int main() {\n    // код → блок-схема\n    return 0;\n}",
        "public static void main(String[] args) { }",
        "static void Main() { }",
    ),
    "psk_07": (
        "# Конец программы — автоматически",
        "return 0;  // конец main()",
        "// Конец метода main — конец программы",
        "// Конец метода Main — конец программы",
    ),
    "psk_08": (
        "import sys\nimport os  # импорты вверху файла",
        "#include <iostream>\n#include <cmath>  // вверху файла",
        "import java.util.Scanner;\nimport java.util.Arrays;",
        "using System;\nusing System.IO;",
    ),
    "psk_09": (
        "# Однострочный комментарий\n\"\"\"Многострочный\nкомментарий\"\"\"",
        "// Однострочный\n/* Многострочный\n   комментарий */",
        "// Однострочный\n/* Многострочный\n   комментарий */",
        "// Однострочный\n/* Многострочный\n   комментарий */",
    ),
    "psk_11": (
        "MAX = 100  # 'const'\nx: int = 0  # var с аннотацией типа",
        "const int MAX = 100;\nint x = 0;",
        "final int MAX = 100;\nint x = 0;",
        "const int MAX = 100;\nint x = 0;",
    ),
    "psk_12": (
        "if True:\n    pass  # пустой блок",
        "if (true) {\n    // пустой блок\n}",
        "if (true) {\n    // пустой блок\n}",
        "if (true) {\n    // пустой блок\n}",
    ),

    # ── 2. typed_variables ─────────────────────────────────────────────────
    "typ_01": (
        "x: int = 0\ny: int = 0  # явный тип",
        "int x;\nint y;  // объявление в секции",
        "int x;\nint y;",
        "int x;\nint y;",
    ),
    "typ_02": (
        "x = 5  # присваивание через =",
        "int x;\nx = 5;  // присваивание",
        "int x;\nx = 5;",
        "int x;\nx = 5;",
    ),
    "typ_03": (
        "x: float = 3.14\ny: float = 2.71",
        "float x = 3.14f;\ndouble y = 3.14;",
        "float x = 3.14f;\ndouble y = 3.14;",
        "float x = 3.14f;\ndouble y = 3.14;",
    ),
    "typ_04": (
        "flag: bool = True\nif flag:\n    print('yes')",
        "bool flag = true;\nif (flag) { cout << \"yes\"; }",
        "boolean flag = true;\nif (flag) { System.out.println(\"yes\"); }",
        "bool flag = true;\nif (flag) { Console.WriteLine(\"yes\"); }",
    ),
    "typ_05": (
        "c: str = 'A'   # символ — строка длины 1\ns: str = 'AB'  # строка",
        "char c = 'A';\nstring s = \"AB\";",
        "char c = 'A';\nString s = \"AB\";",
        "char c = 'A';\nstring s = \"AB\";",
    ),
    "typ_06": (
        "MAX: int = 100\nPI: float = 3.14",
        "const int MAX = 100;\nconst double PI = 3.14;",
        "final int MAX = 100;\nfinal double PI = 3.14;",
        "const int MAX = 100;\nconst double PI = 3.14;",
    ),
    "typ_07": (
        "# Нет диапазонного типа — проверка вручную\nx = 5\nassert 1 <= x <= 10",
        "int x = 5;\nassert(x >= 1 && x <= 10);",
        "int x = 5;\nassert x >= 1 && x <= 10;",
        "int x = 5;\nif (x < 1 || x > 10) throw new Exception();",
    ),
    "typ_09": (
        "import math\nx = 7.9\nn = int(x)       # trunc\nm = round(x)     # round",
        "double x = 7.9;\nint n = (int)x;\nint m = (int)round(x);",
        "double x = 7.9;\nint n = (int)x;\nint m = (int)Math.round(x);",
        "double x = 7.9;\nint n = (int)x;\nint m = (int)Math.Round(x);",
    ),
    "typ_10": (
        "x: int = 42",
        "int x = 42;",
        "int x = 42;",
        "int x = 42;",
    ),

    # ── 3. io ──────────────────────────────────────────────────────────────
    "io_01": (
        "n = int(input())  # чтение числа",
        "int n;\ncin >> n;",
        "Scanner sc = new Scanner(System.in);\nint n = sc.nextInt();",
        "int n = int.Parse(Console.ReadLine());",
    ),
    "io_02": (
        "a, b, c = 1, 2, 3\nprint(a, b, c)  # несколько значений",
        "cout << a << \" \" << b << \" \" << c << endl;",
        "System.out.println(a + \" \" + b + \" \" + c);",
        "Console.WriteLine($\"{a} {b} {c}\");",
    ),
    "io_03": (
        "x = int(input('Введите: '))",
        "int x;\ncin >> x;",
        "int x = sc.nextInt();",
        "int x = int.Parse(Console.ReadLine());",
    ),
    "io_04": (
        "print(f'{x:8.2f}')  # форматированный вывод",
        "printf(\"%8.2f\\n\", x);",
        "System.out.printf(\"%8.2f%n\", x);",
        "Console.WriteLine($\"{x,8:F2}\");",
    ),
    "io_05": (
        "s = '42'\nn = int(s)  # парсинг строки",
        "string s = \"42\";\nint n = stoi(s);",
        "String s = \"42\";\nint n = Integer.parseInt(s);",
        "string s = \"42\";\nint n = int.Parse(s);",
    ),
    "io_06": (
        "x = int(input())\nprint(x * 2)",
        "int x;\ncin >> x;\ncout << x * 2 << endl;",
        "int x = sc.nextInt();\nSystem.out.println(x * 2);",
        "int x = int.Parse(Console.ReadLine());\nConsole.WriteLine(x * 2);",
    ),
    "io_07": (
        "n = int(input())\nprint(n * n)",
        "int n;\ncin >> n;\ncout << n * n << endl;",
        "int n = sc.nextInt();\nSystem.out.println(n * n);",
        "int n = int.Parse(Console.ReadLine());\nConsole.WriteLine(n * n);",
    ),
    "io_09": (
        "print('Введите число:')  # сначала prompt\nx = int(input())",
        "cout << \"Введите: \";\ncin >> x;",
        "System.out.print(\"Введите: \");\nint x = sc.nextInt();",
        "Console.Write(\"Введите: \");\nint x = int.Parse(Console.ReadLine());",
    ),

    # ── 4. expressions ─────────────────────────────────────────────────────
    "exp_01": (
        "a, b = 17, 5\nq = a // b  # div\nr = a % b   # mod",
        "int a=17, b=5;\nint q = a/b;  // div\nint r = a%b;  // mod",
        "int q = a/b;\nint r = a%b;",
        "int q = a/b;\nint r = a%b;",
    ),
    "exp_02": (
        "q = 17 // 5  # целочисленное деление",
        "int q = 17 / 5;  // аналог div",
        "int q = 17 / 5;",
        "int q = 17 / 5;",
    ),
    "exp_03": (
        "x = 6\nprint(x << 1)  # shl\nprint(x >> 1)  # shr\nprint(x & 3)   # and\nprint(x | 1)   # or\nprint(x ^ 2)   # xor",
        "int x=6;\nprintf(\"%d\\n\", x<<1);  // shl\nprintf(\"%d\\n\", x>>1);  // shr\nprintf(\"%d\\n\", x&3);   // and",
        "System.out.println(x<<1);\nSystem.out.println(x>>1);\nSystem.out.println(x&3);",
        "Console.WriteLine(x<<1);\nConsole.WriteLine(x>>1);\nConsole.WriteLine(x&3);",
    ),
    "exp_05": (
        "x = None\nif x is not None and x > 0:\n    print(x)  # short-circuit and",
        "if (x != nullptr && x > 0) {\n    // short-circuit &&\n}",
        "if (x != null && x > 0) { }",
        "if (x != null && x > 0) { }",
    ),
    "exp_04": (
        "s = {'a', 'b', 'c'}\nif 'a' in s:\n    print('yes')  # множество",
        "#include <set>\nset<char> s={'a','b','c'};\nif (s.count('a')) cout << \"yes\";",
        "Set<Character> s = new HashSet<>();\ns.add('a');\nif (s.contains('a')) System.out.println(\"yes\");",
        "var s = new HashSet<char>{'a','b','c'};\nif (s.Contains('a')) Console.WriteLine(\"yes\");",
    ),
    "exp_06": (
        "x = 7.5\nr = x % 2  # float mod",
        "#include <cmath>\ndouble x=7.5;\ndouble r = fmod(x, 2);",
        "double x=7.5;\ndouble r = x % 2;",
        "double x=7.5;\ndouble r = x % 2;",
    ),
    "exp_08": (
        "a, b = 17, 5\nq = a // b\nr = a % b\nprint(q, r)",
        "int q = a/b, r = a%b;\nprintf(\"%d %d\\n\", q, r);",
        "int q = a/b, r = a%b;\nSystem.out.println(q+\" \"+r);",
        "Console.WriteLine($\"{a/b} {a%b}\");",
    ),

    # ── 5. conditions ──────────────────────────────────────────────────────
    "cnd_01": (
        "x = int(input())\nif x > 0:\n    print('positive')\nelse:\n    print('not positive')",
        "if (x > 0) {\n    cout << \"positive\";\n} else {\n    cout << \"not positive\";\n}",
        "if (x > 0) {\n    System.out.println(\"positive\");\n} else {\n    System.out.println(\"not positive\");\n}",
        "if (x > 0) {\n    Console.WriteLine(\"positive\");\n} else {\n    Console.WriteLine(\"not positive\");\n}",
    ),
    "cnd_02": (
        "if x > 0:\n    print('yes')\nelse:\n    print('no')",
        "if (x > 0) {\n    cout << \"yes\";\n} else {\n    cout << \"no\";\n}",
        "if (x > 0) {\n    System.out.println(\"yes\");\n} else {\n    System.out.println(\"no\");\n}",
        "if (x > 0) {\n    Console.WriteLine(\"yes\");\n} else {\n    Console.WriteLine(\"no\");\n}",
    ),
    "cnd_03": (
        "if x > 0:\n    print('positive')\nelif x < 0:\n    print('negative')\nelse:\n    print('zero')",
        "if (x > 0) cout << \"positive\";\nelse if (x < 0) cout << \"negative\";\nelse cout << \"zero\";",
        "if (x > 0) System.out.println(\"positive\");\nelse if (x < 0) System.out.println(\"negative\");\nelse System.out.println(\"zero\");",
        "if (x > 0) Console.WriteLine(\"positive\");\nelse if (x < 0) Console.WriteLine(\"negative\");\nelse Console.WriteLine(\"zero\");",
    ),
    "cnd_04": (
        "if a > b:\n    print('a больше')\nelif a < b:\n    print('b больше')\nelse:\n    print('равны')",
        "if (a > b) cout << \"a>b\";\nelse if (a < b) cout << \"b>a\";\nelse cout << \"a==b\";",
        "if (a > b) System.out.println(\"a>b\");\nelse if (a < b) System.out.println(\"b>a\");\nelse System.out.println(\"a==b\");",
        "if (a > b) Console.WriteLine(\"a>b\");\nelse if (a < b) Console.WriteLine(\"b>a\");\nelse Console.WriteLine(\"a==b\");",
    ),
    "cnd_05": (
        "day = 3\nif day == 1: print('Mon')\nelif day == 2: print('Tue')\nelif day == 3: print('Wed')\nelse: print('Other')",
        "switch (day) {\n  case 1: cout<<\"Mon\"; break;\n  case 2: cout<<\"Tue\"; break;\n  default: cout<<\"Other\";\n}",
        "switch (day) {\n  case 1: System.out.println(\"Mon\"); break;\n  default: System.out.println(\"Other\");\n}",
        "switch (day) {\n  case 1: Console.WriteLine(\"Mon\"); break;\n  default: Console.WriteLine(\"Other\"); break;\n}",
    ),
    "cnd_06": (
        "result = 'yes' if x > 0 else 'no'  # тернарный",
        "string r = (x > 0) ? \"yes\" : \"no\";",
        "String r = (x > 0) ? \"yes\" : \"no\";",
        "string r = (x > 0) ? \"yes\" : \"no\";",
    ),
    "cnd_07": (
        "if x > 0 and y > 0:\n    print('both positive')",
        "if (x > 0 && y > 0) {\n    cout << \"both positive\";\n}",
        "if (x > 0 && y > 0) {\n    System.out.println(\"both positive\");\n}",
        "if (x > 0 && y > 0) {\n    Console.WriteLine(\"both positive\");\n}",
    ),
    "cnd_08": (
        "day = int(input())\nif day == 1: print('Mon')\nelif day == 2: print('Tue')\nelse: print('Unknown')  # else важен!",
        "switch (day) {\n  case 1: cout<<\"Mon\"; break;\n  default: cout<<\"Unknown\";  // default важен!\n}",
        "switch (day) {\n  case 1: System.out.println(\"Mon\"); break;\n  default: System.out.println(\"Unknown\");\n}",
        "switch (day) {\n  case 1: Console.WriteLine(\"Mon\"); break;\n  default: Console.WriteLine(\"Unknown\"); break;\n}",
    ),
    "cnd_09": (
        "x = int(input())\nabs_x = x if x >= 0 else -x\nprint(abs_x)",
        "int abs_x = (x >= 0) ? x : -x;\ncout << abs_x;",
        "int absX = (x >= 0) ? x : -x;\nSystem.out.println(absX);",
        "int absX = (x >= 0) ? x : -x;\nConsole.WriteLine(absX);",
    ),
    "cnd_10": (
        "grade = 'B'\nif grade == 'A': print('Отлично')\nelif grade == 'B': print('Хорошо')\nelse: print('Другое')",
        "switch (grade) {\n  case 'A': cout<<\"Отлично\"; break;\n  case 'B': cout<<\"Хорошо\"; break;\n  default: cout<<\"Другое\";\n}",
        "switch (grade) {\n  case 'A': System.out.println(\"Отлично\"); break;\n  default: System.out.println(\"Другое\");\n}",
        "switch (grade) {\n  case 'A': Console.WriteLine(\"Отлично\"); break;\n  default: Console.WriteLine(\"Другое\"); break;\n}",
    ),
    "cnd_11": (
        "if x > 0:\n    print('positive')\nelse:\n    print('non-positive')",
        "if (x > 0) cout << \"positive\";\nelse cout << \"non-positive\";",
        "if (x > 0) System.out.println(\"positive\");\nelse System.out.println(\"non-positive\");",
        "if (x > 0) Console.WriteLine(\"positive\");\nelse Console.WriteLine(\"non-positive\");",
    ),
    "cnd_12": (
        "if x > 0:\n    print('positive')\nelse:\n    print('non-positive')",
        "if (x > 0) cout << \"positive\";\nelse cout << \"non-positive\";",
        "if (x > 0) System.out.println(\"positive\");\nelse System.out.println(\"non-positive\");",
        "if (x > 0) Console.WriteLine(\"positive\");\nelse Console.WriteLine(\"non-positive\");",
    ),
    "cnd_13": (
        "if x > 0:\n    print('yes')\n# НЕТ ; перед else в Python!",
        "if (x > 0) {\n    cout << \"yes\";\n}  // НЕТ ; перед else!\nelse { cout << \"no\"; }",
        "if (x > 0) {\n    System.out.println(\"yes\");\n} else {\n    System.out.println(\"no\");\n}",
        "if (x > 0) {\n    Console.WriteLine(\"yes\");\n} else {\n    Console.WriteLine(\"no\");\n}",
    ),
    "cnd_14": (
        "day = 2\nif day == 1: print('Mon')\nelif day == 2: print('Tue')\nelse: print('Other')",
        "switch (day) {\n  case 1: cout<<\"Mon\"; break;\n  case 2: cout<<\"Tue\"; break;\n  default: cout<<\"Other\";\n}",
        "switch (day) {\n  case 1: System.out.println(\"Mon\"); break;\n  case 2: System.out.println(\"Tue\"); break;\n  default: System.out.println(\"Other\");\n}",
        "switch (day) {\n  case 1: Console.WriteLine(\"Mon\"); break;\n  default: Console.WriteLine(\"Other\"); break;\n}",
    ),

    # ── 6. loops ───────────────────────────────────────────────────────────
    "lop_01": (
        "for i in range(1, 11):\n    print(i)  # for to do",
        "for (int i=1; i<=10; i++) {\n    cout << i << endl;\n}",
        "for (int i=1; i<=10; i++) {\n    System.out.println(i);\n}",
        "for (int i=1; i<=10; i++) {\n    Console.WriteLine(i);\n}",
    ),
    "lop_02": (
        "for i in range(1, 6):\n    print(i)",
        "for (int i=1; i<=5; i++) {\n    cout << i;\n}",
        "for (int i=1; i<=5; i++) {\n    System.out.println(i);\n}",
        "for (int i=1; i<=5; i++) {\n    Console.WriteLine(i);\n}",
    ),
    "lop_03": (
        "for i in range(10, 0, -1):\n    print(i)  # downto",
        "for (int i=10; i>=1; i--) {\n    cout << i;\n}",
        "for (int i=10; i>=1; i--) {\n    System.out.println(i);\n}",
        "for (int i=10; i>=1; i--) {\n    Console.WriteLine(i);\n}",
    ),
    "lop_04": (
        "x = int(input())\nwhile x > 0:\n    print(x)\n    x -= 1",
        "int x;\ncin >> x;\nwhile (x > 0) {\n    cout << x;\n    x--;\n}",
        "while (x > 0) {\n    System.out.println(x);\n    x--;\n}",
        "while (x > 0) {\n    Console.WriteLine(x);\n    x--;\n}",
    ),
    "lop_05": (
        "count = 0\nwhile True:\n    count += 1\n    if count >= 5:\n        break  # repeat..until",
        "int count = 0;\ndo {\n    count++;\n} while (count < 5);",
        "int count = 0;\ndo {\n    count++;\n} while (count < 5);",
        "int count = 0;\ndo {\n    count++;\n} while (count < 5);",
    ),
    "lop_06": (
        "n = 0\nwhile True:\n    n += 1\n    if n >= 5:\n        break  # условие выхода",
        "int n = 0;\ndo {\n    n++;\n} while (n < 5);",
        "int n = 0;\ndo {\n    n++;\n} while (n < 5);",
        "int n = 0;\ndo {\n    n++;\n} while (n < 5);",
    ),
    "lop_07": (
        "n = 0\nwhile True:\n    n += 1\n    print(n)\n    if n >= 5:\n        break",
        "int n = 0;\ndo {\n    n++;\n    cout << n;\n} while (n < 5);",
        "int n = 0;\ndo {\n    n++;\n    System.out.println(n);\n} while (n < 5);",
        "int n = 0;\ndo {\n    n++;\n    Console.WriteLine(n);\n} while (n < 5);",
    ),
    "lop_08": (
        "n = 0\nwhile True:\n    n += 1\n    if n >= 10:\n        break  # until n >= 10",
        "int n = 0;\ndo {\n    n++;\n} while (n < 10);  // пока n < 10",
        "int n = 0;\ndo {\n    n++;\n} while (n < 10);",
        "int n = 0;\ndo {\n    n++;\n} while (n < 10);",
    ),
    "lop_09": (
        "for i in range(1, 11):\n    if i == 5:\n        break\n    if i % 2 == 0:\n        continue\n    print(i)",
        "for (int i=1; i<=10; i++) {\n    if (i==5) break;\n    if (i%2==0) continue;\n    cout << i;\n}",
        "for (int i=1; i<=10; i++) {\n    if (i==5) break;\n    if (i%2==0) continue;\n    System.out.println(i);\n}",
        "for (int i=1; i<=10; i++) {\n    if (i==5) break;\n    if (i%2==0) continue;\n    Console.WriteLine(i);\n}",
    ),
    "lop_12": (
        "for i in range(1, 4):\n    for j in range(1, 4):\n        print(i, j)  # вложенные циклы",
        "for (int i=1; i<=3; i++) {\n    for (int j=1; j<=3; j++) {\n        cout << i << \" \" << j;\n    }\n}",
        "for (int i=1; i<=3; i++) {\n    for (int j=1; j<=3; j++) {\n        System.out.println(i+\" \"+j);\n    }\n}",
        "for (int i=1; i<=3; i++) {\n    for (int j=1; j<=3; j++) {\n        Console.WriteLine($\"{i} {j}\");\n    }\n}",
    ),
    "lop_13": (
        "# while — условие ДО тела\nwhile n > 0:\n    n //= 2\n\n# do-while — хотя бы одна итерация\nwhile True:\n    n = int(input())\n    if n > 0: break",
        "while (n > 0) { n /= 2; }  // условие до\n\ndo {\n    cin >> n;\n} while (n <= 0);  // условие после",
        "while (n > 0) { n /= 2; }\n\ndo {\n    n = sc.nextInt();\n} while (n <= 0);",
        "while (n > 0) { n /= 2; }\n\ndo {\n    n = int.Parse(Console.ReadLine());\n} while (n <= 0);",
    ),
    "lop_14": (
        "for i in range(1, 11):  # правильный заголовок\n    print(i)",
        "for (int i=1; i<=10; i++) {\n    cout << i;\n}",
        "for (int i=1; i<=10; i++) {\n    System.out.println(i);\n}",
        "for (int i=1; i<=10; i++) {\n    Console.WriteLine(i);\n}",
    ),
    "lop_15": (
        "for i in range(10, 0, -1):\n    print(i)  # for downto",
        "for (int i=10; i>=1; i--) {\n    cout << i;\n}",
        "for (int i=10; i>=1; i--) {\n    System.out.println(i);\n}",
        "for (int i=10; i>=1; i--) {\n    Console.WriteLine(i);\n}",
    ),

    # ── 7. functions ───────────────────────────────────────────────────────
    "fn_01": (
        "def add(a: int, b: int) -> int:\n    return a + b",
        "int add(int a, int b) {\n    return a + b;\n}",
        "int add(int a, int b) {\n    return a + b;\n}",
        "int Add(int a, int b) {\n    return a + b;\n}",
    ),
    "fn_02": (
        "def square(x: int) -> int:\n    return x * x  # return = Result",
        "int square(int x) {\n    return x * x;  // return = Result\n}",
        "int square(int x) {\n    return x * x;\n}",
        "int Square(int x) {\n    return x * x;\n}",
    ),
    "fn_03": (
        "def compute(x: int, y: int) -> int:\n    return x + y",
        "int compute(int x, int y) {\n    return x + y;\n}",
        "int compute(int x, int y) {\n    return x + y;\n}",
        "int Compute(int x, int y) {\n    return x + y;\n}",
    ),
    "fn_04": (
        "def classify(x: int) -> str:\n    if x > 0:\n        return 'positive'\n    return 'non-positive'  # return в каждой ветке",
        "string classify(int x) {\n    if (x > 0) return \"positive\";\n    return \"non-positive\";  // return везде!\n}",
        "String classify(int x) {\n    if (x > 0) return \"positive\";\n    return \"non-positive\";\n}",
        "string Classify(int x) {\n    if (x > 0) return \"positive\";\n    return \"non-positive\";\n}",
    ),
    "fn_06": (
        "def greet(name: str) -> str:\n    return f'Hello, {name}!'",
        "string greet(string name) {\n    return \"Hello, \" + name + \"!\";\n}",
        "String greet(String name) {\n    return \"Hello, \" + name + \"!\";\n}",
        "string Greet(string name) {\n    return \"Hello, \" + name + \"!\";\n}",
    ),
    "fn_12": (
        "def factorial(n: int) -> int:\n    if n <= 1: return 1\n    return n * factorial(n - 1)",
        "int factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}",
        "int factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}",
        "int Factorial(int n) {\n    if (n <= 1) return 1;\n    return n * Factorial(n-1);\n}",
    ),
    "fn_05": (
        "# Python: forward не нужна\ndef foo(): bar()\ndef bar(): pass",
        "void bar();  // forward declaration\nvoid foo() { bar(); }\nvoid bar() { }  // реализация",
        "// Java: нет forward declaration\nvoid foo() { bar(); }\nvoid bar() { }",
        "// C#: нет forward declaration\nvoid Foo() { Bar(); }\nvoid Bar() { }",
    ),
    "fn_07": (
        "# Python: не нужна явная декларация\ndef even(n): return n % 2 == 0",
        "bool even(int n);  // прототип\nbool even(int n) {\n    return n % 2 == 0;\n}",
        "boolean even(int n) {\n    return n % 2 == 0;\n}",
        "bool Even(int n) {\n    return n % 2 == 0;\n}",
    ),
    "fn_08": (
        "def outer():\n    def inner():  # вложенная разрешена в Python\n        pass",
        "// Вложенные функции запрещены в C++!\n// Используйте лямбды:\nauto inner = [](){ };",
        "// Java: вложенные классы вместо функций",
        "// C#: локальные функции разрешены\nvoid Outer() {\n    void Inner() { }\n}",
    ),
    "fn_09": (
        "def find(arr, target):\n    for i, x in enumerate(arr):\n        if x == target:\n            return i  # досрочный выход\n    return -1",
        "int find(int arr[], int n, int target) {\n    for (int i=0; i<n; i++)\n        if (arr[i]==target) return i;\n    return -1;\n}",
        "int find(int[] arr, int target) {\n    for (int i=0; i<arr.length; i++)\n        if (arr[i]==target) return i;\n    return -1;\n}",
        "int Find(int[] arr, int target) {\n    for (int i=0; i<arr.Length; i++)\n        if (arr[i]==target) return i;\n    return -1;\n}",
    ),
    "fn_11": (
        "# Python: не нужна forward declaration",
        "void helper();  // прототип вверху\nint main() {\n    helper();\n}\nvoid helper() { }",
        "// Java: нет forward declaration",
        "// C#: нет forward declaration",
    ),

    # ── 8. procedures ──────────────────────────────────────────────────────
    "prc_01": (
        "def greet(name: str) -> None:\n    print(f'Hello, {name}!')  # None = без возврата",
        "void greet(string name) {\n    cout << \"Hello, \" << name;\n}",
        "void greet(String name) {\n    System.out.println(\"Hello, \" + name);\n}",
        "void Greet(string name) {\n    Console.WriteLine($\"Hello, {name}!\");\n}",
    ),
    "prc_02": (
        "def swap(lst, i, j):\n    lst[i], lst[j] = lst[j], lst[i]",
        "void swap(int& a, int& b) {\n    int tmp=a; a=b; b=tmp;\n}",
        "void swap(int[] a, int i, int j) {\n    int tmp=a[i]; a[i]=a[j]; a[j]=tmp;\n}",
        "void Swap(ref int a, ref int b) {\n    int tmp=a; a=b; b=tmp;\n}",
    ),
    "prc_03": (
        "def compute(x: int, mult: int) -> int:\n    return x * mult  # mult не меняется",
        "int compute(int x, const int mult) {\n    return x * mult;\n}",
        "int compute(int x, final int mult) {\n    return x * mult;\n}",
        "int Compute(int x, int mult) {\n    return x * mult;\n}",
    ),
    "prc_05": (
        "def info(name: str, age: int = 0):\n    print(name, age)",
        "void info(string name, int age = 0) {\n    cout << name << \" \" << age;\n}",
        "void info(String name) { info(name, 0); }\nvoid info(String name, int age) { }",
        "void Info(string name, int age = 0) {\n    Console.WriteLine($\"{name} {age}\");\n}",
    ),
    "prc_06": (
        "def modify(data: list, v: int):\n    data.append(v)  # список изменяется",
        "void modify(int& x, int v) {\n    x = v;  // изменение по ссылке\n}",
        "void modify(int[] arr, int idx, int v) {\n    arr[idx] = v;\n}",
        "void Modify(ref int x, int v) {\n    x = v;\n}",
    ),
    "prc_07": (
        "def increment(values: list, step: int):\n    for i in range(len(values)):\n        values[i] += step",
        "void increment(int& x, int step) {\n    x += step;\n}",
        "void increment(int[] arr, int step) {\n    for (int i=0; i<arr.length; i++) arr[i]+=step;\n}",
        "void Increment(ref int x, int step) {\n    x += step;\n}",
    ),
    "prc_09": (
        "def helper():\n    print('help')\n\ndef main():\n    helper()  # helper до main\n\nmain()",
        "void helper() {  // объявление до main\n    cout << \"help\";\n}\nint main() {\n    helper();\n}",
        "// Java: порядок методов не важен",
        "// C#: порядок методов не важен",
    ),
    "prc_10": (
        "def print_doubled(n: int) -> None:\n    print(n * 2)",
        "void printDoubled(int n) {\n    cout << n * 2;\n}",
        "void printDoubled(int n) {\n    System.out.println(n * 2);\n}",
        "void PrintDoubled(int n) {\n    Console.WriteLine(n * 2);\n}",
    ),
    "prc_04": (
        "def sum_arr(arr: list) -> int:\n    return sum(arr)  # произвольная длина",
        "int sumArr(int arr[], int n) {\n    int s=0;\n    for (int i=0; i<n; i++) s+=arr[i];\n    return s;\n}",
        "int sumArr(int[] arr) {\n    int s=0;\n    for (int x : arr) s+=x;\n    return s;\n}",
        "int SumArr(int[] arr) {\n    return arr.Sum();\n}",
    ),
    "prc_08": (
        "def read_value() -> int:\n    return int(input())",
        "void readValue(int& result) {\n    cin >> result;  // out-параметр через &\n}",
        "int readValue(Scanner sc) {\n    return sc.nextInt();\n}",
        "void ReadValue(out int result) {\n    result = int.Parse(Console.ReadLine());\n}",
    ),
    "prc_12": (
        "def swap(a: int, b: int) -> tuple:\n    return b, a  # примитивы не изменяются!\n\nx, y = 1, 2\nx, y = swap(x, y)",
        "void swap(int& a, int& b) {  // & обязательна!\n    int tmp=a; a=b; b=tmp;\n}",
        "// Примитивы Java — по значению!\nvoid swapArr(int[] a, int i, int j) { }",
        "void Swap(ref int a, ref int b) {  // ref обязателен!\n    int tmp=a; a=b; b=tmp;\n}",
    ),
    "prc_13": (
        "def greet(name: str) -> None:\n    print(f'Hello, {name}!')\n\ngreet('Alice')  # вызов",
        "void greet(string name) {\n    cout << \"Hello, \" << name;\n}\ngreet(\"Alice\");",
        "void greet(String name) {\n    System.out.println(\"Hello, \" + name);\n}\ngreet(\"Alice\");",
        "void Greet(string name) {\n    Console.WriteLine($\"Hello, {name}!\");\n}\nGreet(\"Alice\");",
    ),

    # ── 9. static_arrays ───────────────────────────────────────────────────
    "arr_01": (
        "arr = [0] * 10  # массив из 10 элементов\narr[0] = 5     # индекс от 0",
        "int arr[10];\narr[0] = 5;  // индекс от 0",
        "int[] arr = new int[10];\narr[0] = 5;",
        "int[] arr = new int[10];\narr[0] = 5;",
    ),
    "arr_02": (
        "arr = [1, 2, 3, 4, 5]\nprint(len(arr))  # Length\nprint(arr[0])    # Low\nprint(arr[-1])   # High",
        "int arr[]={1,2,3,4,5};\nint n=sizeof(arr)/sizeof(arr[0]);\ncout << arr[0] << \" \" << arr[n-1];",
        "int[] arr={1,2,3,4,5};\nSystem.out.println(arr.length);\nSystem.out.println(arr[arr.length-1]);",
        "int[] arr={1,2,3,4,5};\nConsole.WriteLine(arr.Length);\nConsole.WriteLine(arr[arr.Length-1]);",
    ),
    "arr_03": (
        "arr = [10, 20, 30]\nprint(arr[0])  # первый: индекс 0",
        "int arr[]={10,20,30};\ncout << arr[0];  // первый: индекс 0",
        "int[] arr={10,20,30};\nSystem.out.println(arr[0]);",
        "int[] arr={10,20,30};\nConsole.WriteLine(arr[0]);",
    ),
    "arr_04": (
        "arr = [3, 1, 4, 1, 5]\nfor x in arr:\n    print(x)  # обход",
        "int arr[]={3,1,4,1,5};\nint n=sizeof(arr)/sizeof(arr[0]);\nfor (int i=0; i<n; i++) cout << arr[i];",
        "int[] arr={3,1,4,1,5};\nfor (int i=0; i<arr.length; i++)\n    System.out.println(arr[i]);",
        "int[] arr={3,1,4,1,5};\nfor (int i=0; i<arr.Length; i++)\n    Console.WriteLine(arr[i]);",
    ),
    "arr_05": (
        "matrix = [[0]*3 for _ in range(3)]\nmatrix[0][1] = 5  # 2D-массив",
        "int matrix[3][3] = {{0}};\nmatrix[0][1] = 5;",
        "int[][] matrix = new int[3][3];\nmatrix[0][1] = 5;",
        "int[,] matrix = new int[3,3];\nmatrix[0,1] = 5;",
    ),
    "arr_06": (
        "arr = [0] * 5  # объявление массива",
        "int arr[5];  // объявление",
        "int[] arr = new int[5];",
        "int[] arr = new int[5];",
    ),
    "arr_07": (
        "arr = [0] * 100  # фиксированная длина",
        "int arr[100];  // фиксированный размер",
        "int[] arr = new int[100];",
        "int[] arr = new int[100];",
    ),
    "arr_08": (
        "arr = [1, 2, 3, 4, 5]\ncopy = arr[1:4]  # Copy(a, 2, 3) → [2,3,4]",
        "vector<int> arr={1,2,3,4,5};\nvector<int> copy(arr.begin()+1, arr.begin()+4);",
        "int[] arr={1,2,3,4,5};\nint[] copy=Arrays.copyOfRange(arr, 1, 4);",
        "int[] arr={1,2,3,4,5};\nint[] copy=arr[1..4];",
    ),
    "arr_09": (
        "arr = [1, 2, 3]\n# arr[5]  # IndexError!\nif 0 <= 5 < len(arr):\n    print(arr[5])",
        "int arr[3]={1,2,3};\n// arr[5] — UB! Проверяйте: 0<=i<3",
        "int[] arr={1,2,3};\n// arr[5] — ArrayIndexOutOfBoundsException!",
        "int[] arr={1,2,3};\n// arr[5] — IndexOutOfRangeException!",
    ),

    # ── 10. dynamic_arrays ─────────────────────────────────────────────────
    "dyn_01": (
        "arr = []          # пустой список\narr = [0] * n     # с нужным размером\narr.append(x)     # добавить элемент",
        "vector<int> arr;\narr.resize(n);    // SetLength\narr.push_back(x); // добавить",
        "ArrayList<Integer> arr = new ArrayList<>();\nint[] arr2 = new int[n];",
        "List<int> arr = new List<int>();\nint[] arr2 = new int[n];",
    ),
    "dyn_05": (
        "arr = [0] * 5  # создать с размером 5\narr[2] = 42",
        "vector<int> arr(5, 0);  // аналог SetLength\narr[2] = 42;",
        "int[] arr = new int[5];\narr[2] = 42;",
        "int[] arr = new int[5];\narr[2] = 42;",
    ),
    "dyn_02": (
        "arr = [1, 2, 3]\nprint(len(arr))  # Length",
        "vector<int> arr={1,2,3};\ncout << arr.size();  // Length",
        "int[] arr={1,2,3};\nSystem.out.println(arr.length);",
        "int[] arr={1,2,3};\nConsole.WriteLine(arr.Length);",
    ),
    "dyn_03": (
        "arr = [1, 2, 3]\narr.append(4)  # добавить один элемент\nprint(len(arr))  # теперь 4",
        "vector<int> arr={1,2,3};\narr.push_back(4);\ncout << arr.size();",
        "ArrayList<Integer> arr = new ArrayList<>(Arrays.asList(1,2,3));\narr.add(4);\nSystem.out.println(arr.size());",
        "var arr = new List<int>{1,2,3};\narr.Add(4);\nConsole.WriteLine(arr.Count);",
    ),
    "dyn_04": (
        "arr = []\nfor i in range(5):\n    arr.append(i * 2)  # добавление",
        "vector<int> arr;\nfor (int i=0; i<5; i++)\n    arr.push_back(i*2);",
        "ArrayList<Integer> arr = new ArrayList<>();\nfor (int i=0; i<5; i++) arr.add(i*2);",
        "var arr = new List<int>();\nfor (int i=0; i<5; i++) arr.Add(i*2);",
    ),
    "dyn_06": (
        "arr = []  # начать с пустого",
        "vector<int> arr;  // пустой вектор",
        "ArrayList<Integer> arr = new ArrayList<>();",
        "var arr = new List<int>();",
    ),
    "dyn_07": (
        "arr = [1, 2, 3]\ndel arr  # Python — GC сам\narr = None",
        "vector<int>* arr = new vector<int>{1,2,3};\ndelete arr;  // Finalize",
        "// Java: GC автоматически\nint[] arr={1,2,3};\narr = null;",
        "// C#: GC автоматически\nint[] arr={1,2,3};\narr = null;",
    ),
    "dyn_08": (
        "arr = [1, 2, 3, 4, 5]\ncopy = arr[1:4]  # Copy(a, 2, 3)",
        "vector<int> arr={1,2,3,4,5};\nvector<int> copy(arr.begin()+1, arr.begin()+4);",
        "int[] arr={1,2,3,4,5};\nint[] copy=Arrays.copyOfRange(arr, 1, 4);",
        "int[] arr={1,2,3,4,5};\nint[] copy=arr[1..4];",
    ),
    "dyn_09": (
        "# В Python нет статических массивов\narr = []  # всегда динамический",
        "int staticArr[5];     // статический\nvector<int> dynArr;   // динамический",
        "int[] fixed = new int[5];\nArrayList<Integer> dynamic = new ArrayList<>();",
        "int[] fixed_ = new int[5];\nList<int> dynamic = new List<int>();",
    ),
    "dyn_10": (
        "arr = [1, 2, 3]\narr.append(4)\nprint(arr[-1])  # последний = arr[len-1]",
        "vector<int> arr={1,2,3};\narr.push_back(4);\ncout << arr.back();",
        "ArrayList<Integer> arr=new ArrayList<>(Arrays.asList(1,2,3));\narr.add(4);\nSystem.out.println(arr.get(arr.size()-1));",
        "var arr=new List<int>{1,2,3};\narr.Add(4);\nConsole.WriteLine(arr[arr.Count-1]);",
    ),
    "dyn_11": (
        "arr = []\nfor i in range(5):\n    arr.append(i)  # рост по одному",
        "vector<int> arr;\nfor (int i=0; i<5; i++) arr.push_back(i);",
        "ArrayList<Integer> arr=new ArrayList<>();\nfor (int i=0; i<5; i++) arr.add(i);",
        "var arr=new List<int>();\nfor (int i=0; i<5; i++) arr.Add(i);",
    ),

    # ── 11. strings ────────────────────────────────────────────────────────
    "str_01": (
        "s = 'Hello'\nprint(len(s))  # Length\nprint(s[0])    # первый (индекс 0)",
        "string s=\"Hello\";\ncout << s.length();\ncout << s[0];",
        "String s=\"Hello\";\nSystem.out.println(s.length());\nSystem.out.println(s.charAt(0));",
        "string s=\"Hello\";\nConsole.WriteLine(s.Length);\nConsole.WriteLine(s[0]);",
    ),
    "str_02": (
        "s = 'Hello'\nprint(s[0])  # первый: индекс 0 в Python",
        "string s=\"Hello\";\ncout << s[0];  // первый: индекс 0",
        "String s=\"Hello\";\nSystem.out.println(s.charAt(0));",
        "string s=\"Hello\";\nConsole.WriteLine(s[0]);",
    ),
    "str_03": (
        "s = 'Hello'\nprint(s[-1])       # последний\nprint(s[len(s)-1]) # или так",
        "string s=\"Hello\";\ncout << s[s.length()-1];  // последний",
        "String s=\"Hello\";\nSystem.out.println(s.charAt(s.length()-1));",
        "string s=\"Hello\";\nConsole.WriteLine(s[s.Length-1]);",
    ),
    "str_04": (
        "s = 'Hello, World!'\nsub = s[7:12]  # Copy(s, 8, 5)",
        "string s=\"Hello, World!\";\nstring sub=s.substr(7, 5);",
        "String s=\"Hello, World!\";\nString sub=s.substring(7, 12);",
        "string s=\"Hello, World!\";\nstring sub=s.Substring(7, 5);",
    ),
    "str_05": (
        "s1 = 'Hello'\ns2 = ', World!'\nresult = s1 + s2  # конкатенация",
        "string result = s1 + s2;",
        "String result = s1 + s2;",
        "string result = s1 + s2;",
    ),
    "lop_11": (
        "s = 'Hello'\nfor i in range(len(s)):\n    print(s[i])  # обход по индексам",
        "string s=\"Hello\";\nfor (int i=0; i<(int)s.length(); i++)\n    cout << s[i];",
        "String s=\"Hello\";\nfor (int i=0; i<s.length(); i++)\n    System.out.println(s.charAt(i));",
        "string s=\"Hello\";\nfor (int i=0; i<s.Length; i++)\n    Console.WriteLine(s[i]);",
    ),
    "str_07": (
        "s = 'Hello, World!'\npart = s[0:5]      # Copy\nresult = part + '!'  # Concat",
        "string part=s.substr(0,5);\nstring result=part+\"!\";",
        "String part=s.substring(0,5);\nString result=part+\"!\";",
        "string part=s.Substring(0,5);\nstring result=part+\"!\";",
    ),
    "str_09": (
        "s = 'Hello'\nfor i in range(len(s)):\n    print(s[i])  # 1..Length(s)",
        "string s=\"Hello\";\nfor (int i=0; i<(int)s.length(); i++)\n    cout << s[i];",
        "String s=\"Hello\";\nfor (int i=0; i<s.length(); i++)\n    System.out.println(s.charAt(i));",
        "string s=\"Hello\";\nfor (int i=0; i<s.Length; i++)\n    Console.WriteLine(s[i]);",
    ),

    # ── 12. records ────────────────────────────────────────────────────────
    "rec_01": (
        "from dataclasses import dataclass\n@dataclass\nclass Person:\n    name: str\n    age: int\n\np = Person('Alice', 30)",
        "struct Person {\n    string name;\n    int age;\n};\nPerson p = {\"Alice\", 30};",
        "class Person {\n    String name;\n    int age;\n}",
        "struct Person {\n    public string Name;\n    public int Age;\n}",
    ),
    "rec_02": (
        "p = Point()\nprint(p.x, p.y)  # прямой доступ к полям",
        "Point p = {1.0f, 2.0f};\ncout << p.x << \" \" << p.y;",
        "Point p = new Point();\nSystem.out.println(p.x+\" \"+p.y);",
        "Point p = new Point { X=1.0f, Y=2.0f };\nConsole.WriteLine($\"{p.X} {p.Y}\");",
    ),
    "rec_03": (
        "p = Point(1.0, 2.0)\np.x, p.y = p.y, p.x  # обмен полей",
        "swap(p.x, p.y);  // обмен полей",
        "float tmp=p.x; p.x=p.y; p.y=tmp;",
        "float tmp=p.X; p.X=p.Y; p.Y=tmp;",
    ),
    "rec_07": (
        "class Student:\n    name: str\n    grade: int\n    score: float",
        "struct Student {\n    string name;\n    int grade;\n    double score;\n};",
        "class Student {\n    String name;\n    int grade;\n    double score;\n}",
        "struct Student {\n    public string Name;\n    public int Grade;\n    public double Score;\n}",
    ),
    "rec_04": (
        "# Python: нет прямых указателей\ndata = [1, 2, 3]\nref = data  # ссылка",
        "int* p = nullptr;\np = new int(42);\ncout << *p;  // разыменование\ndelete p;",
        "// Java: нет указателей — только ссылки",
        "// C#: нет указателей в managed code",
    ),
    "rec_05": (
        "from typing import Union\nvalue: Union[int, str] = 42\nif isinstance(value, int):\n    print('int')",
        "union Data { int i; double d; char c; };\nData d; d.i = 42;",
        "Object value = 42;\nif (value instanceof Integer) { }",
        "object value = 42;\nif (value is int i) { Console.WriteLine(i); }",
    ),
    "rec_06": (
        "# Python: GC автоматически\nobj = SomeClass()\ndel obj",
        "int* p = new int(42);\ncout << *p;\ndelete p;  // New/Dispose",
        "// Java: GC управляет памятью",
        "using var obj = new SomeClass();  // IDisposable",
    ),
    "rec_10": (
        "class Outer:\n    x: int = 0\n    class Inner:\n        x: int = 0\n# Outer.x != Inner.x",
        "struct Inner { int x; };\nstruct Outer { Inner inner; int x; };\n// outer.x != outer.inner.x",
        "class Outer { int x; class Inner { int x; } }\n// outer.x != inner.x",
        "// C#: нет конфликта без with\nOuter outer = new Outer();",
    ),
    "rec_11": (
        "p = Point()\nprint(p.x, p.y)",
        "Point p = {1, 2};\ncout << p.x << \" \" << p.y;",
        "Point p = new Point();\nSystem.out.println(p.x+\" \"+p.y);",
        "Point p = new Point();\nConsole.WriteLine($\"{p.X} {p.Y}\");",
    ),

    # ── 13. files ──────────────────────────────────────────────────────────
    "fil_01": (
        "with open('data.txt', 'r') as f:\n    for line in f:\n        print(line.strip())",
        "#include <fstream>\nifstream f(\"data.txt\");\nstring line;\nwhile (getline(f, line)) cout << line;\nf.close();",
        "BufferedReader br=new BufferedReader(new FileReader(\"data.txt\"));\nString line;\nwhile ((line=br.readLine())!=null)\n    System.out.println(line);\nbr.close();",
        "using var sr=new StreamReader(\"data.txt\");\nstring? line;\nwhile ((line=sr.ReadLine())!=null)\n    Console.WriteLine(line);",
    ),
    "fil_02": (
        "with open('out.txt', 'w') as f:\n    f.write('Hello\\n')\n    f.write('World\\n')",
        "ofstream f(\"out.txt\");\nf << \"Hello\" << endl;\nf << \"World\" << endl;\nf.close();",
        "PrintWriter pw=new PrintWriter(new FileWriter(\"out.txt\"));\npw.println(\"Hello\");\npw.println(\"World\");\npw.close();",
        "using var sw=new StreamWriter(\"out.txt\");\nsw.WriteLine(\"Hello\");\nsw.WriteLine(\"World\");",
    ),
    "fil_03": (
        "# Python: with автоматически закрывает\nwith open('data.txt') as f:\n    data = f.read()\n# файл закрыт автоматически",
        "ifstream f(\"data.txt\");\nstring data;\ngetline(f, data);\nf.close();  // CloseFile!",
        "FileReader fr=new FileReader(\"data.txt\");\n// ...\nfr.close();  // обязательно!",
        "var sr=new StreamReader(\"data.txt\");\n// ...\nsr.Close();  // или using",
    ),
    "fil_04": (
        "with open('data.txt') as f:\n    for line in f:  # EOF автоматически\n        print(line.strip())",
        "ifstream f(\"data.txt\");\nstring line;\nwhile (!f.eof()) {  // not Eof(f)\n    getline(f, line);\n    cout << line;\n}",
        "while (!br.ready()) { }\nString line=br.readLine();",
        "while (!sr.EndOfStream) {\n    string line=sr.ReadLine();\n}",
    ),
    "fil_06": (
        "with open('log.txt', 'w') as f: f.write('x')  # Rewrite\nwith open('log.txt', 'a') as f: f.write('y')  # Append",
        "ofstream f;\nf.open(\"log.txt\");            // Rewrite\nf.open(\"log.txt\", ios::app);  // Append",
        "new FileWriter(\"log.txt\");           // Rewrite\nnew FileWriter(\"log.txt\", true);  // Append",
        "new StreamWriter(\"log.txt\");         // Rewrite\nnew StreamWriter(\"log.txt\", true); // Append",
    ),
    "fil_07": (
        "with open('data.txt', 'r') as f:\n    data = f.read()",
        "ifstream f;\nf.open(\"data.txt\");\nstring data;\ngetline(f, data);\nf.close();",
        "FileReader fr=new FileReader(\"data.txt\");\n// сразу готов к чтению",
        "var sr=new StreamReader(\"data.txt\");\n// сразу готов к чтению",
    ),
    "fil_08": (
        "with open('data.txt') as f:\n    for line in f:\n        print(line.strip())",
        "ifstream f(\"data.txt\");\nstring line;\nwhile (getline(f, line)) cout << line;\nf.close();",
        "BufferedReader br=new BufferedReader(new FileReader(\"data.txt\"));\nString line;\nwhile ((line=br.readLine())!=null)\n    System.out.println(line);\nbr.close();",
        "using var sr=new StreamReader(\"data.txt\");\nwhile (!sr.EndOfStream)\n    Console.WriteLine(sr.ReadLine());",
    ),

    # ── 14. units ──────────────────────────────────────────────────────────
    "unt_01": (
        "import math\nfrom os import path  # аналог uses",
        "#include <cmath>\n#include <string>  // аналог uses",
        "import java.util.Scanner;\nimport java.util.Arrays;",
        "using System;\nusing System.IO;",
    ),
    "unt_02": (
        "# Python: файл = модуль\n# Нет разделения interface/implementation",
        "// foo.h — interface (объявления)\n// foo.cpp — implementation (реализация)",
        "// Java: public члены = interface\n// реализация — в теле класса",
        "// C#: public члены = interface\n// реализация — в теле класса",
    ),
    "unt_03": (
        "import helper  # везде одинаково",
        "// В .cpp нужен отдельный #include\n#include \"helper.h\"",
        "// import в каждом файле отдельно",
        "// using в каждом файле отдельно",
    ),
    "unt_04": (
        "__all__ = ['helper']  # публичный интерфейс\ndef helper(): pass",
        "// foo.h (interface):\nvoid helper();\n// foo.cpp (implementation):\nvoid helper() { }",
        "public void helper() { }  // public = экспорт",
        "public void Helper() { }  // public = экспорт",
    ),
    "unt_05": (
        "# Python: if __name__ == '__main__': — аналог initialization",
        "// C++: статические объекты при загрузке",
        "static { System.out.println(\"init\"); }  // static блок",
        "static MyClass() { /* static constructor */ }",
    ),
    "unt_06": (
        "# Python: ImportError при круговом импорте",
        "// Circular: #pragma once + forward declaration",
        "// Java: нет проблемы, но плохой дизайн",
        "// C#: нет проблемы, но плохой дизайн",
    ),
    "unt_07": (
        "# Python: нет разделения\n# _private или public",
        "// .h — interface\n// .cpp — implementation",
        "// public = interface\n// private = implementation",
        "// public = interface\n// private = implementation",
    ),
    "unt_08": (
        "__all__ = ['func1', 'Class1']",
        "// foo.h:\nvoid func1();\nclass Class1 { };",
        "public interface MyUnit {\n    void func1();\n}",
        "public interface IMyUnit {\n    void Func1();\n}",
    ),
    "unt_09": (
        "import math  # правильное имя\n# import mathh  # ModuleNotFoundError",
        "#include <cmath>  // правильно\n// #include <mathh>  // ошибка",
        "import java.util.Scanner;\n// import java.util.Scannner;  // ошибка",
        "using System;\n// using Systemm;  // ошибка",
    ),
    "unt_11": (
        "def my_function():\n    return 42  # реализация в модуле",
        "// foo.cpp:\n#include \"foo.h\"\nvoid myFunction() {\n    // реализация\n}",
        "class MyClass implements MyInterface {\n    public void myFunction() {\n        // реализация\n    }\n}",
        "class MyClass : IMyInterface {\n    public void MyFunction() {\n        // реализация\n    }\n}",
    ),
    "unt_13": (
        "__all__ = ['public_func']\ndef public_func():\n    return _private()\ndef _private():\n    return 42",
        "// foo.h:\nvoid publicFunc();\n// foo.cpp:\nvoid publicFunc() { privateHelper(); }\nvoid privateHelper() { }",
        "public class MyModule {\n    public static void publicFunc() {\n        privateHelper();\n    }\n    private static void privateHelper() { }\n}",
        "public class MyModule {\n    public static void PublicFunc() { PrivateHelper(); }\n    private static void PrivateHelper() { }\n}",
    ),

    # ── 15. recursion ──────────────────────────────────────────────────────
    "rcu_01": (
        "def factorial(n: int) -> int:\n    if n <= 1: return 1\n    return n * factorial(n - 1)",
        "int factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}",
        "int factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}",
        "int Factorial(int n) {\n    if (n <= 1) return 1;\n    return n * Factorial(n-1);\n}",
    ),
    "rcu_02": (
        "def fib(n: int) -> int:\n    if n <= 1: return n  # базовый случай!\n    return fib(n-1) + fib(n-2)",
        "int fib(int n) {\n    if (n <= 1) return n;  // базовый случай!\n    return fib(n-1) + fib(n-2);\n}",
        "int fib(int n) {\n    if (n <= 1) return n;  // базовый случай!\n    return fib(n-1) + fib(n-2);\n}",
        "int Fib(int n) {\n    if (n <= 1) return n;\n    return Fib(n-1) + Fib(n-2);\n}",
    ),
    "rcu_03": (
        "def isEven(n):\n    if n == 0: return True\n    return isOdd(n-1)\ndef isOdd(n):\n    if n == 0: return False\n    return isEven(n-1)",
        "bool isOdd(int n);\nbool isEven(int n) {\n    if (n==0) return true;\n    return isOdd(n-1);\n}\nbool isOdd(int n) {\n    if (n==0) return false;\n    return isEven(n-1);\n}",
        "boolean isEven(int n) {\n    if (n==0) return true;\n    return isOdd(n-1);\n}\nboolean isOdd(int n) {\n    if (n==0) return false;\n    return isEven(n-1);\n}",
        "bool IsEven(int n) {\n    if (n==0) return true;\n    return IsOdd(n-1);\n}\nbool IsOdd(int n) {\n    if (n==0) return false;\n    return IsEven(n-1);\n}",
    ),
    "rcu_04": (
        "def countdown(n: int):\n    print(n)\n    countdown(n-1)  # нет базового случая → бесконечная рекурсия!",
        "void countdown(int n) {\n    cout << n;\n    countdown(n-1);  // StackOverflow!\n}",
        "void countdown(int n) {\n    System.out.println(n);\n    countdown(n-1);  // StackOverflow!\n}",
        "void Countdown(int n) {\n    Console.WriteLine(n);\n    Countdown(n-1);  // StackOverflow!\n}",
    ),
    "rcu_06": (
        "# Python: не нужна forward declaration",
        "void helper();  // объявлено\n// Без реализации → linker error!\nvoid helper() { }  // реализация обязательна",
        "// Java: нет проблемы",
        "// C#: нет проблемы",
    ),
    "rcu_07": (
        "def power(base: int, exp: int) -> int:\n    if exp == 0: return 1\n    return base * power(base, exp-1)",
        "int power(int base, int exp) {\n    if (exp==0) return 1;\n    return base * power(base, exp-1);\n}",
        "int power(int base, int exp) {\n    if (exp==0) return 1;\n    return base * power(base, exp-1);\n}",
        "int Power(int b, int exp) {\n    if (exp==0) return 1;\n    return b * Power(b, exp-1);\n}",
    ),

    # ── 16. oop ────────────────────────────────────────────────────────────
    "oop_01": (
        "class Animal:\n    def __init__(self, name: str):\n        self.name = name\n    def speak(self) -> str:\n        return 'Some sound'",
        "class Animal {\npublic:\n    string name;\n    Animal(string n): name(n) {}\n    virtual string speak() { return \"...\"; }\n};",
        "class Animal {\n    String name;\n    Animal(String n) { this.name=n; }\n    String speak() { return \"...\"; }\n}",
        "class Animal {\n    public string Name;\n    public Animal(string n) { Name=n; }\n    public virtual string Speak() { return \"...\"; }\n}",
    ),
    "oop_02": (
        "class Person:\n    def __init__(self, name: str, age: int):\n        self.name = name\n        self.age = age",
        "class Person {\npublic:\n    string name; int age;\n    Person(string n, int a): name(n), age(a) {}\n};",
        "class Person {\n    String name; int age;\n    Person(String n, int a) { this.name=n; this.age=a; }\n}",
        "class Person {\n    public string Name; public int Age;\n    public Person(string n, int a) { Name=n; Age=a; }\n}",
    ),
    "oop_03": (
        "class Resource:\n    def __del__(self):\n        self._close()  # деструктор",
        "class Resource {\npublic:\n    Resource() { }\n    ~Resource() { }  // деструктор\n};",
        "class Resource implements AutoCloseable {\n    public void close() { }  // финализация\n}",
        "class Resource : IDisposable {\n    public void Dispose() { }  // деструктор\n}",
    ),
    "oop_04": (
        "class Child(Parent):\n    def __init__(self):\n        super().__init__()  # inherited",
        "class Child : public Parent {\npublic:\n    Child() : Parent() { }  // inherited\n};",
        "class Child extends Parent {\n    Child() {\n        super();  // inherited\n    }\n}",
        "class Child : Parent {\n    public Child() : base() { }  // inherited\n}",
    ),
    "oop_13": (
        "class MyClass:\n    field1: int\n    field2: str\n    def method(self): pass",
        "class MyClass {\npublic:\n    int field1;\n    string field2;\n    void method();\n};",
        "class MyClass {\n    int field1;\n    String field2;\n    void method() {}\n}",
        "class MyClass {\n    public int Field1;\n    public string Field2;\n    public void Method() {}\n}",
    ),
    "oop_05": (
        "class Base:\n    def method(self): pass\nclass Child(Base):\n    def method(self):\n        super().method()",
        "class Base {\npublic:\n    virtual void method() { }  // virtual!\n};\nclass Child : public Base {\npublic:\n    void method() override { }\n};",
        "class Base { void method() { } }\nclass Child extends Base {\n    @Override\n    void method() { }\n}",
        "class Base {\n    public virtual void Method() { }  // virtual!\n}\nclass Child : Base {\n    public override void Method() { }  // override\n}",
    ),
    "oop_06": (
        "class Shape:\n    def area(self) -> float:\n        raise NotImplementedError\nclass Circle(Shape):\n    def area(self) -> float:\n        return 3.14 * self.r * self.r",
        "class Shape {\npublic:\n    virtual double area() = 0;\n};\nclass Circle : public Shape {\npublic:\n    double area() override { return 3.14*r*r; }\n};",
        "abstract class Shape { abstract double area(); }\nclass Circle extends Shape {\n    double area() { return 3.14*r*r; }\n}",
        "abstract class Shape { public abstract double Area(); }\nclass Circle : Shape {\n    public override double Area() { return 3.14*r*r; }\n}",
    ),
    "oop_07": (
        "class Person:\n    @property\n    def name(self) -> str: return self._name\n    @name.setter\n    def name(self, v: str): self._name = v",
        "class Person {\n    string _name;\npublic:\n    string getName() { return _name; }\n    void setName(string n) { _name=n; }\n};",
        "class Person {\n    private String _name;\n    public String getName() { return _name; }\n    public void setName(String n) { _name=n; }\n}",
        "class Person {\n    private string _name;\n    public string Name {\n        get { return _name; }\n        set { _name = value; }\n    }\n}",
    ),
    "oop_08": (
        "class Rectangle:\n    def __init__(self):\n        self._width = 0\n    @property\n    def width(self): return self._width\n    @width.setter\n    def width(self, v): self._width = max(0, v)",
        "class Rectangle {\n    int _width=0;\npublic:\n    int getWidth() { return _width; }\n    void setWidth(int w) { _width=max(0,w); }\n};",
        "class Rectangle {\n    private int _width=0;\n    public int getWidth() { return _width; }\n    public void setWidth(int w) { _width=Math.max(0,w); }\n}",
        "class Rectangle {\n    private int _width=0;\n    public int Width {\n        get { return _width; }\n        set { _width=Math.Max(0,value); }\n    }\n}",
    ),
    "oop_09": (
        "class Counter:\n    count = 0\n    def increment(self): self.count += 1\n    def get(self) -> int: return self.count",
        "class Counter {\n    int count=0;\npublic:\n    void increment() { count++; }\n    int get() { return count; }\n};",
        "class Counter {\n    private int count=0;\n    public void increment() { count++; }\n    public int get() { return count; }\n}",
        "class Counter {\n    private int count=0;\n    public void Increment() { count++; }\n    public int Get() { return count; }\n}",
    ),
    "oop_11": (
        "class Animal: pass\nclass Dog(Animal): pass\na: Animal = Dog()  # OK\n# b: Dog = Animal()  # TypeError!",
        "Animal* a = new Dog();   // OK (upcasting)\n// Dog* d = new Animal();  // ошибка типов!",
        "Animal a = new Dog();   // OK\n// Dog d = new Animal();  // ошибка типов!",
        "Animal a = new Dog();   // OK\n// Dog d = new Animal();  // ошибка типов!",
    ),
    "oop_14": (
        "from abc import ABC, abstractmethod\nclass Printable(ABC):\n    @abstractmethod\n    def print(self): pass",
        "class IPrintable {\npublic:\n    virtual void print() = 0;  // pure virtual\n};",
        "interface Printable {\n    void print();\n}",
        "interface IPrintable {\n    void Print();\n}",
    ),
    "oop_15": (
        "class Child(Parent):\n    def method(self):\n        super().method()  # inherited\n        # доп. логика",
        "class Child : public Parent {\npublic:\n    void method() override {\n        Parent::method();  // inherited\n    }\n};",
        "class Child extends Parent {\n    @Override\n    void method() {\n        super.method();  // inherited\n    }\n}",
        "class Child : Parent {\n    public override void Method() {\n        base.Method();  // inherited\n    }\n}",
    ),
    "oop_16": (
        "class MyClass:\n    def __init__(self):\n        self.value = 0\n    def set_value(self, v: int):\n        self.value = v  # self = Self",
        "class MyClass {\n    int value=0;\npublic:\n    void setValue(int v) {\n        this->value=v;  // this = Self\n    }\n};",
        "class MyClass {\n    int value=0;\n    void setValue(int v) {\n        this.value=v;  // this = Self\n    }\n}",
        "class MyClass {\n    int value=0;\n    void SetValue(int v) {\n        this.value=v;  // this = Self\n    }\n}",
    ),
    "oop_17": (
        "class Shape:\n    def __init__(self, color: str):\n        self.color = color\nclass Circle(Shape):\n    def __init__(self, color: str, r: float):\n        super().__init__(color)\n        self.r = r",
        "class Shape {\npublic:\n    string color;\n    Shape(string c): color(c) {}\n};\nclass Circle : public Shape {\npublic:\n    double r;\n    Circle(string c, double r): Shape(c), r(r) {}\n};",
        "class Shape { String color; Shape(String c){this.color=c;} }\nclass Circle extends Shape {\n    double r;\n    Circle(String c, double r) { super(c); this.r=r; }\n}",
        "class Shape { public string Color; public Shape(string c){Color=c;} }\nclass Circle : Shape {\n    public double R;\n    public Circle(string c, double r): base(c) { R=r; }\n}",
    ),
    "oop_18": (
        "class Temperature:\n    def __init__(self):\n        self._celsius = 0.0\n    @property\n    def celsius(self): return self._celsius\n    @celsius.setter\n    def celsius(self, v):\n        if v >= -273.15: self._celsius = v",
        "class Temperature {\n    double _celsius=0;\npublic:\n    double getCelsius() { return _celsius; }\n    void setCelsius(double v) {\n        if (v>=-273.15) _celsius=v;\n    }\n};",
        "class Temperature {\n    private double celsius=0;\n    public double getCelsius() { return celsius; }\n    public void setCelsius(double v) {\n        if (v>=-273.15) celsius=v;\n    }\n}",
        "class Temperature {\n    private double _celsius=0;\n    public double Celsius {\n        get { return _celsius; }\n        set { if (value>=-273.15) _celsius=value; }\n    }\n}",
    ),

    # ── 17. pascal_pitfalls ────────────────────────────────────────────────
    "pit_01": (
        "if x > 0:\n    print('yes')\nelse:\n    print('no')  # нет ; перед else",
        "if (x > 0) {\n    cout << \"yes\";\n}  // НЕТ ; перед else!\nelse {\n    cout << \"no\";\n}",
        "if (x > 0) {\n    System.out.println(\"yes\");\n} else {\n    System.out.println(\"no\");\n}",
        "if (x > 0) {\n    Console.WriteLine(\"yes\");\n} else {\n    Console.WriteLine(\"no\");\n}",
    ),
    "pit_02": (
        "ptr = None\nif ptr is not None:\n    print(ptr.value)  # проверка nil",
        "int* ptr = nullptr;\nif (ptr != nullptr) {\n    cout << *ptr;\n}",
        "Object obj = null;\nif (obj != null) {\n    System.out.println(obj);\n}",
        "object obj = null;\nif (obj != null) {\n    Console.WriteLine(obj);\n}",
    ),
    "pit_03": (
        "s = 'Hello'\nprint(s[0])  # первый: индекс 0\n# s[0] Python = s[1] Pascal",
        "string s=\"Hello\";\ncout << s[0];  // первый: индекс 0",
        "String s=\"Hello\";\nSystem.out.println(s.charAt(0));",
        "string s=\"Hello\";\nConsole.WriteLine(s[0]);",
    ),
    "pit_04": (
        "for i in range(10):\n    # i = 5  # не рекомендуется!\n    print(i)",
        "for (int i=0; i<10; i++) {\n    // i=5; — предупреждение!\n    cout << i;\n}",
        "for (int i=0; i<10; i++) {\n    System.out.println(i);\n}",
        "for (int i=0; i<10; i++) {\n    Console.WriteLine(i);\n}",
    ),
    "pit_05": (
        "day = 3\nif day == 1: print('Mon')\nelif day == 2: print('Tue')\nelse: print('Other')  # else важен!",
        "switch (day) {\n  case 1: cout<<\"Mon\"; break;\n  default: cout<<\"Other\";  // default важен!\n}",
        "switch (day) {\n  case 1: System.out.println(\"Mon\"); break;\n  default: System.out.println(\"Other\");\n}",
        "switch (day) {\n  case 1: Console.WriteLine(\"Mon\"); break;\n  default: Console.WriteLine(\"Other\"); break;\n}",
    ),
    "pit_07": (
        "# Python: имя файла = имя модуля\n# math.py → import math",
        "// C++: #include = имя файла\n// mymath.h → #include \"mymath.h\"",
        "// Java: имя файла = имя public класса\n// MyClass.java → public class MyClass { }",
        "// C#: рекомендуется имя файла = имя класса",
    ),
    "pit_08": (
        "def get(x: int) -> int:\n    result = 0  # инициализировать Result!\n    if x > 0: result = x\n    return result",
        "int get(int x) {\n    int result=0;  // инициализировать!\n    if (x>0) result=x;\n    return result;\n}",
        "int get(int x) {\n    int result=0;\n    if (x>0) result=x;\n    return result;\n}",
        "int Get(int x) {\n    int result=0;\n    if (x>0) result=x;\n    return result;\n}",
    ),
    "pit_09": (
        "arr = [0] * n  # выделить сразу нужный размер\nfor i in range(n):\n    arr[i] = i",
        "vector<int> arr;\narr.resize(n);  // resize один раз!\nfor (int i=0; i<n; i++) arr[i]=i;",
        "int[] arr = new int[n];\nfor (int i=0; i<n; i++) arr[i]=i;",
        "int[] arr = new int[n];\nfor (int i=0; i<n; i++) arr[i]=i;",
    ),
    "pit_10": (
        "p = Point()\np.x = 1\np.y = 2  # нет конфликта без with",
        "Point p = {1, 2};\ncout << p.x << p.y;",
        "Point p = new Point();\np.x=1; p.y=2;",
        "Point p = new Point();\np.X=1; p.Y=2;",
    ),
    "pit_11": (
        "# Python: конец файла = конец программы",
        "int main() {\n    return 0;  // нет . после }\n}",
        "public static void main(String[] args) {\n}  // нет . после }",
        "static void Main() {\n}  // нет . после }",
    ),
    "pit_12": (
        "if x > 0:\n    y = x      # блок через отступ\n    z = y + 1  # оба в блоке if",
        "if (x > 0) {\n    y=x;\n    z=y+1;\n}  // begin/end через { }",
        "if (x > 0) {\n    y=x;\n    z=y+1;\n}",
        "if (x > 0) {\n    y=x;\n    z=y+1;\n}",
    ),
    "pit_13": (
        "# Python: нет interface/implementation",
        "// .h: только объявления!\n// void foo() { }  // ошибка в .h!",
        "interface IFoo {\n    void foo();  // только объявление!\n}",
        "interface IFoo {\n    void Foo();  // только объявление!\n}",
    ),
    "pit_14": (
        "# Python: GC автоматически\nobj = SomeClass()\ndel obj  # подсказка GC",
        "int* p = new int(42);\ncout << *p;\ndelete p;  // Dispose обязателен!",
        "// Java: GC управляет памятью",
        "using var obj = new SomeClass();  // IDisposable",
    ),
    "pit_15": (
        "arr = [1,2,3,4,5]\nfor i in range(len(arr)):  # Low=0, High=len-1\n    print(arr[i])",
        "int n=sizeof(arr)/sizeof(arr[0]);\nfor (int i=0; i<n; i++)  // Low=0, High=n-1\n    cout << arr[i];",
        "for (int i=0; i<arr.length; i++)\n    System.out.println(arr[i]);",
        "for (int i=0; i<arr.Length; i++)\n    Console.WriteLine(arr[i]);",
    ),
    "pit_16": (
        "def swap(lst, i, j):\n    lst[i], lst[j] = lst[j], lst[i]",
        "void swap(int& a, int& b) {  // & обязательна!\n    int tmp=a; a=b; b=tmp;\n}",
        "// Java: примитивы по значению!\nvoid swapInArray(int[] a, int i, int j) { }",
        "void Swap(ref int a, ref int b) {  // ref!\n    int tmp=a; a=b; b=tmp;\n}",
    ),
    "pit_17": (
        "def compute(x: int) -> int:\n    return x * x  # return, а не side effect",
        "int compute(int x) {\n    return x * x;\n}",
        "int compute(int x) {\n    return x * x;\n}",
        "int Compute(int x) {\n    return x * x;\n}",
    ),
    "pit_18": (
        "arr = []\narr.append(42)\nprint(arr[-1])  # последний = arr[len-1]",
        "vector<int> arr;\narr.push_back(42);\ncout << arr.back();",
        "ArrayList<Integer> arr=new ArrayList<>();\narr.add(42);\nSystem.out.println(arr.get(arr.size()-1));",
        "var arr=new List<int>();\narr.Add(42);\nConsole.WriteLine(arr[arr.Count-1]);",
    ),
    "pit_19": (
        "class Outer:\n    x = 0\n    class Inner:\n        x = 0\n# Outer.x != Inner.x",
        "struct Outer { Inner inner; int x; };\n// outer.x != outer.inner.x",
        "// Java: нет конфликта без with",
        "// C#: нет конфликта без with",
    ),
    "pit_21": (
        "def compute(x: int) -> int:\n    return x * 2  # функция — есть возврат\n\ndef print_r(x: int) -> None:\n    print(x)  # процедура — нет возврата",
        "int compute(int x) { return x*2; }  // function\nvoid printR(int x) { cout<<x; }  // procedure",
        "int compute(int x) { return x*2; }\nvoid printR(int x) { System.out.println(x); }",
        "int Compute(int x) { return x*2; }\nvoid PrintR(int x) { Console.WriteLine(x); }",
    ),
    "pit_22": (
        "# Python: нет статических массивов\narr = []  # всегда динамический",
        "int arr[10];      // статический\nvector<int> dynArr;  // динамический",
        "int[] fixed=new int[10];\nArrayList<Integer> dynamic=new ArrayList<>();",
        "int[] fixed_=new int[10];\nList<int> dynamic=new List<int>();",
    ),
    "pit_23": (
        "while True:\n    n = int(input())\n    if n > 0:  # условие ВЫХОДА\n        break",
        "int n;\ndo {\n    cin >> n;\n} while (n <= 0);  // условие ПРОДОЛЖЕНИЯ",
        "int n;\ndo {\n    n=sc.nextInt();\n} while (n <= 0);",
        "int n;\ndo {\n    n=int.Parse(Console.ReadLine());\n} while (n <= 0);",
    ),
    "pit_24": (
        "class Rectangle:\n    def __init__(self):\n        self._width = 0  # backing field!\n    @property\n    def width(self): return self._width",
        "class Rectangle {\n    int _width=0;  // backing field!\npublic:\n    int getWidth() { return _width; }\n};",
        "class Rectangle {\n    private int _width=0;  // backing field!\n    public int getWidth() { return _width; }\n}",
        "class Rectangle {\n    private int _width=0;  // backing field!\n    public int Width { get { return _width; } }\n}",
    ),

    # ── 18. compiler_diagnostics ───────────────────────────────────────────
    "cdg_01": (
        "x = 5  # объявить перед использованием\nprint(x)",
        "int x=5;  // объявить в секции var!\ncout << x;",
        "int x=5;  // объявить перед использованием!\nSystem.out.println(x);",
        "int x=5;  // объявить перед использованием!\nConsole.WriteLine(x);",
    ),
    "cdg_02": (
        "x: int = 5\ny: float = float(x)  # явное приведение",
        "int x=5;\ndouble y=(double)x;  // явное приведение",
        "int x=5;\ndouble y=(double)x;",
        "int x=5;\ndouble y=(double)x;",
    ),
    "cdg_03": (
        "def add(a: int, b: int) -> int:\n    return a + b\nadd(1, 2)  # правильно\n# add(1, 'a')  # TypeError!",
        "void process(int x) { cout<<x; }\nprocess(42);     // правильно\n// process(3.14);  // ошибка типа",
        "void process(int x) { System.out.println(x); }\nprocess(42);\n// process(3.14);  // ошибка",
        "void Process(int x) { Console.WriteLine(x); }\nProcess(42);\n// Process(3.14);  // ошибка",
    ),
    "cdg_04": (
        "if x > 0:\n    print('yes')  # отступ = begin",
        "if (x > 0) {\n    cout << \"yes\";\n}  // { } обязательны",
        "if (x > 0) {\n    System.out.println(\"yes\");\n}",
        "if (x > 0) {\n    Console.WriteLine(\"yes\");\n}",
    ),
    "cdg_05": (
        "if x > 0:\n    print('yes')\n# конец блока — через отступ",
        "if (x > 0) {\n    cout << \"yes\";\n}  // } = end",
        "if (x > 0) {\n    System.out.println(\"yes\");\n}",
        "if (x > 0) {\n    Console.WriteLine(\"yes\");\n}",
    ),
    "cdg_06": (
        "x = 5\ny = 10\nz = x + y  # нет разделителей в Python",
        "int x=5;\nint y=10;  // ; между операторами\nint z=x+y;",
        "int x=5;\nint y=10;  // ; обязательна\nint z=x+y;",
        "int x=5;\nint y=10;  // ; обязательна\nint z=x+y;",
    ),
    "cdg_07": (
        "x: int = 0  # объявление с типом",
        "int x=0;  // объявление с типом",
        "int x=0;",
        "int x=0;",
    ),
    "cdg_08": (
        "# SyntaxError показывает место ошибки",
        "// Компилятор показывает строку ошибки\nint x = 1 +;  // ошибка синтаксиса",
        "// Компилятор показывает ошибку\nint x = 1 +;",
        "// Компилятор показывает ошибку\nint x = 1 +;",
    ),
    "cdg_09": (
        "class Animal: pass\nclass Dog(Animal): pass\na: Animal = Dog()   # OK\n# d: Dog = Animal()  # TypeError!",
        "Animal* a = new Dog();   // OK\n// Dog* d = new Animal();  // ошибка!",
        "Animal a = new Dog();   // OK\n// Dog d = new Animal();  // ошибка!",
        "Animal a = new Dog();   // OK\n// Dog d = new Animal();  // ошибка!",
    ),
    "cdg_10": (
        "# Python: нет forward declaration",
        "void helper();  // объявлено\nvoid helper() { }  // реализация обязательна!",
        "// Java: нет forward declaration",
        "// C#: нет forward declaration",
    ),
    "cdg_11": (
        "def add(a: int, b: int) -> int:\n    return a + b  # return в функции",
        "int add(int a, int b) {\n    return a + b;  // return только в функции!\n}",
        "int add(int a, int b) {\n    return a + b;\n}",
        "int Add(int a, int b) {\n    return a + b;\n}",
    ),
    "cdg_12": (
        "class Base:\n    def method(self): pass\nclass Child(Base):\n    def method(self):\n        super().method()",
        "class Base {\npublic:\n    virtual void method() {}  // virtual!\n};\nclass Child : public Base {\npublic:\n    void method() override {}\n};",
        "class Base { void method() {} }\nclass Child extends Base {\n    @Override\n    void method() {}\n}",
        "class Base {\n    public virtual void Method() {}\n}\nclass Child : Base {\n    public override void Method() {}\n}",
    ),
    "cdg_13": (
        "import math  # правильное имя\n# import mathh  # ModuleNotFoundError",
        "#include <cmath>  // правильно\n// #include <mathh>  // ошибка",
        "import java.util.Scanner;\n// import java.util.Scannner;  // ошибка",
        "using System;\n// using Systemm;  // ошибка",
    ),
    "cdg_14": (
        "for i in range(1, 11):  # правильный заголовок\n    print(i)",
        "for (int i=1; i<=10; i++) {\n    cout << i;\n}",
        "for (int i=1; i<=10; i++) {\n    System.out.println(i);\n}",
        "for (int i=1; i<=10; i++) {\n    Console.WriteLine(i);\n}",
    ),
    "cdg_15": (
        "arr = [1,2,3]\n# arr[5]  # IndexError!\nif 0 <= 5 < len(arr):\n    print(arr[5])",
        "int arr[3]={1,2,3};\n// arr[5] — UB! Проверяйте: 0<=i<3",
        "int[] arr={1,2,3};\n// arr[5] — ArrayIndexOutOfBoundsException!",
        "int[] arr={1,2,3};\n// arr[5] — IndexOutOfRangeException!",
    ),
    "cdg_16": (
        "class Person:\n    name: str = 'Alice'\np = Person()\nprint(p.name)",
        "class Person {\npublic:\n    string name=\"Alice\";\n};\nPerson p;\ncout << p.name;",
        "class Person {\n    public String name=\"Alice\";\n}\nPerson p=new Person();\nSystem.out.println(p.name);",
        "class Person {\n    public string Name=\"Alice\";\n}\nPerson p=new Person();\nConsole.WriteLine(p.Name);",
    ),
}


from application.curriculum.pascal.catalog.pascal_v32_delta_content import V32_KNOWN_CODE

_C.update(V32_KNOWN_CODE)
_C.update(
    __import__(
        "application.curriculum.pascal.catalog.pascal_v311_capstone_catalog",
        fromlist=["capstone_known_code"],
    ).capstone_known_code()
)


def get_known_code(slot_id: str) -> tuple[str, str, str, str] | None:
    """Return (python, cpp, java, csharp) for *slot_id*, or None if not found."""
    result = _C.get(slot_id)
    if result is not None:
        return result
    # For v4 slots (pas_NNN / py_NNN / cpp_NNN), look up from the v4 reference code file.
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code
        py = get_reference_code(slot_id, "python")
        cpp = get_reference_code(slot_id, "cpp")
        java = get_reference_code(slot_id, "java")
        csharp = get_reference_code(slot_id, "csharp")
        if any([py, cpp, java, csharp]):
            return (py, cpp, java, csharp)
    except ImportError:
        pass
    return None
