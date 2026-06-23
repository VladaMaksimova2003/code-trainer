"""Batch 7 preview spec: task_063 descending integer sort, task_071 pos/neg sums (no DB apply)."""

T063_TITLE = "Сортировка по убыванию"
T063_DESC = (
    "Вводится n, затем n целых чисел по одному в строке. "
    "Отсортируйте массив по убыванию и выведите элементы в одной строке через пробел."
)
T063_TESTS = [
    {"name": "Тест 1", "inputs": "5\n5\n2\n9\n1\n7\n", "output": "9 7 5 2 1"},
    {"name": "Тест 2", "inputs": "1\n10\n", "output": "10"},
    {"name": "Тест 3", "inputs": "3\n-1\n-3\n-2\n", "output": "-1 -2 -3"},
    {"name": "Тест 4", "inputs": "3\n4\n4\n4\n", "output": "4 4 4"},
]

T063_REF = {
    "pascal": """var n, i, j, temp: integer;
    a: array[0..99] of integer;
begin
  readln(n);

  for i := 0 to n - 1 do
    readln(a[i]);

  for i := 0 to n - 1 do
    for j := 0 to n - i - 2 do
      if a[j] < a[j + 1] then
      begin
        temp := a[j];
        a[j] := a[j + 1];
        a[j + 1] := temp;
      end;

  for i := 0 to n - 1 do
    write(a[i], ' ');
end.""",
    "python": """n = int(input())
a = [int(input()) for _ in range(n)]

for i in range(n):
    for j in range(0, n - i - 1):
        if a[j] < a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]

print(' '.join(str(x) for x in a))""",
    "cpp": """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (a[j] < a[j + 1]) {
                std::swap(a[j], a[j + 1]);
            }
        }
    }

    for (int i = 0; i < n; i++) {
        if (i > 0) {
            std::cout << ' ';
        }
        std::cout << a[i];
    }

    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (a[j] < a[j + 1]) {
                    int temp = a[j];
                    a[j] = a[j + 1];
                    a[j + 1] = temp;
                }
            }
        }

        Console.WriteLine(string.Join(" ", a));
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (a[j] < a[j + 1]) {
                    int temp = a[j];
                    a[j] = a[j + 1];
                    a[j + 1] = temp;
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) {
                sb.append(' ');
            }
            sb.append(a[i]);
        }
        System.out.println(sb);
    }
}""",
}

T063_BUGGY = {
    "pascal": """var n, i, j, temp: integer;
    a: array[0..99] of integer;
begin
  n = int(input());

  for i in range(n) do
    a[i] := int(input());

  for i := 0 to n do
    for j := 0 to n - i do
      if a[j] > a[j + 1] then
      begin
        swap(a[j], a[j + 1]);
      end;

  print(*a);
end.""",
    "python": """n = int(input())
a = [int(input()) for _ in range(n)]

for i in range(n):
    for j in range(0, n - i - 1):
        if a[j] > a[j + 1]:
            a[j], a[j + 1] = a[j + 1], a[j]

print(' '.join(str(x) for x in a))""",
    "cpp": """#include <iostream>
#include <vector>

int main() {
    int n = int(input());
    vector<int> a = new int[n];

    for i in range(n):
        cin >> a[i];

    for (int i = 0; i <= n; i++) {
        for (int j = 0; j < n - i; j++) {
            if (a[j] > a[j + 1]) {
                a[j], a[j + 1] = a[j + 1], a[j];
            }
        }
    }

    Console.WriteLine(a);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Console.ReadLine();

        for (int i = 0; i <= n; i++) {
            for (int j = 0; j < n - i; j++) {
                if (a[j] > a[j + 1]) {
                    a[j], a[j + 1] = a[j + 1], a[j];
                }
            }
        }

        print(a);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Scanner.nextInt();

        for (int i = 0; i <= n; i++) {
            for (int j = 0; j < n - i; j++) {
                if (a[j] > a[j + 1]) {
                    a[j], a[j + 1] = a[j + 1], a[j];
                }
            }
        }

        Console.WriteLine(a);
    }
}""",
}

