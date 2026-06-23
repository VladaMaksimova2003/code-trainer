"""Load chapter-4 (arrays_collections) user task definitions for DB import."""

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

CHAPTER_KEY = "arrays_collections"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

CH4_TASK_META: dict[str, dict[str, str]] = {
    "task_025": {
        "title": "Разворот массива",
        "goal": (
            "Даны n и n целых чисел. "
            "Выведите элементы массива в обратном порядке через пробел."
        ),
        "action": "assemble",
        "format_ru": "сборка_программы",
    },
    "task_026": {
        "title": "Циклический сдвиг вправо",
        "goal": (
            "Даны n, k и массив из n чисел. "
            "Циклически сдвиньте массив вправо на k позиций и выведите результат."
        ),
        "action": "assemble",
        "format_ru": "сборка_фрагмента",
    },
    "task_027": {
        "title": "Удаление элемента по позиции",
        "goal": (
            "Даны n, массив из n чисел и индекс pos (1-based). "
            "Удалите элемент на позиции pos и выведите новый массив. "
            "При pos вне 1..n выведите invalid."
        ),
        "action": "implement",
        "format_ru": "перевод_программы",
    },
    "task_028": {
        "title": "Вставка элемента по позиции",
        "goal": (
            "Даны n, массив, позиция pos (1-based) и значение x. "
            "Вставьте x на позицию pos и выведите массив. "
            "При pos вне 1..n+1 выведите invalid."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_029": {
        "title": "Объединение двух массивов",
        "goal": (
            "Даны размеры и элементы двух массивов. "
            "Объедините их в один и выведите через пробел."
        ),
        "action": "assemble",
        "format_ru": "сборка_программы",
    },
    "task_030": {
        "title": "Проверка дубликатов в массиве",
        "goal": (
            "Даны n и n чисел. "
            "Если в массиве есть одинаковые элементы — yes, иначе no."
        ),
        "action": "assemble",
        "format_ru": "сборка_фрагмента",
    },
    "task_031": {
        "title": "Слияние отсортированных массивов",
        "goal": (
            "Даны два отсортированных по неубыванию массива A (n чисел) и B (m чисел). "
            "Слейте их в один отсортированный массив и выведите элементы через пробел."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_032": {
        "title": "Итоговая: позиция вставки в массив",
        "goal": (
            "Даны n, отсортированный массив и число x. "
            "Найдите позицию вставки x (1-based) и выведите её."
        ),
        "action": "implement",
        "format_ru": "перевод_программы",
    },
}

_KIND_BY_PATTERN = {
    pid: "translation" if meta["action"] == "implement" else meta["action"]
    for pid, meta in CH4_TASK_META.items()
}


def _lines_stdin(*lines: str | int) -> str:
    return "\n".join(str(line) for line in lines) + "\n"


def _line_stdin(*tokens: str | int) -> str:
    return " ".join(str(t) for t in tokens) + "\n"


def _array_stdin(n: int, *values: int) -> str:
    return "\n".join([str(n), *[str(v) for v in values]]) + "\n"


def _shift_stdin(n: int, k: int, *values: int) -> str:
    return "\n".join([f"{n} {k}", *[str(v) for v in values]]) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    if pattern_id == "task_025":
        return [
            {"inputs": _array_stdin(4, 2, 9, 1, 7), "output": "7 1 9 2"},
            {"inputs": _array_stdin(1, 10), "output": "10"},
            {"inputs": _array_stdin(4, -5, -1, -8, -2), "output": "-2 -8 -1 -5"},
        ]
    if pattern_id == "task_026":
        return [
            {"inputs": _shift_stdin(5, 2, 1, 2, 3, 4, 5), "output": "4 5 1 2 3"},
            {"inputs": _shift_stdin(1, 3, 10), "output": "10"},
            {"inputs": _shift_stdin(3, 1, 1, 2, 3), "output": "3 1 2"},
            {"inputs": _shift_stdin(4, 4, 1, 2, 3, 4), "output": "1 2 3 4"},
        ]
    if pattern_id == "task_027":
        return [
            {"inputs": _lines_stdin(4, 1, 2, 3, 4, 2), "output": "1 3 4"},
            {"inputs": _lines_stdin(1, 10, 1), "output": ""},
            {"inputs": _lines_stdin(3, 5, 6, 7, 5), "output": "invalid"},
        ]
    if pattern_id == "task_028":
        return [
            {"inputs": _lines_stdin(3, 1, 2, 3, "2 9"), "output": "1 9 2 3"},
            {"inputs": _lines_stdin(1, 10, "1 5"), "output": "5 10"},
            {"inputs": _lines_stdin(2, 1, 2, "5 9"), "output": "invalid"},
        ]
    if pattern_id == "task_029":
        return [
            {"inputs": _lines_stdin(2, 1, 2, 2, 3, 4), "output": "1 2 3 4"},
            {"inputs": _lines_stdin(1, 10, 1, 20), "output": "10 20"},
            {"inputs": _lines_stdin(3, 4, 5, 6, 0), "output": "4 5 6"},
        ]
    if pattern_id == "task_030":
        return [
            {"inputs": _array_stdin(4, 1, 2, 3, 4), "output": "no"},
            {"inputs": _array_stdin(3, 1, 2, 2), "output": "yes"},
            {"inputs": _array_stdin(5, 1, 2, 3, 4, 1), "output": "yes"},
        ]
    if pattern_id == "task_031":
        return [
            {"inputs": "3 3\n1 3 5\n2 4 6\n", "output": "1 2 3 4 5 6"},
            {"inputs": "2 2\n1 2\n3 4\n", "output": "1 2 3 4"},
            {"inputs": "1 3\n5\n1 2 3\n", "output": "1 2 3 5"},
            {"inputs": "2 2\n-5 -1\n-3 -2\n", "output": "-5 -3 -2 -1"},
        ]
    if pattern_id == "task_032":
        return [
            {"inputs": _lines_stdin(4, 1, 3, 5, 7, 4), "output": "3"},
            {"inputs": _lines_stdin(3, 1, 2, 3, 0), "output": "1"},
            {"inputs": _lines_stdin(1, 10, 5), "output": "1"},
        ]
    raise KeyError(pattern_id)


def _user_meta(pattern_id: str) -> dict[str, str]:
    row = CH4_TASK_META[pattern_id]
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
    return importlib.import_module(f"ch4_user_codes.task_{task_num:03d}")


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
    for task_num in range(25, 33):
        pattern_id = f"task_{task_num:03d}"
        kind = _KIND_BY_PATTERN[pattern_id]
        mod = _load_code_module(task_num)
        payload = _codes_from_module(mod, kind)
        meta = _user_meta(pattern_id)
        catalog = CH4_TASK_META[pattern_id]
        item: dict[str, Any] = {
            "task_num": task_num,
            "pattern_id": pattern_id,
            "kind": kind,
            "task_format": catalog["format_ru"],
            "difficulty": _difficulty_from_course(pattern_id),
            "tests": _tests_for_pattern(pattern_id),
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
