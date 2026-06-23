"""Load chapter-10 (maps) user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

CHAPTER_KEY = "maps"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

# 73,76,77,78 assemble; 74,75 translation; 79,80 debug
_KIND_BY_PATTERN = {
    "task_073": "assemble",
    "task_074": "translation",
    "task_075": "translation",
    "task_076": "assemble",
    "task_077": "assemble",
    "task_078": "assemble",
    "task_079": "debug",
    "task_080": "debug",
}

_FORMAT_BY_PATTERN = {
    "task_073": "сборка_программы",
    "task_074": "перевод_программы",
    "task_075": "перевод_программы",
    "task_076": "сборка_программы",
    "task_077": "сборка_программы",
    "task_078": "сборка_фрагмента",
    "task_079": "исправление",
    "task_080": "исправление",
}

_USER_META: dict[str, dict[str, str]] = {
    "task_073": {
        "title": "Частотный словарь символов",
        "short_goal": "Частотный словарь символов.",
        "detailed_description": (
            "Программа хранит пары ключ-значение и использует ключи для быстрого доступа к данным."
        ),
    },
    "task_074": {
        "title": "Подсчёт слов",
        "short_goal": "Подсчёт слов.",
        "detailed_description": (
            "Дана строка из слов. Подсчитайте, сколько раз встречается каждое слово."
        ),
    },
    "task_075": {
        "title": "Телефонная книга",
        "short_goal": "Найдите телефон по имени.",
        "detailed_description": (
            "Вводится n, затем n пар name phone, затем имя для поиска. "
            "Если имя найдено — выведите телефон, иначе not found."
        ),
    },
    "task_076": {
        "title": "Индекс студентов по ID",
        "short_goal": "Найдите студента по id.",
        "detailed_description": (
            "Вводится n, затем n строк id name grade, затем id для поиска. "
            "Выведите name grade или not found."
        ),
    },
    "task_077": {
        "title": "Кэш запросов",
        "short_goal": "Кэшируйте повторяющиеся запросы.",
        "detailed_description": (
            "Вводится n, затем n запросов-строк. Если запрос уже был — выведите cached, "
            "иначе выведите new и добавьте его в кэш."
        ),
    },
    "task_078": {
        "title": "Группировка товаров по категории",
        "short_goal": "Сгруппируйте товары по категории.",
        "detailed_description": (
            "Вводится n, затем n строк category product. "
            "Нужно вывести категории и количество товаров в каждой категории."
        ),
    },
    "task_079": {
        "title": "Объединение двух словарей",
        "short_goal": "Объедините два словаря с суммированием значений.",
        "detailed_description": (
            "Вводится n, затем n пар key value, потом m, затем m пар key value. "
            "Если ключ повторяется, значения суммируются."
        ),
    },
    "task_080": {
        "title": "Итоговая: анализ текста через словарь",
        "short_goal": "Найдите самое частое слово.",
        "detailed_description": (
            "Вводится строка слов. Выведите самое частое слово и количество его повторений. "
            "Если таких несколько — выведите лексикографически меньшее."
        ),
    },
}


def _lines_stdin(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_073":
        return [
            {"inputs": "aabbcc\n", "output": _lines_stdin("a 2", "b 2", "c 2").rstrip("\n")},
            {"inputs": "z\n", "output": "z 1"},
            {"inputs": "Abc\n", "output": "b 1\nc 1"},
        ]
    if pattern_id == "task_074":
        return [
            {
                "inputs": "red blue red\n",
                "output": _lines_stdin("blue 1", "red 2").rstrip("\n"),
            },
            {"inputs": "a b c\n", "output": _lines_stdin("a 1", "b 1", "c 1").rstrip("\n")},
            {
                "inputs": "one one two\n",
                "output": _lines_stdin("one 2", "two 1").rstrip("\n"),
            },
        ]
    if pattern_id == "task_075":
        return [
            {
                "inputs": _lines_stdin("2", "Amy 111", "Bob 222", "Amy"),
                "output": "111",
            },
            {
                "inputs": _lines_stdin("1", "Solo 42", "Solo"),
                "output": "42",
            },
            {
                "inputs": _lines_stdin("1", "Solo 42", "Missing"),
                "output": "not found",
            },
        ]
    if pattern_id == "task_076":
        return [
            {
                "inputs": _lines_stdin("2", "s1 Ivan 5", "s2 Olya 4", "s1"),
                "output": "Ivan 5",
            },
            {
                "inputs": _lines_stdin("1", "x Ann 10", "x"),
                "output": "Ann 10",
            },
            {
                "inputs": _lines_stdin("1", "x Ann 10", "y"),
                "output": "not found",
            },
        ]
    if pattern_id == "task_077":
        return [
            {
                "inputs": _lines_stdin("3", "a", "a", "b"),
                "output": _lines_stdin("new", "cached", "new").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("2", "only", "only"),
                "output": _lines_stdin("new", "cached").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("2", "x", "y"),
                "output": _lines_stdin("new", "new").rstrip("\n"),
            },
        ]
    if pattern_id == "task_078":
        return [
            {
                "inputs": _lines_stdin("3", "food apple", "food banana", "book pen"),
                "output": _lines_stdin("book 1", "food 2").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("2", "zoo x", "apple y"),
                "output": _lines_stdin("apple 1", "zoo 1").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("1", "solo item"),
                "output": "solo 1",
            },
        ]
    if pattern_id == "task_079":
        return [
            {
                "inputs": _lines_stdin("2", "a 1", "b 2", "2", "a 3", "c 4"),
                "output": _lines_stdin("a 4", "b 2", "c 4").rstrip("\n"),
            },
            {
                "inputs": _lines_stdin("1", "x 5", "1", "x 7"),
                "output": "x 12",
            },
            {
                "inputs": _lines_stdin("0", "2", "p 1", "q 2"),
                "output": _lines_stdin("p 1", "q 2").rstrip("\n"),
            },
        ]
    if pattern_id == "task_080":
        return [
            {"inputs": "red blue red\n", "output": "red 2"},
            {"inputs": "a a b\n", "output": "a 2"},
            {"inputs": "solo\n", "output": "solo 1"},
        ]
    raise KeyError(pattern_id)


def _load_code_module(task_num: int):
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch10_user_codes.task_{task_num:03d}")


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
    for task_num in range(73, 81):
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
            "tests": _tests_for_pattern(pattern_id),
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
