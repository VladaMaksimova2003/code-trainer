"""Load chapter-14 (trees_graphs) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "trees_graphs"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

_COMMON_DESC = (
    "Программа представляет связи между объектами и выполняет обход или поиск."
)

_KIND_BY_PATTERN = {
    "task_105": "assemble",
    "task_106": "debug",
    "task_107": "translation",
    "task_108": "debug",
    "task_109": "assemble",
    "task_110": "debug",
    "task_111": "debug",
    "task_112": "translation",
}

_FORMAT_BY_PATTERN = {
    "task_105": "сборка_программы",
    "task_106": "исправление",
    "task_107": "перевод_программы",
    "task_108": "исправление",
    "task_109": "сборка_программы",
    "task_110": "исправление",
    "task_111": "исправление",
    "task_112": "перевод_программы",
}

_USER_META: dict[str, dict[str, str]] = {
    "task_105": {
        "title": "Создание дерева",
        "short_goal": "Создание дерева.",
        "detailed_description": _COMMON_DESC,
    },
    "task_106": {
        "title": "DFS дерева",
        "short_goal": "DFS дерева.",
        "detailed_description": _COMMON_DESC,
    },
    "task_107": {
        "title": "BFS дерева",
        "short_goal": "BFS дерева.",
        "detailed_description": _COMMON_DESC,
    },
    "task_108": {
        "title": "Поиск узла дерева",
        "short_goal": "Поиск узла дерева.",
        "detailed_description": _COMMON_DESC,
    },
    "task_109": {
        "title": "Представление графа",
        "short_goal": "Представление графа.",
        "detailed_description": _COMMON_DESC,
    },
    "task_110": {
        "title": "DFS графа",
        "short_goal": "DFS графа.",
        "detailed_description": _COMMON_DESC,
    },
    "task_111": {
        "title": "BFS графа",
        "short_goal": "BFS графа.",
        "detailed_description": _COMMON_DESC,
    },
    "task_112": {
        "title": "Итоговая: поиск пути на карте",
        "short_goal": "Итоговая: поиск пути на карте.",
        "detailed_description": _COMMON_DESC,
    },
}

_DEMO_OK_TESTS = [
    {"inputs": "demo\n", "output": "ok"},
    {"inputs": "empty\n", "output": "ok"},
    {"inputs": "edge\n", "output": "ok"},
]

_SUM_TESTS = [
    {"inputs": "5\n2\n9\n1\n7\n", "output": "19"},
    {"inputs": "1\n10\n", "output": "10"},
    {"inputs": "4\n-5\n-1\n-8\n-2\n", "output": "-16"},
]

_CUSTOM_TESTS: dict[str, list[dict[str, str]]] = {
    "task_105": _DEMO_OK_TESTS,
    "task_106": _DEMO_OK_TESTS,
    "task_107": _DEMO_OK_TESTS,
    "task_108": _DEMO_OK_TESTS,
    "task_109": _SUM_TESTS,
    "task_110": _DEMO_OK_TESTS,
    "task_111": _DEMO_OK_TESTS,
    "task_112": _SUM_TESTS,
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
    return importlib.import_module(f"ch14_user_codes.task_{task_num:03d}")


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
    for task_num in range(105, 113):
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
