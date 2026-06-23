"""Load chapter-5 (strings) user task definitions for DB import."""

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

CHAPTER_KEY = "strings"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

CH5_TASK_META: dict[str, dict[str, str]] = {
    "task_033": {
        "title": "Подсчёт символов",
        "goal": "Дана строка s. Подсчитайте количество символов и выведите число.",
        "action": "assemble",
        "format_ru": "сборка_программы",
    },
    "task_034": {
        "title": "Разворот строки",
        "goal": "Дана строка s. Выведите её в обратном порядке.",
        "action": "assemble",
        "format_ru": "сборка_фрагмента",
    },
    "task_035": {
        "title": "Проверка палиндрома",
        "goal": "Дана строка s. Если s — палиндром, выведите yes, иначе no.",
        "action": "implement",
        "format_ru": "перевод_программы",
    },
    "task_036": {
        "title": "Первое вхождение подстроки",
        "goal": (
            "Даны строка s и подстрока p. "
            "Найдите первое вхождение p в s и выведите индекс (1-based) или 0."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_037": {
        "title": "Подсчёт слов в строке",
        "goal": (
            "Дана строка из слов, разделённых пробелами. "
            "Подсчитайте количество слов и выведите его."
        ),
        "action": "assemble",
        "format_ru": "сборка_программы",
    },
    "task_038": {
        "title": "Проверка анаграммы",
        "goal": (
            "Даны две строки. "
            "Определите, являются ли они анаграммами, и выведите yes или no."
        ),
        "action": "assemble",
        "format_ru": "сборка_фрагмента",
    },
    "task_039": {
        "title": "RLE-сжатие строки",
        "goal": (
            "Дана строка s. "
            "Выполните RLE-сжатие: каждую группу одинаковых символов "
            "замените символом и длиной группы."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_040": {
        "title": "Итоговая: анализ текста",
        "goal": (
            "Дана строка текста. "
            "Выведите количество символов, слов и гласных букв."
        ),
        "action": "implement",
        "format_ru": "перевод_программы",
    },
}

_KIND_BY_PATTERN = {
    pid: "translation" if meta["action"] == "implement" else meta["action"]
    for pid, meta in CH5_TASK_META.items()
}


def _line_stdin(text: str) -> str:
    return text + "\n"


def _lines_stdin(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_033":
        return [
            {"inputs": _line_stdin("hello"), "output": "5"},
            {"inputs": _line_stdin("a"), "output": "1"},
            {"inputs": _line_stdin("abc def"), "output": "7"},
            {"inputs": "\n", "output": "0"},
        ]
    if pattern_id == "task_034":
        return [
            {"inputs": _line_stdin("abba"), "output": "abba"},
            {"inputs": _line_stdin("abc"), "output": "cba"},
            {"inputs": _line_stdin("aaabb"), "output": "bbaaa"},
        ]
    if pattern_id == "task_035":
        return [
            {"inputs": _line_stdin("abba"), "output": "yes"},
            {"inputs": _line_stdin("abc"), "output": "no"},
            {"inputs": _line_stdin("aaabb"), "output": "no"},
        ]
    if pattern_id == "task_036":
        return [
            {"inputs": _lines_stdin("hello", "ll"), "output": "3"},
            {"inputs": _lines_stdin("abc", "z"), "output": "0"},
            {"inputs": _lines_stdin("ababab", "ab"), "output": "1"},
        ]
    if pattern_id == "task_037":
        return [
            {"inputs": _line_stdin("one two three"), "output": "3"},
            {"inputs": "\n", "output": "0"},
            {"inputs": _line_stdin("word"), "output": "1"},
        ]
    if pattern_id == "task_038":
        return [
            {"inputs": _lines_stdin("listen", "silent"), "output": "yes"},
            {"inputs": _lines_stdin("abc", "cba"), "output": "yes"},
            {"inputs": _lines_stdin("abc", "abd"), "output": "no"},
        ]
    if pattern_id == "task_039":
        return [
            {"inputs": _line_stdin("aaabb"), "output": "a3b2"},
            {"inputs": _line_stdin("abba"), "output": "a1b2a1"},
            {"inputs": _line_stdin("abc"), "output": "a1b1c1"},
        ]
    if pattern_id == "task_040":
        return [
            {"inputs": _line_stdin("abba"), "output": "4 1 2"},
            {"inputs": _line_stdin("abc"), "output": "3 1 1"},
            {"inputs": _line_stdin("a a"), "output": "3 2 2"},
        ]
    raise KeyError(pattern_id)


def _user_meta(pattern_id: str) -> dict[str, str]:
    row = CH5_TASK_META[pattern_id]
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
    return importlib.import_module(f"ch5_user_codes.task_{task_num:03d}")


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
    for task_num in range(33, 41):
        pattern_id = f"task_{task_num:03d}"
        kind = _KIND_BY_PATTERN[pattern_id]
        mod = _load_code_module(task_num)
        payload = _codes_from_module(mod, kind)
        catalog = CH5_TASK_META[pattern_id]
        item: dict[str, Any] = {
            "task_num": task_num,
            "pattern_id": pattern_id,
            "kind": kind,
            "task_format": catalog["format_ru"],
            "difficulty": _difficulty_from_course(pattern_id),
            "tests": _tests_for_pattern(pattern_id),
            **_user_meta(pattern_id),
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
