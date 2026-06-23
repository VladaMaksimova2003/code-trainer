"""Stage 3: expansion task meta task_129–task_144 (chapters 1–4, P1)."""

from __future__ import annotations

from typing import Any

from v128_test_matrix import tc

V192_STAGE3_SHIPPED_COUNT = 16
V192_STAGE3_FIRST = 129
V192_STAGE3_LAST = 144

_FORMAT_BY_ACTION = {
    "assemble": "сборка_программы",
    "debug": "исправление",
    "implement": "перевод_программы",
}

_ACTION_BY_SLOT = {
    129: "assemble",
    130: "assemble",
    131: "debug",
    132: "implement",
    133: "assemble",
    134: "assemble",
    135: "debug",
    136: "implement",
    137: "assemble",
    138: "assemble",
    139: "debug",
    140: "implement",
    141: "assemble",
    142: "assemble",
    143: "debug",
    144: "implement",
}

_CHAPTER_BY_NUM = {
    **{n: "algo_basics" for n in range(129, 133)},
    **{n: "branches" for n in range(133, 137)},
    **{n: "loops" for n in range(137, 141)},
    **{n: "arrays_collections" for n in range(141, 145)},
}

_PITFALL_BY_NUM = {
    131: "integer_division",
    135: "chain_comparison",
    139: "for_range_off_by_one",
    143: "index_1based",
}

_GOALS: dict[int, str] = {
    129: "Дано целое n. Выведите сумму его цифр.",
    130: "Дано n и n целых чисел. Выведите количество чётных.",
    131: "Дано n и n температур (целые). Выведите целую часть среднего.",
    132: "Дано n и n чисел. Выведите минимум.",
    133: "Дано year. Выведите yes, если год високосный, иначе no.",
    134: "Даны weight (кг) и height (см). Выведите категорию BMI: under/normal/over/obese.",
    135: "Даны a, b, x. Выведите yes, если a ≤ x ≤ b, иначе no.",
    136: "Даны a, b, c. Выведите число действительных корней (0, 1 или 2).",
    137: "Дано n. Выведите сумму 1 + 2 + … + n.",
    138: "Даны a и b. Выведите НОД(a, b).",
    139: "Читайте числа до 0. Суммируйте только положительные и выведите сумму.",
    140: "Дано n. Выведите длину последовательности Collatz, начиная с n.",
    141: "Дано n и n чисел. Выведите второй по величине элемент.",
    142: "Дано n и n чисел. Сдвиньте все нули в конец, сохранив порядок остальных.",
    143: "Дано n и n чисел. Выведите элементы массива в обратном порядке.",
    144: "Дано n и n чисел. Выведите n+1 чисел — префиксные суммы (s0=0).",
}

_TITLES: dict[int, str] = {
    129: "Сумма цифр числа",
    130: "Количество чётных чисел",
    131: "Среднее температур (целое)",
    132: "Минимум из n чисел",
    133: "Високосный год",
    134: "Категория BMI",
    135: "Попадание x в отрезок [a,b]",
    136: "Корни квадратного уравнения",
    137: "Сумма 1+2+…+n",
    138: "НОД (алгоритм Еuclid)",
    139: "Сумма положительных до нуля",
    140: "Длина последовательности Collatz",
    141: "Второй максимум массива",
    142: "Сдвиг нулей в конец",
    143: "Разворот массива",
    144: "Префиксные суммы",
}

