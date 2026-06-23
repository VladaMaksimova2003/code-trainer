"""Load chapter-16 (inheritance_capstone) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "inheritance_capstone"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

_COMMON_DESC = (
    "Программа использует базовый тип и специализированные типы с переопределением поведения."
)

# 121,125,126 assemble; 122,123,128 translation; 124,127 debug
_KIND_BY_PATTERN = {
    "task_121": "assemble",
    "task_122": "translation",
    "task_123": "translation",
    "task_124": "debug",
    "task_125": "assemble",
    "task_126": "assemble",
    "task_127": "debug",
    "task_128": "translation",
}

_FORMAT_BY_PATTERN = {
    "task_121": "сборка_программы",
    "task_122": "перевод_программы",
    "task_123": "перевод_программы",
    "task_124": "исправление",
    "task_125": "сборка_программы",
    "task_126": "сборка_программы",
    "task_127": "исправление",
    "task_128": "перевод_программы",
}

_USER_META: dict[str, dict[str, str]] = {
    "task_121": {
        "title": "Базовый класс Animal",
        "short_goal": "Базовый класс Animal.",
        "detailed_description": _COMMON_DESC,
    },
    "task_122": {
        "title": "Иерархия транспорта",
        "short_goal": "Иерархия транспорта.",
        "detailed_description": _COMMON_DESC,
    },
    "task_123": {
        "title": "Сотрудники разных типов",
        "short_goal": "Сотрудники разных типов.",
        "detailed_description": _COMMON_DESC,
    },
    "task_124": {
        "title": "Ошибка переопределения метода",
        "short_goal": "Ошибка переопределения метода.",
        "detailed_description": _COMMON_DESC,
    },
    "task_125": {
        "title": "Полиморфный список объектов",
        "short_goal": "Полиморфный список объектов.",
        "detailed_description": _COMMON_DESC,
    },
    "task_126": {
        "title": "Интерфейс/абстрактный тип",
        "short_goal": "Интерфейс/абстрактный тип.",
        "detailed_description": _COMMON_DESC,
    },
    "task_127": {
        "title": "Геометрические фигуры",
        "short_goal": "Геометрические фигуры.",
        "detailed_description": _COMMON_DESC,
    },
    "task_128": {
        "title": "Финальная: система доставки",
        "short_goal": "Финальная: система доставки.",
        "detailed_description": _COMMON_DESC,
    },
}

_CUSTOM_TESTS: dict[str, list[dict[str, str]]] = {
    "task_121": [{"inputs": "", "output": "woof"}],
    "task_122": [{"inputs": "", "output": "car drives\nbike rides"}],
    "task_123": [{"inputs": "", "output": "150000"}],
    "task_124": [{"inputs": "", "output": "email\nsms"}],
    "task_125": [{"inputs": "", "output": "16\n15"}],
    "task_126": [{"inputs": "", "output": "card 100\ncash 100"}],
    "task_127": [{"inputs": "", "output": "24"}],
    "task_128": [{"inputs": "", "output": "285"}],
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
    return importlib.import_module(f"ch16_user_codes.task_{task_num:03d}")


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
    for task_num in range(121, 129):
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
