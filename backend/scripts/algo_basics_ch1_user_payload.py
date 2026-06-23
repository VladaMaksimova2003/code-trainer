"""Load chapter-1 user task definitions for DB import."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

CHAPTER_KEY = "algo_basics"
_LANGS = ("pascal", "python", "cpp", "csharp", "java")
_CODE_DIR = Path(__file__).resolve().parent / "ch1_user_codes"
_COURSE_JSON = Path(__file__).resolve().parents[1] / "algo_syntax_course.json"

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from algo_v128_catalog import _TASK_INDEX  # noqa: E402
from application.curriculum.display.chapter1_algo_basics_hints import (  # noqa: E402
    chapter1_hints_for_pattern,
)

_ACTION_TO_KIND = {
    "assemble": "assemble",
    "debug": "debug",
    "implement": "implement",
}


def _stdin_from_tokens(raw: str, *, pattern_id: str = "") -> str:
    from application.curriculum.content.v4_test_cases_io import normalize_test_case_inputs

    return normalize_test_case_inputs(
        raw,
        pattern_id=pattern_id,
    )


def _tests_for_pattern(pattern_id: str) -> list[dict[str, str]]:
    """Authoritative chapter-1 test cases (inputs use trailing newline)."""
    raw_cases: dict[str, list[tuple[str, str]]] = {
        "task_002": [
            ("5 12 8 3 12 5 9", "3"),
            ("3 7 1 2 3", "0"),
            ("4 5 5 5 1 2", "1"),
            ("1 42 42", "1"),
        ],
        "task_005": [
            ("5 2 9 1 7 4", "23"),
            ("1 10", "10"),
            ("4 -5 10 -2 1", "4"),
            ("3 0 0 0", "0"),
        ],
        "task_006": [
            ("5 10 20 30 40 50", "30"),
            ("1 7", "7"),
            ("4 0 0 10 10", "5"),
            ("3 5 5 5", "5"),
        ],
        "task_001": [
            ("4 2 9 1 7", "9"),
            ("1 4", "4"),
            ("4 -5 -1 -8 -3", "-1"),
            ("3 10 10 5", "10"),
        ],
        "task_004": [
            ("5 100 -20 0 50 -1", "2"),
            ("3 -5 -1 0", "0"),
            ("4 1 2 3 4", "4"),
            ("2 0 0", "0"),
        ],
        "task_007": [
            ("5 40 50 60 10 70", "3"),
            ("3 1 2 3", "0"),
            ("4 50 50 49 51", "3"),
            ("4 50 50 50 50", "4"),
        ],
        "task_129": [
            ("12345", "15"),
            ("7", "7"),
            ("-123", "6"),
            ("1000", "1"),
        ],
        "task_008": [
            ("5 5 2 4 1 3", "5 3 3"),
            ("3 2 2 2", "2 2 0"),
            ("4 5 4 3 5", "5 4 4"),
            ("1 3", "3 3 1"),
        ],
    }
    if pattern_id == "task_129":
        return [{"inputs": f"{inp}\n", "output": out} for inp, out in raw_cases[pattern_id]]
    return [
        {"inputs": _stdin_from_tokens(inp, pattern_id=pattern_id), "output": out}
        for inp, out in raw_cases[pattern_id]
    ]


def _load_code_module(pattern_id: str):
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module(f"ch1_user_codes.{pattern_id}")


def _codes_from_module(mod, kind: str) -> dict[str, Any]:
    if hasattr(mod, "FIXED_PASCAL") or hasattr(mod, "BUGGY_PASCAL"):
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
        return {"fixed": fixed, "buggy": buggy, "kind": "debug"}
    return {
        "codes": {
            "pascal": mod.PASCAL,
            "python": mod.PYTHON,
            "cpp": mod.CPP,
            "csharp": mod.CSHARP,
            "java": mod.JAVA,
        },
        "kind": kind if kind != "debug" else "assemble",
    }


def _meta_from_catalog(row: dict[str, Any]) -> dict[str, str]:
    pattern_id = str(row["pattern_id"])
    try:
        rows = json.loads(_COURSE_JSON.read_text(encoding="utf-8"))
        course_row = next(r for r in rows if r.get("pattern_id") == pattern_id)
        return {
            "title": str(course_row["title"]),
            "short_goal": str(course_row["short_goal"]),
            "detailed_description": str(course_row["detailed_description"]),
            "difficulty": str(course_row["difficulty"]),
        }
    except (StopIteration, FileNotFoundError, json.JSONDecodeError):
        return {
            "title": str(row["title"]),
            "short_goal": str(row["title"]),
            "detailed_description": str(row["goal"]),
            "difficulty": str(row["difficulty"]),
        }


def _ch1_catalog_rows() -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in _TASK_INDEX
        if row.get("chapter_key") == CHAPTER_KEY and 1 <= int(row.get("task_num") or 0) <= 8
    ]


def build_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for row in sorted(_ch1_catalog_rows(), key=lambda r: int(r["task_num"])):
        pattern_id = str(row["pattern_id"])
        action = str(row["action"])
        task_format = str(row.get("format_ru") or "")
        kind = _ACTION_TO_KIND.get(action, "assemble")
        mod = _load_code_module(pattern_id)
        payload = _codes_from_module(mod, kind)
        kind = str(payload.pop("kind", kind))
        meta = _meta_from_catalog(row)
        hints = chapter1_hints_for_pattern(pattern_id)
        item: dict[str, Any] = {
            "task_num": int(row["task_num"]),
            "pattern_id": pattern_id,
            "kind": kind,
            "action": action,
            "task_format": task_format,
            "features": str(row.get("features") or ""),
            "tests": _tests_for_pattern(pattern_id),
            "hints": hints,
            **meta,
            **payload,
        }
        tasks.append(item)
    return tasks


TASKS = build_tasks()
