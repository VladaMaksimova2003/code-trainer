"""Batch 4 overrides: task_012 date validation, task_020 sum until zero."""

T012_TITLE = "Проверка корректности даты"
T012_DESC = (
    "Даны день, месяц и год. Проверьте, является ли дата корректной, "
    "и выведите valid или invalid."
)
T012_TESTS = [
    {"name": "Тест 1", "inputs": "29 2 2024\n", "output": "valid"},
    {"name": "Тест 2", "inputs": "31 4 2023\n", "output": "invalid"},
    {"name": "Тест 3", "inputs": "15 13 2023\n", "output": "invalid"},
    {"name": "Тест 4", "inputs": "29 2 2020\n", "output": "valid"},
]

T012_REF = {
    "pascal": """var d, m, y, maxDay: integer;
    leap: boolean;
begin
  readln(d, m, y);

  leap := ((y mod 400 = 0) or ((y mod 4 = 0) and (y mod 100 <> 0)));

  if (m < 1) or (m > 12) or (y < 1) then
    writeln('invalid')
  else
  begin
    if (m = 1) or (m = 3) or (m = 5) or (m = 7) or (m = 8) or (m = 10) or (m = 12) then
      maxDay := 31
    else if (m = 4) or (m = 6) or (m = 9) or (m = 11) then
      maxDay := 30
    else if leap then
      maxDay := 29
    else
      maxDay := 28;

    if (d >= 1) and (d <= maxDay) then
      writeln('valid')
    else
      writeln('invalid');
  end;
end.""",
    "python": """d, m, y = map(int, input().split())

leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)

if m < 1 or m > 12 or y < 1:
    print('invalid')
else:
    if m in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif m in (4, 6, 9, 11):
        max_day = 30
    elif leap:
        max_day = 29
    else:
        max_day = 28

    if 1 <= d <= max_day:
        print('valid')
    else:
        print('invalid')""",
    "cpp": """#include <iostream>

int main() {
    int d, m, y;
    std::cin >> d >> m >> y;

    bool leap = (y % 400 == 0) || (y % 4 == 0 && y % 100 != 0);

    if (m < 1 || m > 12 || y < 1) {
        std::cout << "invalid";
    } else {
        int maxDay;

        if (m == 1 || m == 3 || m == 5 || m == 7 || m == 8 || m == 10 || m == 12) {
            maxDay = 31;
        } else if (m == 4 || m == 6 || m == 9 || m == 11) {
            maxDay = 30;
        } else if (leap) {
            maxDay = 29;
        } else {
            maxDay = 28;
        }

        if (d >= 1 && d <= maxDay) {
            std::cout << "valid";
        } else {
            std::cout << "invalid";
        }
    }

    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        string[] p = Console.ReadLine().Split();

        int d = int.Parse(p[0]);
        int m = int.Parse(p[1]);
        int y = int.Parse(p[2]);

        bool leap = y % 400 == 0 || (y % 4 == 0 && y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            Console.WriteLine("invalid");
        } else {
            int maxDay;

            if (m == 1 || m == 3 || m == 5 || m == 7 || m == 8 || m == 10 || m == 12) {
                maxDay = 31;
            } else if (m == 4 || m == 6 || m == 9 || m == 11) {
                maxDay = 30;
            } else if (leap) {
                maxDay = 29;
            } else {
                maxDay = 28;
            }

            if (d >= 1 && d <= maxDay) {
                Console.WriteLine("valid");
            } else {
                Console.WriteLine("invalid");
            }
        }
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int d = sc.nextInt();
        int m = sc.nextInt();
        int y = sc.nextInt();

        boolean leap = y % 400 == 0 || (y % 4 == 0 && y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            System.out.println("invalid");
        } else {
            int maxDay;

            if (m == 1 || m == 3 || m == 5 || m == 7 || m == 8 || m == 10 || m == 12) {
                maxDay = 31;
            } else if (m == 4 || m == 6 || m == 9 || m == 11) {
                maxDay = 30;
            } else if (leap) {
                maxDay = 29;
            } else {
                maxDay = 28;
            }

            if (d >= 1 && d <= maxDay) {
                System.out.println("valid");
            } else {
                System.out.println("invalid");
            }
        }
    }
}""",
}

