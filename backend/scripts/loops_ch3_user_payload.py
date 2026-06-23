"""Load chapter-3 (loops) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
if str(_SCRIPTS.parent) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS.parent))

from application.curriculum.display.chapter3_loops_hints import (  # noqa: E402
    chapter3_hints_for_pattern,
)

CHAPTER_KEY = "loops"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

CH3_TASK_META: dict[str, dict[str, str]] = {
    "task_017": {
        "title": "Сумма чисел до стоп-значения",
        "goal": (
            "Читайте целые числа до появления стоп-значения 0. "
            "Выведите сумму всех прочитанных чисел, не включая 0."
        ),
        "action": "assemble",
        "format_ru": "сборка_программы",
    },
    "task_018": {
        "title": "Поиск первого вхождения",
        "goal": (
            "Даны n и массив из n чисел, затем искомое значение x. "
            "Выведите индекс первого вхождения x (1-based) или 0, если x не найден."
        ),
        "action": "assemble",
        "format_ru": "сборка_фрагмента",
    },
    "task_019": {
        "title": "Проверка простого числа",
        "goal": (
            "Дано целое число n > 1. Определите, является ли оно простым, "
            "и выведите yes или no."
        ),
        "action": "implement",
        "format_ru": "перевод_программы",
    },
    "task_020": {
        "title": "Сумма неотрицательных до нуля",
        "goal": (
            "Читайте числа, пока не встретите 0. "
            "Суммируйте только неотрицательные значения и выведите сумму."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_021": {
        "title": "Таблица умножения",
        "goal": (
            "Дано n. Выведите таблицу умножения чисел от 1 до n "
            "(значения n×1, n×2, …, n×n через пробел в одной строке)."
        ),
        "action": "assemble",
        "format_ru": "сборка_программы",
    },
    "task_022": {
        "title": "Поиск последнего вхождения",
        "goal": (
            "Даны n и массив из n чисел, затем искомое значение x. "
            "Выведите индекс последнего вхождения x (1-based) или 0."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_023": {
        "title": "Гистограмма частот",
        "goal": (
            "Даны n и n целых чисел от 0 до 9. "
            "Постройте гистограмму частот и выведите количество каждого значения "
            "(10 чисел для 0..9 через пробел)."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_024": {
        "title": "Итоговая: статистика последовательности",
        "goal": (
            "Даны n и n целых чисел. "
            "Выведите минимум, максимум, сумму и среднее (целую часть) последовательности. "
            "При n ≤ 0 выведите invalid."
        ),
        "action": "implement",
        "format_ru": "перевод_программы",
    },
}

_KIND_BY_PATTERN = {
    pid: "translation" if meta["action"] == "implement" else meta["action"]
    for pid, meta in CH3_TASK_META.items()
}


def _line_stdin(*tokens: str | int) -> str:
    return " ".join(str(t) for t in tokens) + "\n"


def _lines_stdin(*lines: str | int) -> str:
    return "\n".join(str(line) for line in lines) + "\n"


def _until_zero_stdin(*values: int) -> str:
    return "\n".join(str(v) for v in values) + "\n0\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_017":
        return [
            {"inputs": _until_zero_stdin(2, 9, 1, 7), "output": "19"},
            {"inputs": _until_zero_stdin(10), "output": "10"},
            {"inputs": _until_zero_stdin(-5, -1, -8, -2), "output": "-16"},
        ]
    if pattern_id == "task_018":
        return [
            {"inputs": _lines_stdin("5 7", 2, 9, 1, 7, 7), "output": "4"},
            {"inputs": _lines_stdin("3 5", 1, 2, 3), "output": "0"},
            {"inputs": _lines_stdin("1 12", 12), "output": "1"},
            {"inputs": _lines_stdin("4 7", 7, 7, 1, 7), "output": "1"},
        ]
    if pattern_id == "task_019":
        return [
            {"inputs": "7\n", "output": "yes"},
            {"inputs": "9\n", "output": "no"},
            {"inputs": "2\n", "output": "yes"},
            {"inputs": "1\n", "output": "no"},
        ]
    if pattern_id == "task_020":
        return [
            {"inputs": _lines_stdin(1, 2, -1, 3, 0), "output": "6"},
            {"inputs": _lines_stdin(-5, 0), "output": "0"},
            {"inputs": _lines_stdin(2, 0), "output": "2"},
        ]
    if pattern_id == "task_021":
        return [
            {"inputs": "3\n", "output": "3 6 9"},
            {"inputs": "1\n", "output": "1"},
            {"inputs": "2\n", "output": "2 4"},
            {"inputs": "4\n", "output": "4 8 12 16"},
        ]
    if pattern_id == "task_022":
        return [
            {"inputs": _lines_stdin("5 7", 2, 9, 1, 7, 7), "output": "5"},
            {"inputs": _lines_stdin("3 5", 1, 2, 3), "output": "0"},
            {"inputs": _lines_stdin("4 7", 7, 7, 1, 7), "output": "4"},
            {"inputs": _lines_stdin("1 3", 3), "output": "1"},
        ]
    if pattern_id == "task_023":
        return [
            {"inputs": _lines_stdin(5, 1, 2, 1, 9, 1), "output": "0 3 1 0 0 0 0 0 0 1 "},
            {"inputs": _lines_stdin(3, 0, 0, 0), "output": "3 0 0 0 0 0 0 0 0 0 "},
            {"inputs": _lines_stdin(4, 9, 8, 7, 6), "output": "0 0 0 0 0 0 1 1 1 1 "},
        ]
    if pattern_id == "task_024":
        return [
            {"inputs": _lines_stdin(5, 2, 9, 1, 7, 4), "output": "1 9 23 4"},
            {"inputs": _lines_stdin(1, 10), "output": "10 10 10 10"},
            {"inputs": _lines_stdin(4, -5, -1, -8, -2), "output": "-8 -1 -16 -4"},
            {"inputs": _lines_stdin(3, 5, 5, 5), "output": "5 5 15 5"},
            {"inputs": "0\n", "output": "invalid"},
        ]
    raise KeyError(pattern_id)


def _user_meta(pattern_id: str) -> dict[str, str]:
    row = CH3_TASK_META[pattern_id]
    goal = row["goal"]
    short = goal.split(".")[0].strip()
    if short and not short.endswith("."):
        short += "."
    return {
        "title": row["title"],
        "short_goal": short,
        "detailed_description": goal,
    }


def _load_code_module(task_num: int):
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch3_user_codes.task_{task_num:03d}")


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
    for task_num in range(17, 25):
        pattern_id = f"task_{task_num:03d}"
        kind = _KIND_BY_PATTERN[pattern_id]
        mod = _load_code_module(task_num)
        payload = _codes_from_module(mod, kind)
        meta = _user_meta(pattern_id)
        catalog = CH3_TASK_META[pattern_id]
        item: dict[str, Any] = {
            "task_num": task_num,
            "pattern_id": pattern_id,
            "kind": kind,
            "task_format": catalog["format_ru"],
            "difficulty": _difficulty_from_course(pattern_id),
            "tests": _tests_for_pattern(pattern_id),
            "hints": chapter3_hints_for_pattern(pattern_id),
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
