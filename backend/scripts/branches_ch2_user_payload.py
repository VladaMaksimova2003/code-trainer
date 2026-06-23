"""Load chapter-2 (branches) user task definitions for DB import."""

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

from application.curriculum.display.chapter2_branches_hints import (  # noqa: E402
    chapter2_hints_for_pattern,
)

CHAPTER_KEY = "branches"
_CODE_DIR = Path(__file__).resolve().parent / "ch2_user_codes"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

# Canonical chapter-2 metadata (single source for import + catalog overlays).
CH2_TASK_META: dict[str, dict[str, str]] = {
    "task_009": {
        "title": "Максимум из трёх чисел",
        "goal": "Даны три целых числа. Найдите и выведите максимальное из них.",
        "action": "assemble",
        "format_ru": "сборка_программы",
    },
    "task_010": {
        "title": "Классификация температуры",
        "goal": (
            "Дана температура t (целое). Если t < 0 — freezing; если t ≤ 25 — normal; "
            "если t ≤ 35 — hot; иначе — danger."
        ),
        "action": "assemble",
        "format_ru": "сборка_фрагмента",
    },
    "task_011": {
        "title": "Тип треугольника",
        "goal": (
            "Даны три стороны a, b, c. Если треугольник некорректен — invalid; "
            "если все равны — equilateral; если две равны — isosceles; иначе — scalene."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_012": {
        "title": "Проверка корректности даты",
        "goal": (
            "Даны день d, месяц m и год y. Проверьте корректность даты с учётом високосных лет "
            "и выведите valid или invalid."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_013": {
        "title": "Оценка по баллам",
        "goal": (
            "Дано количество баллов (0–100). Выведите excellent, good, satisfactory, retry или invalid."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_014": {
        "title": "Определение сезона",
        "goal": (
            "Дан номер месяца (1–12). Выведите winter, spring, summer, autumn или invalid."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_015": {
        "title": "Система скидок",
        "goal": (
            "Даны сумма покупки, флаги isStudent и hasCoupon (0/1). "
            "Выведите итоговую скидку в процентах (0–30) или invalid."
        ),
        "action": "debug",
        "format_ru": "исправление",
    },
    "task_016": {
        "title": "Итоговая: валидация заявки",
        "goal": (
            "Даны age, income, debt, score. Выведите accepted, review или rejected по правилам заявки."
        ),
        "action": "implement",
        "format_ru": "перевод_программы",
    },
}

_KIND_BY_PATTERN = {
    pid: "translation" if meta["action"] == "implement" else meta["action"]
    for pid, meta in CH2_TASK_META.items()
}

_FORMAT_BY_KIND = {
    "assemble": "сборка_программы",
    "debug": "исправление",
    "translation": "перевод_программы",
}

_CH2_RAW_TESTS: dict[str, list[tuple[str, str]]] = {
    "task_009": [
        ("3 7 2", "7"),
        ("1 5 3", "5"),
        ("-1 -5 -2", "-1"),
        ("5 5 5", "5"),
    ],
    "task_010": [
        ("-5", "freezing"),
        ("15", "normal"),
        ("30", "hot"),
        ("40", "danger"),
    ],
    "task_011": [
        ("3 4 5", "scalene"),
        ("2 2 2", "equilateral"),
        ("3 3 5", "isosceles"),
        ("1 2 4", "invalid"),
    ],
    "task_012": [
        ("29 2 2024", "valid"),
        ("31 4 2023", "invalid"),
        ("15 13 2023", "invalid"),
        ("28 2 2023", "valid"),
    ],
    "task_013": [
        ("95", "excellent"),
        ("75", "good"),
        ("55", "satisfactory"),
        ("40", "retry"),
        ("150", "invalid"),
    ],
    "task_014": [
        ("12", "winter"),
        ("4", "spring"),
        ("7", "summer"),
        ("13", "invalid"),
    ],
    "task_015": [
        ("25000 1 1", "30"),
        ("3000 0 0", "0"),
        ("10000 0 1", "18"),
        ("-1 0 0", "invalid"),
    ],
    "task_016": [
        ("25 35000 10000 700", "accepted"),
        ("20 25000 8000 600", "review"),
        ("17 10000 5000 400", "rejected"),
        ("18 30000 10000 650", "accepted"),
    ],
}


def _line_stdin(*tokens: str | int) -> str:
    return " ".join(str(t) for t in tokens) + "\n"


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    return [{"inputs": _line_stdin(*inp.split()), "output": out} for inp, out in _CH2_RAW_TESTS[pattern_id]]


def _user_meta(pattern_id: str) -> dict[str, str]:
    row = CH2_TASK_META[pattern_id]
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
    import sys

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch2_user_codes.task_{task_num:03d}")


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
    for task_num in range(9, 17):
        pattern_id = f"task_{task_num:03d}"
        kind = _KIND_BY_PATTERN[pattern_id]
        mod = _load_code_module(task_num)
        payload = _codes_from_module(mod, kind)
        meta = _user_meta(pattern_id)
        catalog = CH2_TASK_META[pattern_id]
        item: dict[str, Any] = {
            "task_num": task_num,
            "pattern_id": pattern_id,
            "kind": kind,
            "task_format": catalog["format_ru"],
            "difficulty": _difficulty_from_course(pattern_id),
            "tests": _tests_for_pattern(pattern_id),
            "hints": chapter2_hints_for_pattern(pattern_id),
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