T063_HINTS = [
    "Сначала прочитайте n, затем n целых чисел.",
    "Для убывания меняйте местами соседние элементы, если левый меньше правого.",
    "Выведите отсортированные числа в одной строке через пробел.",
]
T063_POST = (
    "Нужна сортировка массива целых по убыванию (bubble sort или эквивалент). "
    "Типичные ошибки: сравнение для возрастания (`>` вместо `<`), неверные границы цикла, "
    "путаница с форматом ввода записей name score из legacy-тестов."
)

T071_TITLE = "Суммы положительных и отрицательных"
T071_DESC = (
    "Вводится n, затем n целых чисел по одному в строке. "
    "Выведите сумму положительных чисел и сумму отрицательных через пробел. "
    "Ноль не учитывается ни в одной из сумм."
)
T071_TESTS = [
    {"name": "Тест 1", "inputs": "4\n2\n9\n-1\n7\n", "output": "18 -1"},
    {"name": "Тест 2", "inputs": "3\n-5\n-1\n-8\n", "output": "0 -14"},
    {"name": "Тест 3", "inputs": "3\n0\n0\n0\n", "output": "0 0"},
    {"name": "Тест 4", "inputs": "1\n5\n", "output": "5 0"},
]

T071_REF = {
    "pascal": """var n, i, x, posSum, negSum: integer;
begin
  readln(n);
  posSum := 0;
  negSum := 0;

  for i := 1 to n do
  begin
    readln(x);
    if x > 0 then
      posSum := posSum + x
    else if x < 0 then
      negSum := negSum + x;
  end;

  writeln(posSum, ' ', negSum);
end.""",
    "python": """n = int(input())
pos_sum = 0
neg_sum = 0

for _ in range(n):
    x = int(input())
    if x > 0:
        pos_sum += x
    elif x < 0:
        neg_sum += x

print(pos_sum, neg_sum)""",
    "cpp": """#include <iostream>

int main() {
    int n, x, posSum = 0, negSum = 0;
    std::cin >> n;

    for (int i = 0; i < n; i++) {
        std::cin >> x;
        if (x > 0) {
            posSum += x;
        } else if (x < 0) {
            negSum += x;
        }
    }

    std::cout << posSum << ' ' << negSum;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int posSum = 0;
        int negSum = 0;

        for (int i = 0; i < n; i++) {
            int x = int.Parse(Console.ReadLine());
            if (x > 0) {
                posSum += x;
            } else if (x < 0) {
                negSum += x;
            }
        }

        Console.WriteLine(posSum + " " + negSum);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int posSum = 0;
        int negSum = 0;

        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x > 0) {
                posSum += x;
            } else if (x < 0) {
                negSum += x;
            }
        }

        System.out.println(posSum + " " + negSum);
    }
}""",
}

T071_BUGGY = {
    "pascal": """var n, i, x, posSum, negSum: integer;
begin
  n = int(input());
  posSum := 0;
  negSum := 0;

  for i in range(n) do
  begin
    x := int(input());
    if x >= 0 then
      posSum := posSum + x
    else
      negSum := negSum + x;
  end;

  writeln(negSum, ' ', posSum);
end.""",
    "python": """n = int(input())
pos_sum = 0
neg_sum = 0

for _ in range(n):
    x = int(input())
    if x > 0:
        pos_sum += x
    elif x < 0:
        neg_sum += x

print(neg_sum, pos_sum)""",
    "cpp": """#include <iostream>

int main() {
    int n = int(input());
    int posSum = 0;
    int negSum = 0;

    for i in range(n):
        int x;
        cin >> x;
        if (x >= 0) {
            posSum += x;
        } else {
            negSum += x;
        }

    cout << negSum << " " << posSum;
    return 0;
}""",
    "csharp": """using System;

class Program {
    static void Main() {
        int n = int(input());
        int posSum = 0;
        int negSum = 0;

        for i in range(n):
            int x = int.Parse(Console.ReadLine());
            if (x >= 0) {
                posSum += x;
            } else {
                negSum += x;
            }

        Console.WriteLine(negSum + " " + posSum);
    }
}""",
    "java": """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        int posSum = 0;
        int negSum = 0;

        for i in range(n):
            int x = Scanner.nextInt();
            if (x >= 0) {
                posSum += x;
            } else {
                negSum += x;
            }

        System.out.println(negSum + " " + posSum);
    }
}""",
}