_TESTS: dict[int, list[dict[str, str]]] = {
    129: [
        tc("typical", "12345\n", "15", input_kind="scalar"),
        tc("single", "7\n", "7", input_kind="scalar"),
        tc("typical", "3\n1\n2\n3\n", "6", input_kind="array"),
        tc("negative", "-123\n", "6", input_kind="scalar"),
    ],
    130: [
        tc("typical", "5\n1\n2\n3\n4\n5\n", "2", input_kind="array"),
        tc("single", "1\n0\n", "1", input_kind="array"),
        tc("zero_empty", "3\n1\n3\n5\n", "0", input_kind="array"),
        tc("negative", "4\n-2\n4\n-6\n8\n", "2", input_kind="array"),
    ],
    131: [
        tc("typical", "4\n10\n20\n30\n40\n", "25", input_kind="array"),
        tc("single", "1\n7\n", "7", input_kind="array"),
        tc("negative", "3\n-5\n5\n5\n", "1", input_kind="array"),
        tc("boundary", "2\n3\n4\n", "3", input_kind="array"),
    ],
    132: [
        tc("typical", "4\n2\n9\n1\n7\n", "1", input_kind="array"),
        tc("single", "1\n10\n", "10", input_kind="array"),
        tc("negative", "3\n-5\n-1\n", "-5", input_kind="array"),
        tc("all_equal", "3\n4\n4\n4\n", "4", input_kind="array"),
    ],
    133: [
        tc("typical", "2024\n", "yes", input_kind="scalar"),
        tc("typical", "1900\n", "no", input_kind="scalar"),
        tc("boundary", "2000\n", "yes", input_kind="scalar"),
        tc("single", "2023\n", "no", input_kind="scalar"),
    ],
    134: [
        tc("typical", "70 170\n", "normal", input_kind="scalar"),
        tc("boundary", "50 200\n", "under", input_kind="scalar"),
        tc("typical", "80 170\n", "over", input_kind="scalar"),
        tc("typical", "110 170\n", "obese", input_kind="scalar"),
    ],
    135: [
        tc("typical", "1 10 5\n", "yes", input_kind="scalar"),
        tc("boundary", "1 10 1\n", "yes", input_kind="scalar"),
        tc("not_found", "1 10 0\n", "no", input_kind="scalar"),
        tc("invalid", "5 1 3\n", "no", input_kind="scalar"),
    ],
    136: [
        tc("typical", "1 2 1\n", "2", input_kind="scalar"),
        tc("single", "1 0 0\n", "1", input_kind="scalar"),
        tc("zero_empty", "1 0 1\n", "0", input_kind="scalar"),
        tc("negative", "1 -4 4\n", "2", input_kind="scalar"),
    ],
    137: [
        tc("typical", "5\n", "15", input_kind="scalar"),
        tc("single", "1\n", "1", input_kind="scalar"),
        tc("boundary", "0\n", "0", input_kind="scalar"),
        tc("typical", "10\n", "55", input_kind="scalar"),
    ],
    138: [
        tc("typical", "12 8\n", "4", input_kind="scalar"),
        tc("single", "7 7\n", "7", input_kind="scalar"),
        tc("typical", "48 18\n", "6", input_kind="scalar"),
        tc("boundary", "1 100\n", "1", input_kind="scalar"),
    ],
    139: [
        tc("typical", "1\n2\n-1\n3\n0\n", "6", input_kind="scalar"),
        tc("zero_empty", "0\n", "0", input_kind="scalar"),
        tc("negative", "-5\n0\n", "0", input_kind="scalar"),
        tc("single", "2\n0\n", "2", input_kind="scalar"),
    ],
    140: [
        tc("typical", "6\n", "9", input_kind="scalar"),
        tc("single", "1\n", "1", input_kind="scalar"),
        tc("boundary", "16\n", "5", input_kind="scalar"),
        tc("typical", "3\n", "8", input_kind="scalar"),
    ],
    141: [
        tc("typical", "4\n2\n9\n1\n7\n", "7", input_kind="array"),
        tc("duplicate", "3\n5\n5\n1\n", "5", input_kind="array"),
        tc("single", "1\n10\n", "10", input_kind="array"),
        tc("negative", "4\n-5\n-1\n-8\n-2\n", "-2", input_kind="array"),
    ],
    142: [
        tc("typical", "5\n0\n1\n0\n2\n3\n", "1 2 3 0 0", input_kind="array"),
        tc("zero_empty", "3\n0\n0\n0\n", "0 0 0", input_kind="array"),
        tc("single", "1\n5\n", "5", input_kind="array"),
        tc("all_equal", "3\n1\n2\n3\n", "1 2 3", input_kind="array"),
    ],
    143: [
        tc("typical", "4\n1\n2\n3\n4\n", "4 3 2 1", input_kind="array"),
        tc("single", "1\n7\n", "7", input_kind="array"),
        tc("typical", "2 2\n1\n2\n3\n4\n", "4 3 2 1", input_kind="matrix"),
        tc("zero_empty", "1\n0\n", "0", input_kind="array"),
    ],
    144: [
        tc("typical", "3\n1\n2\n3\n", "0 1 3 6", input_kind="array"),
        tc("single", "1\n5\n", "0 5", input_kind="array"),
        tc("negative", "3\n-1\n2\n3\n", "0 -1 1 4", input_kind="array"),
        tc("zero_empty", "3\n0\n0\n0\n", "0 0 0 0", input_kind="array"),
    ],
}

