/** Подсказки по конструкциям для демо (попап «Арифметика · Python»). */

const PY_ARITH = "total = a + b\navg = total / n"
const PY_FOR = "for i in range(n):\n    s += x[i]"
const PY_IF = "if x % 2 == 0:\n    print('чётное')\nelse:\n    print('нечётное')"
const CPP_ARITH = "sum = a + b;\ncout << sum;"
const CPP_FOR = "for (int i = 0; i < n; i++) {\n    cin >> x;\n    s += x;\n}"

export const MOCK_CONSTRUCTION_HINTS = {
  binary_expression: {
    title: "Арифметика",
    description: "Сложение, вычитание, умножение и деление для накопления результата.",
    examples: {
      python: PY_ARITH,
      cpp: CPP_ARITH,
      java: "int sum = a + b;",
      csharp: "var sum = a + b;",
      pascal: "sum := a + b;",
    },
  },
  arith: {
    title: "Арифметика",
    description: "Базовые арифметические операции в выражениях.",
    examples: {
      python: "result = (a * b) - c",
      cpp: "result = (a * b) - c;",
    },
  },
  for_loop: {
    title: "Цикл for",
    description: "Перебор диапазона или коллекции с известным числом шагов.",
    examples: {
      python: PY_FOR,
      cpp: CPP_FOR,
      java: "for (int i = 0; i < n; i++) { ... }",
      pascal: "for i := 1 to n do\n  ...",
    },
  },
  while_loop: {
    title: "Цикл while",
    description: "Повторение, пока условие истинно.",
    examples: {
      python: "while n > 0:\n    n -= 1",
      cpp: "while (n > 0) { n--; }",
    },
  },
  if_statement: {
    title: "Условие",
    description: "Ветвление по результату проверки.",
    examples: {
      python: PY_IF,
      cpp: "if (n % 2 == 0) cout << \"Even\";",
      java: "if (n % 2 == 0) System.out.println(\"Even\");",
    },
  },
  return_statement: {
    title: "Return",
    description: "Возврат значения из функции.",
    examples: {
      python: "return total",
      cpp: "return total;",
      java: "return total;",
    },
  },
  function_definition: {
    title: "Функция",
    description: "Именованный фрагмент кода с параметрами.",
    examples: {
      python: "def solve(nums):\n    return sum(nums)",
      cpp: "int solve(vector<int>& a) { ... }",
    },
  },
  nested_loops: {
    title: "Вложенные циклы",
    description: "Внешний и внутренний цикл для квадратичных алгоритмов.",
    examples: {
      python: "for i in range(n):\n    for j in range(i + 1, n):\n        ...",
      cpp: "for (int i = 0; i < n; i++)\n  for (int j = i+1; j < n; j++)",
    },
  },
  io: {
    title: "Ввод / вывод",
    description: "Чтение данных и печать результата.",
    examples: {
      python: "n = int(input())\nprint(n)",
      cpp: "cin >> n;\ncout << n;",
      pascal: "readln(n);\nwriteln(n);",
    },
  },
  assign: {
    title: "Присваивание",
    description: "Сохранение значения в переменную.",
    examples: {
      python: "total = 0\ntotal += x",
      cpp: "int total = 0;\ntotal += x;",
    },
  },
  cond: {
    title: "Условие",
    description: "Проверка и ветвление.",
    examples: {
      python: PY_IF,
    },
  },
  loop: {
    title: "Цикл",
    description: "Повторяющееся выполнение тела.",
    examples: {
      python: PY_FOR,
      cpp: CPP_FOR,
    },
  },
}

export function pickConstructionHintsForTask(task) {
  const hints = {}
  for (const key of task.constructions || []) {
    if (MOCK_CONSTRUCTION_HINTS[key]) {
      hints[key] = MOCK_CONSTRUCTION_HINTS[key]
    }
  }
  return hints
}