T071_HINTS = [
    "Прочитайте n, затем n целых чисел.",
    "Положительные (>0) складывайте отдельно, отрицательные (<0) — в другую сумму.",
    "Ноль пропускайте. Выведите две суммы через пробел.",
]
T071_POST = (
    "Нужен один проход с двумя аккумуляторами: pos_sum для x>0, neg_sum для x<0. "
    "Типичные ошибки: включить ноль в neg_sum, перепутать порядок вывода, "
    "использовать группировку по строковым ключам (legacy Canon B)."
)

BATCH7_OVERRIDES = {
    "task_063": {
        "title": T063_TITLE,
        "description": T063_DESC,
        "ref": T063_REF,
        "buggy": T063_BUGGY,
        "tests": T063_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "indexed_sequence",
            "counted_loop",
            "sort_order",
        ],
        "hints": T063_HINTS,
        "post_solve": T063_POST,
        "canon_notes": (
            "Integer array descending; space-separated output. "
            "Source: DB fixed python + v128 corrections; T5 placeholder removed. "
            "Buggy python: ascending sort; non-Python: translate-debug syntax mix."
        ),
        "db_replacements": [
            "title (strip chapter prefix)",
            "description (explicit n + integers I/O)",
            "test_cases (4, drop T5 placeholder)",
            "code_examples fixed/buggy ×5",
            "hints, post_solve_explanation, expected_concepts",
        ],
        "legacy_untouched": [
            "ALGO_SYNTAX_META.raw_title «Сортировка объектов/записей»",
            "v128_test_suites_data (records)",
            "search_sort_ch8_user_payload assemble/records",
            "ch8_user_codes/task_063",
        ],
        "risks": [
            "buggy python may pass T2/T4 (single element / all equal)",
            "non-Python buggy is syntax-mix translate-debug (intentional)",
            "showcase known_language_variants still ascending in cpp/java until apply",
        ],
    },
    "task_071": {
        "title": T071_TITLE,
        "description": T071_DESC,
        "ref": T071_REF,
        "buggy": T071_BUGGY,
        "tests": T071_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "counted_loop",
            "arithmetic_ops",
            "fold_aggregate",
            "filter_select",
        ],
        "hints": T071_HINTS,
        "post_solve": T071_POST,
        "canon_notes": (
            "pos_sum and neg_sum; zeros ignored. Canon A authored from scratch. "
            "DB word-frequency code discarded. T5 placeholder removed."
        ),
        "db_replacements": [
            "title (strip chapter prefix)",
            "description (zeros excluded)",
            "test_cases (4, drop T5)",
            "code_examples (replace word-freq garbage) fixed/buggy ×5",
            "hints, post_solve, expected_concepts",
        ],
        "legacy_untouched": [
            "v128_test_suites_data (category grouping)",
            "aggregation_ch9_user_payload",
            "ch9_user_codes/task_071 Canon B",
            "ALGO_SYNTAX_META.raw_title «Группировка данных»",
        ],
        "risks": [
            "buggy python swapped output passes T3 (0 0)",
            "buggy pascal uses x>=0 (logical) + swapped output + python syntax",
            "full ×5 authored — review Pascal/Java compile paths on apply",
        ],
    },
}
