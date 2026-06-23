"""Load chapter-7 (recursion) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "recursion"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

# 49,50 translation; 51,52,53 assemble; 54,55,56 debug
_KIND_BY_PATTERN = {
    "task_049": "translation",
    "task_050": "translation",
    "task_051": "assemble",
    "task_052": "assemble",
    "task_053": "assemble",
    "task_054": "debug",
    "task_055": "debug",
    "task_056": "debug",
}

_FORMAT_BY_KIND = {
    "assemble": "сборка_программы",
    "debug": "исправление",
    "translation": "перевод_программы",
}

_COMMON_DESC = (
    "Решение должно использовать рекурсивную функцию с базовым случаем "
    "и рекурсивным шагом."
)

_USER_META: dict[str, dict[str, str]] = {
    "task_049": {
        "title": "Факториал",
        "short_goal": "Факториал.",
        "detailed_description": _COMMON_DESC,
    },
    "task_050": {
        "title": "Fibonacci",
        "short_goal": "Fibonacci.",
        "detailed_description": _COMMON_DESC,
    },
    "task_051": {
        "title": "Рекурсивная сумма массива",
        "short_goal": "Рекурсивная сумма массива.",
        "detailed_description": _COMMON_DESC,
    },
    "task_052": {
        "title": "Быстрое возведение в степень",
        "short_goal": "Быстрое возведение в степень.",
        "detailed_description": _COMMON_DESC,
    },
    "task_053": {
        "title": "Рекурсивный разворот строки",
        "short_goal": "Рекурсивный разворот строки.",
        "detailed_description": _COMMON_DESC,
    },
    "task_054": {
        "title": "Бинарный поиск рекурсией",
        "short_goal": "Бинарный поиск рекурсией.",
        "detailed_description": _COMMON_DESC,
    },
    "task_055": {
        "title": "Quicksort",
        "short_goal": "Quicksort.",
        "detailed_description": _COMMON_DESC,
    },
    "task_056": {
        "title": "Итоговая: рекурсивный обход каталога",
        "short_goal": "Итоговая: рекурсивный обход каталога.",
        "detailed_description": _COMMON_DESC,
    },
}


def _lines_stdin(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_049":
        return [
            {"inputs": "5\n", "output": "120"},
            {"inputs": "1\n", "output": "1"},
            {"inputs": "0\n", "output": "1"},
        ]
    if pattern_id == "task_050":
        return [
            {"inputs": "0\n", "output": "0"},
            {"inputs": "1\n", "output": "1"},
            {"inputs": "10\n", "output": "55"},
        ]
    if pattern_id == "task_051":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7"), "output": "24"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("5", "4", "-5", "-1", "-8", "-2"), "output": "-12"},
        ]
    if pattern_id == "task_052":
        return [
            {"inputs": _lines_stdin("2", "10"), "output": "1024"},
            {"inputs": _lines_stdin("3", "4"), "output": "81"},
            {"inputs": _lines_stdin("5", "0"), "output": "1"},
        ]
    if pattern_id == "task_053":
        return [
            {"inputs": "hello\n", "output": "olleh"},
            {"inputs": "a\n", "output": "a"},
            {"inputs": "ab\n", "output": "ba"},
        ]
    if pattern_id == "task_054":
        return [
            {"inputs": _lines_stdin("5", "1", "2", "3", "4", "5", "3"), "output": "2"},
            {"inputs": _lines_stdin("5", "1", "2", "3", "4", "5", "6"), "output": "-1"},
            {"inputs": _lines_stdin("3", "10", "20", "30", "10"), "output": "0"},
        ]
    if pattern_id == "task_055":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7"), "output": "1 2 5 7 9"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("3", "3", "2", "1"), "output": "1 2 3"},
        ]
    if pattern_id == "task_056":
        return [
            {"inputs": _lines_stdin("3", "-1 100", "0 20", "0 30"), "output": "150"},
            {"inputs": _lines_stdin("1", "-1 42"), "output": "42"},
            {"inputs": _lines_stdin("4", "-1 10", "0 5", "0 3", "1 2"), "output": "20"},
        ]
    raise KeyError(pattern_id)


def _load_code_module(task_num: int):
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch7_user_codes.task_{task_num:03d}")


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
    for task_num in range(49, 57):
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
