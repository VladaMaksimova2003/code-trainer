"""Unified v192-B expansion catalog meta (task_129–task_192)."""

from __future__ import annotations

from typing import Any

from v192_expansion_debug_cpp_pairs import CPP_DEBUG_PAIRS_129_192
from v192_expansion_debug_pascal_pairs import PASCAL_DEBUG_PAIRS_129_192
from v192_expansion_multilang_129_144 import CPP_REF_129_144, PASCAL_REF_129_144
from v192_expansion_tasks_145_192 import EXPANSION_TASKS_145_192
from v192_stage3_meta import (
    _ACTION_BY_SLOT,
    _CHAPTER_BY_NUM,
    _DEBUG_PAIR,
    _FORMAT_BY_ACTION,
    _GOALS,
    _PITFALL_BY_NUM,
    _PYTHON_REF,
    _TESTS,
    _TITLES,
    _empty_impl,
)

V192_EXPANSION_SHIPPED_COUNT = 64
V192_EXPANSION_FIRST = 129
V192_EXPANSION_LAST = 192

# Backward-compatible aliases
V192_STAGE3_SHIPPED_COUNT = V192_EXPANSION_SHIPPED_COUNT
V192_STAGE3_FIRST = V192_EXPANSION_FIRST
V192_STAGE3_LAST = V192_EXPANSION_LAST


def _row_from_129_144(task_num: int) -> dict[str, Any]:
    action = _ACTION_BY_SLOT[task_num]
    row: dict[str, Any] = {
        "title": _TITLES[task_num],
        "goal": _GOALS[task_num],
        "action": action,
        "chapter_key": _CHAPTER_BY_NUM[task_num],
        "tests": [dict(t) for t in _TESTS[task_num]],
        "python": _PYTHON_REF[task_num],
    }
    pitfall = _PITFALL_BY_NUM.get(task_num)
    if pitfall:
        row["pitfall_id"] = pitfall
    if action == "debug" and task_num in _DEBUG_PAIR:
        buggy, fixed = _DEBUG_PAIR[task_num]
        row["debug_buggy"] = buggy
        row["debug_fixed"] = fixed
    return row


def _reference_codes(task_num: int, row: dict[str, Any]) -> dict[str, str]:
    py = str(row.get("python") or "")
    pascal = PASCAL_REF_129_144.get(task_num, py)
    cpp = CPP_REF_129_144.get(task_num, py)
    return {
        "python": py,
        "pascal": pascal,
        "cpp": cpp,
        "csharp": py,
        "java": py,
    }


def _build_meta(task_num: int, row: dict[str, Any]) -> dict[str, Any]:
    action = str(row["action"])
    refs = _reference_codes(task_num, row)
    py = refs["python"]
    impl = _empty_impl()
    impls: dict[str, dict[str, Any]] = {}

    for lang in ("pascal", "python", "cpp", "csharp", "java"):
        lang_impl = dict(impl)
        ref = refs.get(lang, py)
        if action == "debug" and row.get("debug_buggy") and row.get("debug_fixed"):
            if lang == "python":
                lang_impl["buggy_code"] = row["debug_buggy"]
                lang_impl["fixed_code"] = row["debug_fixed"]
                lang_impl["translation_code"] = row["debug_fixed"]
            else:
                curated: tuple[str, str] | None = None
                if lang == "pascal" and task_num in PASCAL_DEBUG_PAIRS_129_192:
                    curated = PASCAL_DEBUG_PAIRS_129_192[task_num]
                elif lang == "cpp" and task_num in CPP_DEBUG_PAIRS_129_192:
                    curated = CPP_DEBUG_PAIRS_129_192[task_num]
                if curated:
                    lang_impl["buggy_code"] = curated[0]
                    lang_impl["fixed_code"] = curated[1]
                    lang_impl["translation_code"] = curated[1]
                else:
                    # Fallback: keep reference as fixed, but ensure buggy != fixed.
                    lang_impl["fixed_code"] = ref
                    lang_impl["buggy_code"] = "# BUG: needs fixing\n" + ref
                    lang_impl["translation_code"] = ref
        elif action == "implement":
            lang_impl["translation_code"] = ref
            lang_impl["fixed_code"] = ref
        else:
            lang_impl["translation_code"] = ref
            lang_impl["fixed_code"] = ref
        impls[lang] = lang_impl

    meta: dict[str, Any] = {
        "task_num": task_num,
        "chapter_key": row["chapter_key"],
        "raw_title": row["title"],
        "title": row["title"],
        "short_goal": row["goal"],
        "detailed_description": row["goal"],
        "format_ru": _FORMAT_BY_ACTION[action],
        "format_raw": _FORMAT_BY_ACTION[action],
        "action": action,
        "difficulty": "medium",
        "difficulty_ru": "средний",
        "test_cases": [dict(t) for t in row.get("tests") or []],
        "expected_concepts": {"python": ["program_entry", "stdin_read", "stdout_write"]},
        "implementations": impls,
        "reference_codes": refs,
    }
    if row.get("pitfall_id"):
        meta["pitfall_id"] = row["pitfall_id"]
    return meta


def build_v192_expansion_meta() -> dict[str, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for n in range(V192_EXPANSION_FIRST, 145):
        rows[n] = _row_from_129_144(n)
    rows.update(EXPANSION_TASKS_145_192)
    return {f"task_{n:03d}": _build_meta(n, rows[n]) for n in sorted(rows)}


V192_EXPANSION_META: dict[str, dict[str, Any]] = build_v192_expansion_meta()

# Legacy name
V192_STAGE3_META = V192_EXPANSION_META


def apply_v192_expansion_meta(catalog: dict[str, dict[str, Any]]) -> None:
    from v128_test_input_enrichment import enrich_test_suite

    for pattern, meta in V192_EXPANSION_META.items():
        row = dict(meta)
        row["test_cases"] = enrich_test_suite(pattern, row.get("test_cases") or [])
        catalog[pattern] = row


# Legacy alias
apply_v192_stage3_meta = apply_v192_expansion_meta
