"""Batch 3 damaged-task overrides: task_044 power, task_047 min/max (canon confirmed)."""

T044_TITLE = "Возведение в степень"
T044_DESC = (
    "Даны целые base и exp. Реализуйте функцию возведения в степень base^exp "
    "и выведите результат."
)
T044_TESTS = [
    {"name": "Тест 1", "inputs": "2 3\n", "output": "8"},
    {"name": "Тест 2", "inputs": "5 0\n", "output": "1"},
    {"name": "Тест 3", "inputs": "3 1\n", "output": "3"},
    {"name": "Тест 4", "inputs": "2 10\n", "output": "1024"},
]

T044_REF = {
    "pascal": """function Power(base, exp: integer): integer;
var i, result: integer;
begin
  result := 1;

  for i := 1 to exp do
    result := result * base;

  Power := result;
end;

var base, exp: integer;
begin
  readln(base, exp);
  writeln(Power(base, exp));
end.""",
    "python": """def power(base, exp):
    result = 1

    for _ in range(exp):
        result *= base

    return result


base, exp = map(int, input().split())
print(power(base, exp))""",
    "cpp": """#include <iostream>

int power(int base, int exp) {
    int result = 1;

    for (int i = 0; i < exp; i++)
        result *= base;

    return result;
}

int main() {
    int base, exp;
    std::cin >> base >> exp;

    std::cout << power(base, exp);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static int Power(int baseNum, int exp) {
        int result = 1;

        for (int i = 0; i < exp; i++)
            result *= baseNum;

        return result;
    }

    static void Main() {
        string[] parts = Console.ReadLine().Split();
        int baseNum = int.Parse(parts[0]);
        int exp = int.Parse(parts[1]);

        Console.WriteLine(Power(baseNum, exp));
    }
}""",
    "java": """import java.util.*;

class Main {
    static int power(int baseNum, int exp) {
        int result = 1;

        for (int i = 0; i < exp; i++)
            result *= baseNum;

        return result;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int baseNum = sc.nextInt();
        int exp = sc.nextInt();

        System.out.println(power(baseNum, exp));
    }
}""",
}

T044_BUGGY = {
    "pascal": """function Power(base, exp: integer): integer;
var i, result: integer;
begin
  result := 1;

  for i := 1 to exp do
    result := result + base;

  Power := result;
end;

var base, exp: integer;
begin
  readln(base, exp);
  writeln(Power(base, exp));
end.""",
    "python": """def power(base, exp):
    result = 1

    for _ in range(exp):
        result += base

    return result


base, exp = map(int, input().split())
print(power(base, exp))""",
    "cpp": """#include <iostream>

int power(int base, int exp) {
    int result = 1;

    for (int i = 0; i < exp; i++)
        result += base;

    return result;
}

int main() {
    int base, exp;
    std::cin >> base >> exp;

    std::cout << power(base, exp);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static int Power(int baseNum, int exp) {
        int result = 1;

        for (int i = 0; i < exp; i++)
            result += baseNum;

        return result;
    }

    static void Main() {
        string[] parts = Console.ReadLine().Split();
        int baseNum = int.Parse(parts[0]);
        int exp = int.Parse(parts[1]);

        Console.WriteLine(Power(baseNum, exp));
    }
}""",
    "java": """import java.util.*;

class Main {
    static int power(int baseNum, int exp) {
        int result = 1;

        for (int i = 0; i < exp; i++)
            result += baseNum;

        return result;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int baseNum = sc.nextInt();
        int exp = sc.nextInt();

        System.out.println(power(baseNum, exp));
    }
}""",
}

T047_TITLE = "Минимум и максимум пары"
T047_DESC = (
    "Даны два целых числа a и b. Реализуйте функции минимума и максимума "
    "и выведите сначала min(a, b), затем max(a, b) через пробел."
)
T047_TESTS = [
    {"name": "Тест 1", "inputs": "9 2\n", "output": "2 9"},
    {"name": "Тест 2", "inputs": "5 5\n", "output": "5 5"},
    {"name": "Тест 3", "inputs": "-3 7\n", "output": "-3 7"},
    {"name": "Тест 4", "inputs": "100 -5\n", "output": "-5 100"},
]

