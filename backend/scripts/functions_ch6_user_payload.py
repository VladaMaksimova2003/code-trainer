"""Load chapter-6 (functions) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "functions"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

# 41,46,48 translation; 42,45,47 debug; 43,44 assemble
_KIND_BY_PATTERN = {
    "task_041": "translation",
    "task_042": "debug",
    "task_043": "assemble",
    "task_044": "assemble",
    "task_045": "debug",
    "task_046": "translation",
    "task_047": "debug",
    "task_048": "translation",
}

_FORMAT_BY_KIND = {
    "assemble": "сборка_программы",
    "debug": "исправление",
    "translation": "перевод_программы",
}

_COMMON_DESC = (
    "Основная логика должна быть вынесена в функцию, "
    "которую вызывает главная часть программы."
)

_USER_META: dict[str, dict[str, str]] = {
    "task_041": {
        "title": "Функция поиска максимума",
        "short_goal": "Функция поиска максимума.",
        "detailed_description": _COMMON_DESC,
    },
    "task_042": {
        "title": "Функция проверки простого числа",
        "short_goal": "Функция проверки простого числа.",
        "detailed_description": _COMMON_DESC,
    },
    "task_043": {
        "title": "Функция GCD",
        "short_goal": "Функция GCD.",
        "detailed_description": _COMMON_DESC,
    },
    "task_044": {
        "title": "Функция нормализации строки",
        "short_goal": "Функция нормализации строки.",
        "detailed_description": _COMMON_DESC,
    },
    "task_045": {
        "title": "Функция бинарного поиска",
        "short_goal": "Функция бинарного поиска.",
        "detailed_description": _COMMON_DESC,
    },
    "task_046": {
        "title": "Функция проверки палиндрома",
        "short_goal": "Функция проверки палиндрома.",
        "detailed_description": _COMMON_DESC,
    },
    "task_047": {
        "title": "Передача массива в функцию",
        "short_goal": "Передача массива в функцию.",
        "detailed_description": _COMMON_DESC,
    },
    "task_048": {
        "title": "Итоговая: библиотека алгоритмов",
        "short_goal": "Итоговая: библиотека алгоритмов.",
        "detailed_description": _COMMON_DESC,
    },
}


def _lines_stdin(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_041":
        return [
            {"inputs": _lines_stdin("5", "2"), "output": "5"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("4", "-5"), "output": "4"},
        ]
    if pattern_id == "task_042":
        return [
            {"inputs": "5\n", "output": "prime"},
            {"inputs": "1\n", "output": "composite"},
            {"inputs": "4\n", "output": "composite"},
        ]
    if pattern_id == "task_043":
        return [
            {"inputs": _lines_stdin("12", "8"), "output": "4"},
            {"inputs": _lines_stdin("1", "10"), "output": "1"},
            {"inputs": _lines_stdin("48", "18"), "output": "6"},
        ]
    if pattern_id == "task_044":
        return [
            {"inputs": "  Hello  \n", "output": "hello"},
            {"inputs": "ABC\n", "output": "abc"},
            {"inputs": "  \n", "output": ""},
        ]
    if pattern_id == "task_045":
        return [
            {"inputs": _lines_stdin("5", "1", "2", "3", "4", "5", "3"), "output": "2"},
            {"inputs": _lines_stdin("5", "1", "2", "3", "4", "5", "6"), "output": "-1"},
            {"inputs": _lines_stdin("3", "10", "20", "30", "10"), "output": "0"},
        ]
    if pattern_id == "task_046":
        return [
            {"inputs": "abba\n", "output": "yes"},
            {"inputs": "abc\n", "output": "no"},
            {"inputs": "a\n", "output": "yes"},
        ]
    if pattern_id == "task_047":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7"), "output": "24"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("5", "4", "-5", "-1", "-8", "-2"), "output": "-12"},
        ]
    if pattern_id == "task_048":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7"), "output": "9 4 5"},
            {"inputs": _lines_stdin("2", "1", "10"), "output": "10 5 2"},
            {"inputs": _lines_stdin("5", "4", "-5", "-1", "-8", "-2"), "output": "4 -2 1"},
        ]
    raise KeyError(pattern_id)


def _load_code_module(task_num: int):
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch6_user_codes.task_{task_num:03d}")


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
    for task_num in range(41, 49):
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
