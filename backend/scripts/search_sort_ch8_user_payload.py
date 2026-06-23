"""Load chapter-8 (search/sort) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "search_sort"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

# 57,58,59 translation; 62,63 assemble; 60,61,64 debug
_KIND_BY_PATTERN = {
    "task_057": "translation",
    "task_058": "translation",
    "task_059": "translation",
    "task_060": "debug",
    "task_061": "debug",
    "task_062": "assemble",
    "task_063": "assemble",
    "task_064": "debug",
}

_FORMAT_BY_KIND = {
    "assemble": "сборка_программы",
    "debug": "исправление",
    "translation": "перевод_программы",
}

_COMMON_DESC = (
    "Программа применяет алгоритм поиска или сортировки к набору данных."
)

_USER_META: dict[str, dict[str, str]] = {
    "task_057": {
        "title": "Линейный поиск",
        "short_goal": "Линейный поиск.",
        "detailed_description": _COMMON_DESC,
    },
    "task_058": {
        "title": "Бинарный поиск",
        "short_goal": "Бинарный поиск.",
        "detailed_description": _COMMON_DESC,
    },
    "task_059": {
        "title": "Selection Sort",
        "short_goal": "Selection Sort.",
        "detailed_description": _COMMON_DESC,
    },
    "task_060": {
        "title": "Bubble Sort",
        "short_goal": "Bubble Sort.",
        "detailed_description": _COMMON_DESC,
    },
    "task_061": {
        "title": "Insertion Sort",
        "short_goal": "Insertion Sort.",
        "detailed_description": _COMMON_DESC,
    },
    "task_062": {
        "title": "Сортировка строк",
        "short_goal": "Сортировка строк.",
        "detailed_description": _COMMON_DESC,
    },
    "task_063": {
        "title": "Сортировка объектов/записей",
        "short_goal": "Сортировка объектов/записей.",
        "detailed_description": _COMMON_DESC,
    },
    "task_064": {
        "title": "Итоговая: таблица лидеров",
        "short_goal": "Итоговая: таблица лидеров.",
        "detailed_description": _COMMON_DESC,
    },
}


def _lines_stdin(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_057":
        return [
            {"inputs": _lines_stdin("5 7", "5", "2", "9", "1", "7"), "output": "4"},
            {"inputs": _lines_stdin("3 10", "1", "2", "3"), "output": "-1"},
            {"inputs": _lines_stdin("4 2", "2", "2", "1", "3"), "output": "0"},
        ]
    if pattern_id == "task_058":
        return [
            {"inputs": _lines_stdin("5 9", "1", "3", "5", "7", "9"), "output": "4"},
            {"inputs": _lines_stdin("5 4", "1", "2", "3", "4", "5"), "output": "3"},
            {"inputs": _lines_stdin("3 10", "1", "2", "3"), "output": "-1"},
        ]
    if pattern_id == "task_059":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7"), "output": "1 2 5 7 9"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("3", "3", "2", "1"), "output": "1 2 3"},
        ]
    if pattern_id == "task_060":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7"), "output": "1 2 5 7 9"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("3", "3", "2", "1"), "output": "1 2 3"},
        ]
    if pattern_id == "task_061":
        return [
            {"inputs": _lines_stdin("5", "5", "2", "9", "1", "7"), "output": "1 2 5 7 9"},
            {"inputs": _lines_stdin("1", "10"), "output": "10"},
            {"inputs": _lines_stdin("3", "3", "2", "1"), "output": "1 2 3"},
        ]
    if pattern_id == "task_062":
        return [
            {
                "inputs": _lines_stdin("3", "banana", "apple", "cherry"),
                "output": _lines_stdin("apple", "banana", "cherry").rstrip("\n"),
            },
            {"inputs": _lines_stdin("1", "zebra"), "output": "zebra"},
            {"inputs": _lines_stdin("2", "b", "a"), "output": _lines_stdin("a", "b").rstrip("\n")},
        ]
    if pattern_id == "task_063":
        return [
            {
                "inputs": _lines_stdin("3", "Anna 90", "Bob 90", "Carl 80"),
                "output": _lines_stdin("Carl 80", "Anna 90", "Bob 90").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("2", "X 100", "Y 50"),
                "output": _lines_stdin("X 100", "Y 50").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("1", "Solo 42"),
                "output": "Solo 42",
            },
        ]
    if pattern_id == "task_064":
        return [
            {
                "inputs": _lines_stdin(
                    "3",
                    "Anna 100 5",
                    "Bob 100 4",
                    "Carl 90 10",
                ),
                "output": _lines_stdin(
                    "1 Anna 100 5",
                    "2 Bob 100 4",
                    "3 Carl 90 10",
                ).rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("1", "Solo 50 1"),
                "output": "1 Solo 50 1",
            },
            {
                "inputs": _lines_stdin(
                    "2",
                    "A 10 2",
                    "B 10 3",
                ),
                "output": _lines_stdin("1 B 10 3", "2 A 10 2").rstrip("\n"),
            },
        ]
    raise KeyError(pattern_id)


def _load_code_module(task_num: int):
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch8_user_codes.task_{task_num:03d}")


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
    for task_num in range(57, 65):
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
