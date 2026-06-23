"""Load chapter-13 (linked_lists) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "linked_lists"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

_COMMON_DESC = "Программа работает с узлами, связанными ссылками."

# 97-99 assemble; 100,101,104 translation; 102,103 debug
_KIND_BY_PATTERN = {
    "task_097": "assemble",
    "task_098": "assemble",
    "task_099": "assemble",
    "task_100": "translation",
    "task_101": "translation",
    "task_102": "debug",
    "task_103": "debug",
    "task_104": "translation",
}

_FORMAT_BY_PATTERN = {
    "task_097": "сборка_программы",
    "task_098": "сборка_программы",
    "task_099": "сборка_программы",
    "task_100": "перевод_программы",
    "task_101": "перевод_программы",
    "task_102": "исправление",
    "task_103": "исправление",
    "task_104": "перевод_программы",
}

_USER_META: dict[str, dict[str, str]] = {
    "task_097": {
        "title": "Создание узла",
        "short_goal": "Создание узла.",
        "detailed_description": _COMMON_DESC,
    },
    "task_098": {
        "title": "Добавление в начало",
        "short_goal": "Добавление в начало.",
        "detailed_description": _COMMON_DESC,
    },
    "task_099": {
        "title": "Добавление в конец",
        "short_goal": "Добавление в конец.",
        "detailed_description": _COMMON_DESC,
    },
    "task_100": {
        "title": "Поиск узла",
        "short_goal": "Поиск узла.",
        "detailed_description": _COMMON_DESC,
    },
    "task_101": {
        "title": "Удаление узла",
        "short_goal": "Удаление узла.",
        "detailed_description": _COMMON_DESC,
    },
    "task_102": {
        "title": "Разворот списка",
        "short_goal": "Разворот списка.",
        "detailed_description": _COMMON_DESC,
    },
    "task_103": {
        "title": "Слияние двух списков",
        "short_goal": "Слияние двух списков.",
        "detailed_description": _COMMON_DESC,
    },
    "task_104": {
        "title": "Итоговая: плейлист",
        "short_goal": "Итоговая: плейлист.",
        "detailed_description": (
            "Команды: add song, next, current. "
            "Плейлист — кольцевой связный список."
        ),
    },
}

_CUSTOM_TESTS: dict[str, list[dict[str, str]]] = {
    "task_097": [
        {"inputs": "", "output": "10"},
    ],
    "task_098": [
        {"inputs": "3\n1\n2\n3\n", "output": "3 2 1 "},
        {"inputs": "1\n5\n", "output": "5 "},
        {"inputs": "0\n", "output": ""},
    ],
    "task_099": [
        {"inputs": "3\n1\n2\n3\n", "output": "1 2 3 "},
        {"inputs": "1\n5\n", "output": "5 "},
        {"inputs": "0\n", "output": ""},
    ],
    "task_100": [
        {"inputs": "3\n1\n2\n3\n2\n", "output": "found"},
        {"inputs": "2\n5\n3\n4\n", "output": "not found"},
        {"inputs": "1\n7\n7\n", "output": "found"},
    ],
    "task_101": [
        {"inputs": "4\n1\n2\n3\n4\n2\n", "output": "1 3 4 "},
        {"inputs": "3\n1\n2\n3\n1\n", "output": "2 3 "},
        {"inputs": "2\n5\n5\n5\n", "output": "5 "},
    ],
    "task_102": [
        {"inputs": "3\n1\n2\n3\n", "output": "3 2 1 "},
        {"inputs": "1\n5\n", "output": "5 "},
        {"inputs": "0\n", "output": ""},
    ],
    "task_103": [
        {"inputs": "3\n1\n3\n5\n3\n2\n4\n6\n", "output": "1 2 3 4 5 6 "},
        {"inputs": "2\n1\n3\n1\n2\n", "output": "1 2 3 "},
        {"inputs": "0\n2\n4\n5\n", "output": "4 5 "},
    ],
    "task_104": [
        {"inputs": "2\nadd song1\ncurrent\n", "output": "song1"},
        {"inputs": "1\ncurrent\n", "output": "empty"},
        {"inputs": "4\nadd a\nadd b\nnext\ncurrent\n", "output": "b"},
    ],
}


def _difficulty_from_course(pattern_id: str) -> str:
    rows = json.loads(_COURSE_JSON.read_text(encoding="utf-8"))
    row = next(r for r in rows if r.get("pattern_id") == pattern_id)
    raw = str(row.get("difficulty") or "medium").strip().lower()
    if raw in {"easy", "medium", "hard"}:
        return raw
    mapping = {"легкий": "easy", "средний": "medium", "сложный": "hard"}
    return mapping.get(raw, "medium")


def _load_code_module(task_num: int):
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch13_user_codes.task_{task_num:03d}")


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


def build_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for task_num in range(97, 105):
        pattern_id = f"task_{task_num:03d}"
        kind = _KIND_BY_PATTERN[pattern_id]
        mod = _load_code_module(task_num)
        payload = _codes_from_module(mod, kind)
        meta = dict(_USER_META[pattern_id])
        item: dict[str, Any] = {
            "task_num": task_num,
            "pattern_id": pattern_id,
            "kind": kind,
            "task_format": _FORMAT_BY_PATTERN[pattern_id],
            "difficulty": _difficulty_from_course(pattern_id),
            "tests": _CUSTOM_TESTS[pattern_id],
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
