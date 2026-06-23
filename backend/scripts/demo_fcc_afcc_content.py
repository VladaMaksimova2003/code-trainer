"""Curated DEMO content for task_006 (FCC) and task_003 (AFCC)."""

T006_TITLE = "Средняя загрузка сервера"
T006_DESC = (
    "Вводится количество измерений и значения загрузки сервера. "
    "Нужно вывести целую часть среднего значения: сумму всех измерений, "
    "делённую на их количество."
)

T006_TESTS = [
    {"name": "Тест 1", "inputs": "5\n10\n20\n30\n40\n50\n", "output": "30"},
    {"name": "Тест 2", "inputs": "1\n7\n", "output": "7"},
    {"name": "Тест 3", "inputs": "4\n0\n0\n10\n10\n", "output": "5"},
    {"name": "Тест 4", "inputs": "2\n3\n7\n", "output": "5"},
    {"name": "Тест 5", "inputs": "1\n1\n", "output": "1"},
]

T006_REF = {
    "pascal": """var n, i, load, total: integer;
begin
  readln(n);
  total := 0;
  for i := 1 to n do
  begin
    readln(load);
    total := total + load;
  end;
  writeln(total div n);
end.""",
    "python": """n = int(input())
total = 0
for _ in range(n):
    load = int(input())
    total += load
print(total // n)""",
    "cpp": """#include <iostream>

int main() {
    int n, load, total = 0;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> load;
        total += load;
    }
    std::cout << total / n;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int total = 0;
        for (int i = 0; i < n; i++) {
            int load = int.Parse(Console.ReadLine());
            total += load;
        }
        Console.WriteLine(total / n);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int total = 0;
        for (int i = 0; i < n; i++) {
            total += sc.nextInt();
        }
        System.out.println(total / n);
    }
}""",
}

T006_BUGGY = {
    "pascal": """var n, i, load, total: integer;
begin
  readln(n);
  total := 0;
  for i := 1 to n do
  begin
    readln(load);
    total := total + load;
  end;
  writeln(total / n);
end.""",
    "python": """n = int(input())
total = 0
for _ in range(n):
    load = int(input())
    total += load
print(total / n)""",
    "cpp": """#include <iostream>

int main() {
    int n, load, total = 0;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> load;
        total += load;
    }
    std::cout << (total + 1) / n;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int total = 0;
        for (int i = 0; i < n; i++) {
            total += int.Parse(Console.ReadLine());
        }
        Console.WriteLine((total + 1) / n);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int total = 0;
        for (int i = 0; i < n; i++) {
            total += sc.nextInt();
        }
        System.out.println((total + 1) / n);
    }
}""",
}

T006_HINTS = [
    "Сначала прочитайте n, затем n значений загрузки в цикле.",
    "Суммируйте все измерения в переменную total.",
    "Для целой части среднего используйте целочисленное деление (без вещественного результата).",
]

T006_POST = (
    "Среднее с целой частью: сумма всех load, делённая на n. "
    "В Pascal оператор / даёт real — для задачи нужен div. "
    "В Python одиночный / даёт float, нужен //."
)

T006_CONCEPTS = [
    "tc_program_structure",
    "tc_variables_types",
    "tc_assignment",
    "tc_console_io",
    "tc_loops",
    "tc_aggregate",
    "tc_arithmetic",
]

T003_TITLE = "Минимальная задержка сервера"
T003_DESC = (
    "Система мониторинга получила несколько значений задержки сервера в миллисекундах. "
    "Нужно найти и вывести минимальную задержку. Чем меньше значение, тем лучше отклик."
)

T003_TESTS = [
    {"name": "Тест 1", "inputs": "5\n40\n18\n25\n60\n19\n", "output": "18", "mplt_contrast": True},
    {"name": "Тест 2", "inputs": "1\n7\n", "output": "7"},
    {"name": "Тест 3", "inputs": "4\n100\n90\n120\n80\n", "output": "80"},
    {"name": "Тест 4", "inputs": "3\n42\n42\n42\n", "output": "42"},
    {"name": "Тест 5", "inputs": "1\n1\n", "output": "1"},
]

T003_REF = {
    "pascal": """var n, i, ping, best: integer;
begin
  readln(n);
  readln(best);
  for i := 2 to n do
  begin
    readln(ping);
    if ping < best then
      best := ping;
  end;
  writeln(best);
end.""",
    "python": """n = int(input())
best = int(input())
for _ in range(n - 1):
    ping = int(input())
    if ping < best:
        best = ping
print(best)""",
    "cpp": """#include <iostream>

int main() {
    int n, ping, best;
    std::cin >> n >> best;
    for (int i = 1; i < n; i++) {
        std::cin >> ping;
        if (ping < best) {
            best = ping;
        }
    }
    std::cout << best;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int best = int.Parse(Console.ReadLine());
        for (int i = 1; i < n; i++) {
            int ping = int.Parse(Console.ReadLine());
            if (ping < best) {
                best = ping;
            }
        }
        Console.WriteLine(best);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int best = sc.nextInt();
        for (int i = 1; i < n; i++) {
            int ping = sc.nextInt();
            if (ping < best) {
                best = ping;
            }
        }
        System.out.println(best);
    }
}""",
}

T003_BUGGY = {
    "pascal": """var n, i, ping, best: integer;
begin
  readln(n);
  best := 0;
  for i := 1 to n do
  begin
    readln(ping);
    if ping < best then
      best := ping;
  end;
  writeln(best);
end.""",
    "python": """n = int(input())
best = 0
for _ in range(n):
    ping = int(input())
    if ping < best:
        best = ping
print(best)""",
    "cpp": """#include <iostream>

int main() {
    int n, ping, best = 0;
    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> ping;
        if (ping < best) {
            best = ping;
        }
    }
    std::cout << best;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int best = 0;
        for (int i = 0; i < n; i++) {
            int ping = int.Parse(Console.ReadLine());
            if (ping < best) {
                best = ping;
            }
        }
        Console.WriteLine(best);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int best = 0;
        for (int i = 0; i < n; i++) {
            int ping = sc.nextInt();
            if (ping < best) {
                best = ping;
            }
        }
        System.out.println(best);
    }
}""",
}

# AFCC bad-submit snippet (Pascal): sequential readln vs line model
T003_AFCC_BAD_SUBMIT_PASCAL = """var n, i, ping, best: integer;
begin
  readln(n);
  readln(ping);
  readln(ping);
  readln(ping);
  readln(ping);
  readln(ping);
  best := ping;
  writeln(best);
end."""

T006_FCC_BAD_SUBMIT_PASCAL = """var n, i, load, total: integer;
begin
  readln(n);
  total := 0;
  for i := 1 to n do
  begin
    readln(load);
    total := total + load;
  end;
  writeln(total / n);
end."""

T003_HINTS = [
    "Сначала прочитайте n — количество измерений задержки.",
    "Первое значение можно сразу положить в best, остальные сравнивать в цикле.",
    "Читайте числа так, как задано во входе: если по одному числу на строке — читайте по одному.",
]

T003_POST = (
    "Минимум: первое значение — кандидат в best, далее if ping < best. "
    "Инициализация best := 0 даёт 0 даже при положительных задержках. "
    "При переносе с Python не путайте input().split() с несколькими readln подряд, "
    "если вход — одна строка с числами."
)

T003_CONCEPTS = [
    "tc_program_structure",
    "tc_console_io",
]

T006_FORMAT = "сборка_фрагмента"