T047_REF = {
    "pascal": """function MinPair(a, b: integer): integer;
begin
  if a < b then
    MinPair := a
  else
    MinPair := b;
end;

function MaxPair(a, b: integer): integer;
begin
  if a > b then
    MaxPair := a
  else
    MaxPair := b;
end;

var a, b: integer;
begin
  readln(a, b);
  writeln(MinPair(a, b), ' ', MaxPair(a, b));
end.""",
    "python": """def min_pair(a, b):
    if a < b:
        return a
    return b


def max_pair(a, b):
    if a > b:
        return a
    return b


a, b = map(int, input().split())
print(min_pair(a, b), max_pair(a, b))""",
    "cpp": """#include <iostream>

int minPair(int a, int b) {
    if (a < b) return a;
    return b;
}

int maxPair(int a, int b) {
    if (a > b) return a;
    return b;
}

int main() {
    int a, b;
    std::cin >> a >> b;

    std::cout << minPair(a, b) << ' ' << maxPair(a, b);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static int MinPair(int a, int b) {
        if (a < b) return a;
        return b;
    }

    static int MaxPair(int a, int b) {
        if (a > b) return a;
        return b;
    }

    static void Main() {
        string[] parts = Console.ReadLine().Split();
        int a = int.Parse(parts[0]);
        int b = int.Parse(parts[1]);

        Console.WriteLine(MinPair(a, b) + " " + MaxPair(a, b));
    }
}""",
    "java": """import java.util.*;

class Main {
    static int minPair(int a, int b) {
        if (a < b) return a;
        return b;
    }

    static int maxPair(int a, int b) {
        if (a > b) return a;
        return b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = sc.nextInt();
        int b = sc.nextInt();

        System.out.println(minPair(a, b) + " " + maxPair(a, b));
    }
}""",
}

T047_BUGGY = {
    "pascal": """function MinPair(a, b: integer): integer;
begin
  if a > b then
    MinPair := a
  else
    MinPair := b;
end;

function MaxPair(a, b: integer): integer;
begin
  if a < b then
    MaxPair := a
  else
    MaxPair := b;
end;

var a, b: integer;
begin
  readln(a, b);
  writeln(MinPair(a, b), ' ', MaxPair(a, b));
end.""",
    "python": """def min_pair(a, b):
    if a > b:
        return a
    return b


def max_pair(a, b):
    if a < b:
        return a
    return b


a, b = map(int, input().split())
print(min_pair(a, b), max_pair(a, b))""",
    "cpp": """#include <iostream>

int minPair(int a, int b) {
    if (a > b) return a;
    return b;
}

int maxPair(int a, int b) {
    if (a < b) return a;
    return b;
}

int main() {
    int a, b;
    std::cin >> a >> b;

    std::cout << minPair(a, b) << ' ' << maxPair(a, b);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static int MinPair(int a, int b) {
        if (a > b) return a;
        return b;
    }

    static int MaxPair(int a, int b) {
        if (a < b) return a;
        return b;
    }

    static void Main() {
        string[] parts = Console.ReadLine().Split();
        int a = int.Parse(parts[0]);
        int b = int.Parse(parts[1]);

        Console.WriteLine(MinPair(a, b) + " " + MaxPair(a, b));
    }
}""",
    "java": """import java.util.*;

class Main {
    static int minPair(int a, int b) {
        if (a > b) return a;
        return b;
    }

    static int maxPair(int a, int b) {
        if (a < b) return a;
        return b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int a = sc.nextInt();
        int b = sc.nextInt();

        System.out.println(minPair(a, b) + " " + maxPair(a, b));
    }
}""",
}

T044_HINTS = [
    "Начните result с 1 — это нейтральный элемент для умножения.",
    "В цикле умножайте result на base ровно exp раз.",
    "При exp = 0 цикл не выполняется и ответ остаётся 1.",
]
T044_POST = (
    "Степень — это повторное умножение: base^exp = base * base * … (exp раз). "
    "Замена result * base на result + base считает сумму, а не произведение."
)

T047_HINTS = [
    "MinPair возвращает меньшее из двух чисел, MaxPair — большее.",
    "Сравнивайте a и b напрямую, без обмена аргументов местами.",
    "Выводите сначала минимум, затем максимум через пробел.",
]
T047_POST = (
    "MinPair должен выбирать a при a < b, MaxPair — a при a > b. "
    "Перепутанные знаки сравнения меняют роли функций местами."
)