T012_BUGGY = {
    "pascal": """var d, m, y, maxDay: integer;
    leap: boolean;
begin
  d, m, y = map(int, input().split());

  leap := y % 400 == 0 or (y % 4 == 0 and y % 100 != 0);

  if (m < 1) || (m > 12) || (y < 1) then
    writeln('invalid')
  else
  begin
    if m in [1, 3, 5, 7, 8, 10, 12] then
      maxDay := 31
    else if m in [4, 6, 9, 11] then
      maxDay := 30
    else if leap then
      maxDay := 29
    else
      maxDay := 28;

    if 1 <= d <= maxDay then
      print('valid')
    else
      writeln('invalid');
  end;
end.""",
    "python": """d, m, y = map(int, input().split())

leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)

if m < 1 or m > 12 or y < 1:
    print('invalid')
else:
    if m in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif m in (4, 6, 9, 11):
        max_day = 30
    elif m == 2:
        max_day = 28
    elif leap:
        max_day = 29
    else:
        max_day = 28

    if 1 <= d <= max_day:
        print('valid')
    else:
        print('invalid')""",
    "cpp": """#include <iostream>
using namespace std;

int main() {
    int d, m, y;
    d, m, y = map(int, input().split());

    bool leap = y % 400 = 0 || (y % 4 = 0 && y % 100 != 0);

    if (m < 1 or m > 12 or y < 1) {
        print("invalid");
    } else {
        int maxDay = 28;
        if (m in {1, 3, 5, 7, 8, 10, 12}) {
            maxDay = 31;
        } else if (m in {4, 6, 9, 11}) {
            maxDay = 30;
        }

        if (1 <= d && d <= maxDay) {
            cout << "valid";
        } else {
            cout << "invalid";
        }
    }

    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int d, m, y = map(int, input().split());

        bool leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            print("invalid");
        } else {
            int maxDay = 28;

            if (m in [1, 3, 5, 7, 8, 10, 12]) {
                maxDay = 31;
            } else if (m in [4, 6, 9, 11]) {
                maxDay = 30;
            }

            if (1 <= d && d <= maxDay) {
                Console.WriteLine("valid");
            } else {
                Console.WriteLine("invalid");
            }
        }
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        int d, m, y = map(int, input().split());

        boolean leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            print("invalid");
        } else {
            int maxDay = 28;

            if (m in [1, 3, 5, 7, 8, 10, 12]) {
                maxDay = 31;
            } else if (m in [4, 6, 9, 11]) {
                maxDay = 30;
            }

            if (1 <= d && d <= maxDay) {
                System.out.println("valid");
            } else {
                System.out.println("invalid");
            }
        }
    }
}""",
}

T012_HINTS = [
    "Сначала проверьте диапазон месяца и года.",
    "Для февраля учитывайте високосный год.",
    "Ответ только valid или invalid.",
]
T012_POST = (
    "Корректная дата: месяц 1..12, день в пределах числа дней месяца с учётом високосного года. "
    "Ошибки: неверная длина февраля, 31 день в 30-дневном месяце, неверный месяц."
)

T020_TITLE = "Сумма неотрицательных до нуля"
T020_DESC = (
    "Читайте числа, пока не встретите 0. Суммируйте только неотрицательные значения "
    "и выведите сумму."
)
T020_TESTS = [
    {"name": "Тест 1", "inputs": "1\n2\n-1\n3\n0\n", "output": "6"},
    {"name": "Тест 2", "inputs": "-5\n0\n", "output": "0"},
    {"name": "Тест 3", "inputs": "2\n0\n", "output": "2"},
    {"name": "Тест 4", "inputs": "0\n", "output": "0"},
]