_PYTHON_REF: dict[int, str] = {
    129: "n = int(input())\nprint(sum(int(d) for d in str(abs(n))))",
    130: "n = int(input())\nprint(sum(1 for _ in range(n) if int(input()) % 2 == 0))",
    131: "n = int(input())\nvals = [int(input()) for _ in range(n)]\nprint(sum(vals) // n)",
    132: "n = int(input())\nprint(min(int(input()) for _ in range(n)))",
    133: (
        "y = int(input())\nleap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)\n"
        "print('yes' if leap else 'no')"
    ),
    134: (
        "w, h = map(int, input().split())\n"
        "b = w * 10000 // (h * h)\n"
        "print('under' if b < 1850 else 'normal' if b < 2500 else 'over' if b < 3000 else 'obese')"
    ),
    135: "a, b, x = map(int, input().split())\nprint('yes' if a <= x <= b else 'no')",
    136: (
        "a, b, c = map(int, input().split())\n"
        "d = b * b - 4 * a * c\n"
        "print(0 if d < 0 else 1 if d == 0 else 2)"
    ),
    137: "n = int(input())\nprint(n * (n + 1) // 2)",
    138: (
        "a, b = map(int, input().split())\n"
        "while b:\n    a, b = b, a % b\n"
        "print(a)"
    ),
    139: (
        "total = 0\nx = int(input())\n"
        "while x != 0:\n    if x > 0:\n        total += x\n    x = int(input())\n"
        "print(total)"
    ),
    140: (
        "def collatz(n):\n    steps = 1\n    while n != 1:\n        n = n // 2 if n % 2 == 0 else 3 * n + 1\n        steps += 1\n    return steps\n"
        "print(collatz(int(input())))"
    ),
    141: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "best = second = -10**18\n"
        "for v in a:\n    if v > best:\n        second, best = best, v\n    elif v > second and v != best:\n        second = v\n"
        "print(second)"
    ),
    142: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "nz = [x for x in a if x != 0]\n"
        "print(' '.join(str(x) for x in nz + [0] * (n - len(nz))))"
    ),
    143: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "print(' '.join(str(x) for x in reversed(a)))"
    ),
    144: (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "s = 0\n"
        "out = ['0']\n"
        "for v in a:\n    s += v\n    out.append(str(s))\n"
        "print(' '.join(out))"
    ),
}

_DEBUG_PAIR: dict[int, tuple[str, str]] = {
    131: (
        "n = int(input())\nvals = [int(input()) for _ in range(n)]\nprint(sum(vals) / n)",
        "n = int(input())\nvals = [int(input()) for _ in range(n)]\nprint(sum(vals) // n)",
    ),
    135: (
        "a, b, x = map(int, input().split())\nprint('yes' if a < x < b else 'no')",
        "a, b, x = map(int, input().split())\nprint('yes' if a <= x <= b else 'no')",
    ),
    139: (
        "n = int(input())\ntotal = 0\nfor i in range(n + 1):\n    x = int(input())\n    if x >= 0:\n        total += x\nprint(total)",
        "total = 0\nx = int(input())\nwhile x != 0:\n    if x > 0:\n        total += x\n    x = int(input())\nprint(total)",
    ),
    143: (
        "n = int(input())\nfor i in range(n):\n    print(int(input()))",
        "n = int(input())\na = [int(input()) for _ in range(n)]\nprint(' '.join(str(x) for x in reversed(a)))",
    ),
}


def _empty_impl() -> dict[str, Any]:
    return {
        "assembly_blocks": [],
        "placeholder_code": "",
        "gaps": [],
        "translation_code": "",
        "buggy_code": "",
        "fixed_code": "",
        "error_descriptions": [],
    }


def _build_meta(task_num: int) -> dict[str, Any]:
    pattern = f"task_{task_num:03d}"
    action = _ACTION_BY_SLOT[task_num]
    chapter = _CHAPTER_BY_NUM[task_num]
    goal = _GOALS[task_num]
    py = _PYTHON_REF[task_num]
    impl = _empty_impl()
    impls: dict[str, dict[str, Any]] = {}
    for lang in ("pascal", "python", "cpp", "csharp", "java"):
        row = dict(impl)
        if action == "debug" and task_num in _DEBUG_PAIR:
            buggy, fixed = _DEBUG_PAIR[task_num]
            row["buggy_code"] = buggy
            row["fixed_code"] = fixed
            row["translation_code"] = fixed
        elif action == "implement":
            row["translation_code"] = py
            row["fixed_code"] = py
        else:
            row["translation_code"] = py
            row["fixed_code"] = py
        impls[lang] = row

    meta: dict[str, Any] = {
        "task_num": task_num,
        "chapter_key": chapter,
        "raw_title": _TITLES[task_num],
        "title": _TITLES[task_num],
        "short_goal": goal,
        "detailed_description": goal,
        "format_ru": _FORMAT_BY_ACTION[action],
        "format_raw": _FORMAT_BY_ACTION[action],
        "action": action,
        "difficulty": "medium",
        "difficulty_ru": "средний",
        "test_cases": [dict(t) for t in _TESTS[task_num]],
        "expected_concepts": {"python": ["program_entry", "stdin_read", "stdout_write"]},
        "implementations": impls,
        "reference_codes": {lang: py for lang in ("pascal", "python", "cpp", "csharp", "java")},
    }
    pitfall = _PITFALL_BY_NUM.get(task_num)
    if pitfall:
        meta["pitfall_id"] = pitfall
    return meta


def build_v192_stage3_meta() -> dict[str, dict[str, Any]]:
    return {f"task_{n:03d}": _build_meta(n) for n in range(V192_STAGE3_FIRST, V192_STAGE3_LAST + 1)}


V192_STAGE3_META: dict[str, dict[str, Any]] = build_v192_stage3_meta()


def apply_v192_stage3_meta(catalog: dict[str, dict[str, Any]]) -> None:
    from v128_test_input_enrichment import enrich_test_suite

    for pattern, meta in V192_STAGE3_META.items():
        row = dict(meta)
        row["test_cases"] = enrich_test_suite(pattern, row.get("test_cases") or [])
        catalog[pattern] = row
