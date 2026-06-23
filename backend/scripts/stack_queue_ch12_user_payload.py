"""Load chapter-12 (stack_queue) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "stack_queue"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

_COMMON_DESC = (
    "Программа использует порядок добавления и извлечения элементов для обработки команд."
)

# 89,90,93 assemble; 91,96 translation; 92,94,95 debug
_KIND_BY_PATTERN = {
    "task_089": "assemble",
    "task_090": "assemble",
    "task_091": "translation",
    "task_092": "debug",
    "task_093": "assemble",
    "task_094": "debug",
    "task_095": "debug",
    "task_096": "translation",
}

_FORMAT_BY_PATTERN = {
    "task_089": "сборка_программы",
    "task_090": "сборка_программы",
    "task_091": "перевод_программы",
    "task_092": "исправление",
    "task_093": "сборка_программы",
    "task_094": "исправление",
    "task_095": "исправление",
    "task_096": "перевод_программы",
}

_USER_META: dict[str, dict[str, str]] = {
    "task_089": {
        "title": "Проверка скобок",
        "short_goal": "Проверка скобок.",
        "detailed_description": _COMMON_DESC,
    },
    "task_090": {
        "title": "История браузера",
        "short_goal": "История браузера.",
        "detailed_description": (
            "Команды: visit page, back, current. "
            "Нужно поддерживать стек истории и выводить текущую страницу."
        ),
    },
    "task_091": {
        "title": "Очередь задач",
        "short_goal": "Очередь задач.",
        "detailed_description": (
            "Команды: add task, run. run выводит первую задачу из очереди, "
            "если очередь пустая — empty."
        ),
    },
    "task_092": {
        "title": "Отмена действий",
        "short_goal": "Отмена действий.",
        "detailed_description": (
            "Команды: do action, undo. undo выводит отменённое действие или nothing."
        ),
    },
    "task_093": {
        "title": "Очередь печати",
        "short_goal": "Очередь печати.",
        "detailed_description": (
            "Команды: print doc, next. next печатает первый документ или empty."
        ),
    },
    "task_094": {
        "title": "BFS через очередь",
        "short_goal": "BFS через очередь.",
        "detailed_description": (
            "Вводится граф: n m, затем m рёбер, затем стартовая вершина. "
            "Вывести порядок BFS."
        ),
    },
    "task_095": {
        "title": "Калькулятор выражений",
        "short_goal": "Калькулятор выражений.",
        "detailed_description": (
            "Упрощённый RPN-калькулятор. Вводится строка токенов: числа и операции +, -, *. "
            "Нужно вывести результат."
        ),
    },
    "task_096": {
        "title": "Итоговая: обработчик команд",
        "short_goal": "Итоговая: обработчик команд.",
        "detailed_description": (
            "Команды: push x, pop, front, enqueue x — стек и очередь одновременно."
        ),
    },
}

_CUSTOM_TESTS: dict[str, list[dict[str, str]]] = {
    "task_089": [
        {"inputs": "()\n", "output": "ok"},
        {"inputs": "(())\n", "output": "ok"},
        {"inputs": "(()\n", "output": "bad"},
    ],
    "task_090": [
        {"inputs": "2\nvisit news\ncurrent\n", "output": "news"},
        {"inputs": "3\nvisit a\nback\ncurrent\n", "output": "home"},
        {"inputs": "1\ncurrent\n", "output": "home"},
    ],
    "task_091": [
        {"inputs": "3\nadd t1\nadd t2\nrun\n", "output": "t1"},
        {"inputs": "1\nrun\n", "output": "empty"},
        {"inputs": "2\nadd x\nrun\n", "output": "x"},
    ],
    "task_092": [
        {"inputs": "2\ndo save\nundo\n", "output": "save"},
        {"inputs": "1\nundo\n", "output": "nothing"},
        {"inputs": "3\ndo a\ndo b\nundo\n", "output": "b"},
    ],
    "task_093": [
        {"inputs": "2\nprint doc\nnext\n", "output": "doc"},
        {"inputs": "1\nnext\n", "output": "empty"},
        {"inputs": "3\nprint a\nprint b\nnext\n", "output": "a"},
    ],
    "task_094": [
        {"inputs": "3 2\n0 1\n0 2\n0\n", "output": "0 1 2 "},
        {"inputs": "4 3\n0 1\n0 2\n1 3\n0\n", "output": "0 1 2 3 "},
        {"inputs": "1 0\n0\n", "output": "0 "},
    ],
    "task_095": [
        {"inputs": "3 4 +\n", "output": "7"},
        {"inputs": "2 3 * 4 +\n", "output": "10"},
        {"inputs": "5 1 -\n", "output": "4"},
    ],
    "task_096": [
        {"inputs": "2\nenqueue 7\nfront\n", "output": "7"},
        {"inputs": "1\npop\n", "output": "empty"},
        {"inputs": "4\npush 1\nenqueue 2\nfront\npop\n", "output": "2"},
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
    return importlib.import_module(f"ch12_user_codes.task_{task_num:03d}")


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
    for task_num in range(89, 97):
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