T020_REF = {
    "pascal": """var x, total: integer;
begin
  total := 0;
  readln(x);

  while x <> 0 do
  begin
    if x >= 0 then
      total := total + x;

    readln(x);
  end;

  writeln(total);
end.""",
    "python": """total = 0
x = int(input())

while x != 0:
    if x >= 0:
        total += x
    x = int(input())

print(total)""",
    "cpp": """#include <iostream>

int main() {
    int total = 0;
    int x;
    std::cin >> x;

    while (x != 0) {
        if (x >= 0) {
            total += x;
        }
        std::cin >> x;
    }

    std::cout << total;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int total = 0;
        int x = int.Parse(Console.ReadLine());

        while (x != 0) {
            if (x >= 0) {
                total += x;
            }
            x = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(total);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int total = 0;
        int x = sc.nextInt();

        while (x != 0) {
            if (x >= 0) {
                total += x;
            }
            x = sc.nextInt();
        }

        System.out.println(total);
    }
}""",
}

T020_BUGGY = {
    "pascal": """var x, total: integer;
begin
  total := 0;
  readln(x);

  while x <> 0 do
  begin
    if x < 0 then
      total := total + x;

    readln(x);
  end;

  writeln(total);
end.""",
    "python": """total = 0
x = int(input())

while x != 0:
    if x < 0:
        total += x
    x = int(input())

print(total)""",
    "cpp": """#include <iostream>

int main() {
    int total = 0;
    int x;
    std::cin >> x;

    while (x != 0) {
        if (x < 0) {
            total += x;
        }
        std::cin >> x;
    }

    std::cout << total;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int total = 0;
        int x = int.Parse(Console.ReadLine());

        while (x != 0) {
            if (x < 0) {
                total += x;
            }
            x = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(total);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int total = 0;
        int x = sc.nextInt();

        while (x != 0) {
            if (x < 0) {
                total += x;
            }
            x = sc.nextInt();
        }

        System.out.println(total);
    }
}""",
}

T020_HINTS = [
    "Читайте числа в цикле, пока не встретите 0.",
    "Отрицательные значения не должны попадать в сумму.",
    "0 — только стоп-сигнал, не добавляйте его к сумме.",
]
T020_POST = (
    "Нужно читать числа до нуля и суммировать только неотрицательные. "
    "Типичная ошибка — суммировать отрицательные или читать фиксированное количество чисел вместо цикла до 0."
)

BATCH4_OVERRIDES = {
    "task_012": {
        "title": T012_TITLE,
        "description": T012_DESC,
        "ref": T012_REF,
        "buggy": T012_BUGGY,
        "tests": T012_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "stdin_read",
            "stdout_write",
            "simple_branch",
            "branch_logic",
        ],
        "hints": T012_HINTS,
        "post_solve": T012_POST,
        "canon_notes": (
            "Вывод valid/invalid (не yes/no). Убрать placeholder T5 (3\\n1\\n2\\n3\\n→6). "
            "Buggy: синтаксические ошибки в Pascal/C++/C#/Java + логическая ошибка february=28 в Python."
        ),
        "failing_test_fix": (
            "T5 placeholder из чужого sum-task удаляется; остаются 4 теста v128. "
            "T1–T4 текущего fixed уже проходят."
        ),
    },
    "task_020": {
        "title": T020_TITLE,
        "description": T020_DESC,
        "ref": T020_REF,
        "buggy": T020_BUGGY,
        "tests": T020_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "pre_condition_loop",
        ],
        "hints": T020_HINTS,
        "post_solve": T020_POST,
        "canon_notes": (
            "I/O: read-until-zero (не counted n). Buggy: суммирует только отрицательные (инверсия условия). "
            "Pitfall: for_range_off_by_one / wrong loop model."
        ),
        "failing_test_fix": (
            "T5 placeholder удаляется. Текущий fixed уже проходит T1–T4 until-zero тесты; "
            "проблема только в лишнем T5 с форматом counted-array."
        ),
    },
}
