"""Load chapter-15 (oop) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "oop"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

_COMMON_DESC = "Программа описывает сущность через класс, поля и методы."

# 113,119 assemble; 114,115,117,120 translation; 116,118 debug
_KIND_BY_PATTERN = {
    "task_113": "assemble",
    "task_114": "translation",
    "task_115": "translation",
    "task_116": "debug",
    "task_117": "translation",
    "task_118": "debug",
    "task_119": "assemble",
    "task_120": "translation",
}

_FORMAT_BY_PATTERN = {
    "task_113": "сборка_программы",
    "task_114": "перевод_программы",
    "task_115": "перевод_программы",
    "task_116": "исправление",
    "task_117": "перевод_программы",
    "task_118": "исправление",
    "task_119": "сборка_программы",
    "task_120": "перевод_программы",
}

_USER_META: dict[str, dict[str, str]] = {
    "task_113": {
        "title": "Класс User",
        "short_goal": "Класс User.",
        "detailed_description": _COMMON_DESC,
    },
    "task_114": {
        "title": "Банковский счёт",
        "short_goal": "Банковский счёт.",
        "detailed_description": _COMMON_DESC,
    },
    "task_115": {
        "title": "Класс Product",
        "short_goal": "Класс Product.",
        "detailed_description": _COMMON_DESC,
    },
    "task_116": {
        "title": "Ошибка в методе объекта",
        "short_goal": "Ошибка в методе объекта.",
        "detailed_description": _COMMON_DESC,
    },
    "task_117": {
        "title": "Каталог книг",
        "short_goal": "Каталог книг.",
        "detailed_description": _COMMON_DESC,
    },
    "task_118": {
        "title": "Заказ и список товаров",
        "short_goal": "Заказ и список товаров.",
        "detailed_description": _COMMON_DESC,
    },
    "task_119": {
        "title": "Вызов методов объектов",
        "short_goal": "Вызов методов объектов.",
        "detailed_description": _COMMON_DESC,
    },
    "task_120": {
        "title": "Итоговая: мини-CRM",
        "short_goal": "Итоговая: мини-CRM.",
        "detailed_description": _COMMON_DESC,
    },
}

_CUSTOM_TESTS: dict[str, list[dict[str, str]]] = {
    "task_113": [
        {"inputs": "", "output": "Alex"},
    ],
    "task_114": [
        {"inputs": "", "output": "Alex 150"},
    ],
    "task_115": [
        {"inputs": "", "output": "Book 600"},
    ],
    "task_116": [
        {"inputs": "", "output": "12"},
    ],
    "task_117": [
        {"inputs": "", "output": "Python 2020\nPascal 1995"},
    ],
    "task_118": [
        {"inputs": "", "output": "350"},
    ],
    "task_119": [
        {"inputs": "", "output": "active\ndone"},
    ],
    "task_120": [
        {"inputs": "", "output": "Alex 2 450"},
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
    return importlib.import_module(f"ch15_user_codes.task_{task_num:03d}")


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
    for task_num in range(113, 121):
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
