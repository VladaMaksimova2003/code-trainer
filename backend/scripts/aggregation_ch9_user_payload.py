"""Load chapter-9 (aggregation) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "aggregation"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

# 65-68,72 translation; 69-71 debug
_KIND_BY_PATTERN = {
    "task_065": "translation",
    "task_066": "translation",
    "task_067": "translation",
    "task_068": "translation",
    "task_069": "debug",
    "task_070": "debug",
    "task_071": "debug",
    "task_072": "translation",
}

_FORMAT_BY_KIND = {
    "assemble": "сборка_программы",
    "debug": "исправление",
    "translation": "перевод_программы",
}

_COMMON_DESC = "Фильтрация, свёртка и агрегация данных."

_USER_META: dict[str, dict[str, str]] = {
    "task_065": {
        "title": "Сумма продаж",
        "short_goal": "Даны n и n чисел. Выведите сумму.",
        "detailed_description": "Даны n и n чисел. Найдите сумму всех значений и выведите её.",
    },
    "task_066": {
        "title": "Среднее значение",
        "short_goal": "Даны n и n чисел. Выведите среднее (целая часть).",
        "detailed_description": "Даны n и n чисел. Выведите среднее арифметическое (целую часть).",
    },
    "task_067": {
        "title": "Фильтр положительных чисел",
        "short_goal": "Даны n и n чисел. Выведите только положительные.",
        "detailed_description": "Даны n и n чисел. Выведите только положительные числа через пробел.",
    },
    "task_068": {
        "title": "Фильтр заказов по статусу",
        "short_goal": "Выведите только заказы со статусом paid.",
        "detailed_description": (
            "Вводится n, затем n строк формата: id status amount. "
            "Нужно вывести только заказы со статусом paid."
        ),
    },
    "task_069": {
        "title": "Подсчёт голосов",
        "short_goal": "Подсчитайте частоту каждого слова.",
        "detailed_description": (
            "Вводится строка слов. Выведите каждое слово и количество его вхождений "
            "в алфавитном порядке."
        ),
    },
    "task_070": {
        "title": "Топ N элементов",
        "short_goal": "Выведите k наибольших чисел по убыванию.",
        "detailed_description": (
            "Вводится количество чисел n, затем n чисел, затем k. "
            "Нужно вывести k наибольших чисел по убыванию."
        ),
    },
    "task_071": {
        "title": "Группировка данных",
        "short_goal": "Суммируйте amount по каждой category.",
        "detailed_description": (
            "Вводится n, затем n строк формата: category amount. "
            "Нужно вывести сумму по каждой категории в алфавитном порядке."
        ),
    },
    "task_072": {
        "title": "Итоговая: аналитика магазина",
        "short_goal": "Сводка по оплаченным заказам.",
        "detailed_description": (
            "Вводится n, затем n строк формата: category status amount. "
            "Выведите total_paid count_paid max_paid для заказов со статусом paid. "
            "Если оплаченных заказов нет, выведите 0 0 0."
        ),
    },
}


def _lines_stdin(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_065":
        return [
            {"inputs": _lines_stdin("4", "2", "9", "1", "7"), "output": "19"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("4", "-5", "-1", "-8", "-2"), "output": "-16"},
        ]
    if pattern_id == "task_066":
        return [
            {"inputs": _lines_stdin("4", "2", "9", "1", "7"), "output": "4"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("3", "10", "20", "30"), "output": "20"},
        ]
    if pattern_id == "task_067":
        return [
            {"inputs": _lines_stdin("5", "3", "-1", "5", "0", "2"), "output": "3 5 2"},
            {"inputs": _lines_stdin("3", "1", "2", "3"), "output": "1 2 3 "},
            {"inputs": _lines_stdin("2", "-5", "-1"), "output": ""},
        ]
    if pattern_id == "task_068":
        return [
            {
                "inputs": _lines_stdin(
                    "3",
                    "o1 paid 100",
                    "o2 pending 50",
                    "o3 paid 200",
                ),
                "output": _lines_stdin("o1 100", "o3 200").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("2", "a paid 10", "b paid 20"),
                "output": _lines_stdin("a 10", "b 20").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("2", "x pending 5", "y cancelled 7"),
                "output": "",
            },
        ]
    if pattern_id == "task_069":
        return [
            {
                "inputs": "red blue red\n",
                "output": _lines_stdin("blue 1", "red 2").rstrip("\n"),
            },
            {
                "inputs": "a b c\n",
                "output": _lines_stdin("a 1", "b 1", "c 1").rstrip("\n"),
            },
            {
                "inputs": "one one two\n",
                "output": _lines_stdin("one 2", "two 1").rstrip("\n"),
            },
        ]
    if pattern_id == "task_070":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7", "3"), "output": "9 7 5 "},
            {"inputs": _lines_stdin("1", "10", "1"), "output": "10 "},
            {"inputs": _lines_stdin("4", "1", "2", "3", "4", "10"), "output": "4 3 2 1 "},
        ]
    if pattern_id == "task_071":
        return [
            {
                "inputs": _lines_stdin("4", "food 10", "book 5", "food 20", "book 3"),
                "output": _lines_stdin("book 8", "food 30").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("2", "zoo 1", "apple 2"),
                "output": _lines_stdin("apple 2", "zoo 1").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("1", "solo 42"),
                "output": "solo 42",
            },
        ]
    if pattern_id == "task_072":
        return [
            {
                "inputs": _lines_stdin(
                    "4",
                    "food paid 100",
                    "book pending 50",
                    "food paid 200",
                    "book paid 150",
                ),
                "output": "450 3 200",
            },
            {
                "inputs": _lines_stdin("2", "a pending 10", "b cancelled 20"),
                "output": "0 0 0",
            },
            {
                "inputs": _lines_stdin("1", "x paid 7"),
                "output": "7 1 7",
            },
        ]
    raise KeyError(pattern_id)


def _load_code_module(task_num: int):
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch9_user_codes.task_{task_num:03d}")


def _codes_from_module(mod, kind: str) -> dict[str, Any]:
    if kind == "debug":
        fixed = {
            "pascal": mod.FIXED_PASCAL,
            "python": mod.FIXED_PYTHON,
            "cpp": mod.FIXED_CPP,
            "csharp": mod.FIXED_CSHARP,
            "java": mod.FIXED_JAVA,
        }
        buggy = {
            "pascal": mod.BUGGY_PASCAL,
            "python": mod.BUGGY_PYTHON,
            "cpp": mod.BUGGY_CPP,
            "csharp": mod.BUGGY_CSHARP,
            "java": mod.BUGGY_JAVA,
        }
        return {"fixed": fixed, "buggy": buggy}
    codes = {
        "pascal": mod.PASCAL,
        "python": mod.PYTHON,
        "cpp": mod.CPP,
        "csharp": mod.CSHARP,
        "java": mod.JAVA,
    }
    return {"codes": codes}


def _difficulty_from_course(pattern_id: str) -> str:
    rows = json.loads(_COURSE_JSON.read_text(encoding="utf-8"))
    row = next(r for r in rows if r.get("pattern_id") == pattern_id)
    return str(row["difficulty"])


def build_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for task_num in range(65, 73):
        pattern_id = f"task_{task_num:03d}"
        kind = _KIND_BY_PATTERN[pattern_id]
        mod = _load_code_module(task_num)
        payload = _codes_from_module(mod, kind)
        meta = dict(_USER_META[pattern_id])
        item: dict[str, Any] = {
            "task_num": task_num,
            "pattern_id": pattern_id,
            "kind": kind,
            "task_format": _FORMAT_BY_KIND[kind],
            "difficulty": _difficulty_from_course(pattern_id),
            "tests": _tests_for_pattern(pattern_id),
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
