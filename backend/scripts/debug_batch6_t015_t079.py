"""Batch 6 preview spec: task_015 discount %, task_079 merge dicts (no DB apply)."""
from __future__ import annotations

import importlib

_t15 = importlib.import_module("ch2_user_codes.task_015")
_t79 = importlib.import_module("ch10_user_codes.task_079")

T015_TITLE = "Цена покупки со скидкой"
T015_DESC = (
    "В одной строке вводятся сумма покупки total, флаг студента isStudent (0 или 1) "
    "и флаг купона hasCoupon (0 или 1). По правилам программы рассчитайте итоговый "
    "процент скидки (0–30) с учётом порогов суммы, бонуса студента (+5) и бонуса "
    "купона (+3). При некорректном вводе выведите invalid."
)
T015_TESTS = [
    {"name": "Тест 1", "inputs": "25000 1 1\n", "output": "30"},
    {"name": "Тест 2", "inputs": "3000 0 0\n", "output": "0"},
    {"name": "Тест 3", "inputs": "-1 0 0\n", "output": "invalid"},
    {"name": "Тест 4", "inputs": "20000 1 1\n", "output": "30"},
    {"name": "Тест 5", "inputs": "10000 0 1\n", "output": "18"},
]

T015_REF = {
    "pascal": _t15.FIXED_PASCAL,
    "python": _t15.FIXED_PYTHON,
    "cpp": _t15.FIXED_CPP,
    "csharp": _t15.FIXED_CSHARP,
    "java": _t15.FIXED_JAVA,
}
T015_BUGGY = {
    "pascal": _t15.BUGGY_PASCAL,
    "python": _t15.BUGGY_PYTHON,
    "cpp": _t15.BUGGY_CPP,
    "csharp": _t15.BUGGY_CSHARP,
    "java": _t15.BUGGY_JAVA,
}

T015_HINTS = [
    "Сначала проверьте корректность трёх входных значений.",
    "Базовая скидка зависит от порога суммы, затем добавляются бонусы.",
    "Итоговый процент скидки не может превышать 30.",
]
T015_POST = (
    "Пороги: ≥5000 → 7%, ≥10000 → 15%, ≥20000 → 25%. Студент +5%, купон +3%, "
    "максимум 30%. Ответ — процент скидки (не цена после скидки). "
    "Типичные ошибки: путать цену и процент, не ограничивать cap, неверная валидация флагов."
)

T079_TITLE = "Объединение словарей с суммированием"
T079_DESC = (
    "Вводится n, затем n пар key value, затем m, затем m пар key value. "
    "Объедините отображения: при совпадении ключей суммируйте значения. "
    "Выведите все ключи и итоговые значения в лексикографическом порядке "
    "(по одной паре key value на строку)."
)
T079_TESTS = [
    {
        "name": "Тест 1",
        "inputs": "2\na 1\nb 2\n2\na 3\nc 4\n",
        "output": "a 4\nb 2\nc 4",
    },
    {"name": "Тест 2", "inputs": "1\nx 5\n1\nx 7\n", "output": "x 12"},
    {"name": "Тест 3", "inputs": "0\n2\np 1\nq 2\n", "output": "p 1\nq 2"},
    {"name": "Тест 4", "inputs": "1\nk 5\n1\nk 3\n", "output": "k 8"},
]

T079_REF = {
    "pascal": _t79.FIXED_PASCAL,
    "python": _t79.FIXED_PYTHON,
    "cpp": _t79.FIXED_CPP,
    "csharp": _t79.FIXED_CSHARP,
    "java": _t79.FIXED_JAVA,
}
T079_BUGGY = {
    "pascal": _t79.BUGGY_PASCAL,
    "python": _t79.BUGGY_PYTHON,
    "cpp": _t79.BUGGY_CPP,
    "csharp": _t79.BUGGY_CSHARP,
    "java": _t79.BUGGY_JAVA,
}

T079_HINTS = [
    "Сначала прочитайте n пар, затем m пар для второго словаря.",
    "При совпадении ключа значения нужно суммировать, а не заменять.",
    "Выводите ключи в отсортированном порядке.",
]
T079_POST = (
    "Нужно объединить два отображения с суммированием значений по ключу. "
    "Типичная ошибка — перезаписать значение при повторном ключе вместо сложения "
    "(map merge / overwrite instead of sum)."
)

BATCH6_OVERRIDES = {
    "task_015": {
        "title": T015_TITLE,
        "description": T015_DESC,
        "ref": T015_REF,
        "buggy": T015_BUGGY,
        "tests": T015_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "stdin_read",
            "stdout_write",
            "simple_branch",
            "multi_branch",
        ],
        "hints": T015_HINTS,
        "post_solve": T015_POST,
        "canon_notes": (
            "Output = discount percent 0–30, not final price. "
            "Source: ch2_user_codes/task_015 fixed/buggy ×5. T6 placeholder removed."
        ),
        "db_replacements": [
            "title (strip chapter prefix)",
            "description (percent not price)",
            "test_cases (5, drop T6)",
            "code_examples[lang] fixed",
            "code_examples[buggy_lang] buggy",
            "hints, post_solve_explanation, expected_concepts, teacher_assembly_override",
        ],
        "legacy_untouched": [
            "ALGO_SYNTAX_META.raw_title «Система скидок»",
            "branches_ch2_user_payload generic description",
            "v128_test_suites_data (unchanged on disk)",
        ],
        "risks": [
            "buggy non-Python: intentional syntax errors for translate-debug",
            "buggy Python: C#/JS-like syntax — may fail all tests at runtime",
            "meta still says «итоговая цена» until meta sync",
        ],
    },
    "task_079": {
        "title": T079_TITLE,
        "description": T079_DESC,
        "ref": T079_REF,
        "buggy": T079_BUGGY,
        "tests": T079_TESTS,
        "concepts": [
            "program_entry",
            "typed_declaration",
            "assignment",
            "stdin_read",
            "stdout_write",
            "key_value_map",
        ],
        "hints": T079_HINTS,
        "post_solve": T079_POST,
        "canon_notes": (
            "I/O: n pairs + m pairs. Buggy: overwrite on key clash, wrong loop on dict. "
            "Source: ch10_user_codes/task_079. T5 placeholder removed."
        ),
        "db_replacements": [
            "title (strip chapter prefix)",
            "description (explicit n/m I/O)",
            "test_cases (4, drop T5 sum placeholder)",
            "code_examples (replace word-frequency garbage)",
            "code_examples buggy_* from ch10",
            "hints, post_solve, expected_concepts",
        ],
        "legacy_untouched": [
            "v128_test_suites_data on disk",
            "maps_ch10_user_payload (3-test subset; canon uses 4)",
            "ALGO_SYNTAX_META stale word-freq test_cases",
        ],
        "risks": [
            "T1 multiline output order must match sorted keys",
            "buggy Python: iterates dict keys only — may error or wrong format",
            "n=0 edge case (T3) must not break buggy fixed-size arrays in Pascal buggy",
        ],
    },
}
