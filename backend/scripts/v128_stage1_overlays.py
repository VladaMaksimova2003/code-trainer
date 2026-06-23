"""Stage 1 overlays merged into ALGO_SYNTAX_META at catalog load time.

P0: branches chapter (task_009–task_016) — real test_cases + reference from ch2_user_codes.
P0: loops chapter (task_017–task_024) — real test_cases + reference from ch3_user_codes.
P0: arrays chapter (task_025–task_032) — real test_cases + reference from ch4_user_codes.
P0: strings chapter (task_033–task_040) — real test_cases + reference from ch5_user_codes.
P1: pitfall_id on high-priority debug slots (basics already OK in transfer meta).
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from branches_ch2_user_payload import CH2_TASK_META, _tests_for_pattern as ch2_tests_for_pattern  # noqa: E402
from loops_ch3_user_payload import CH3_TASK_META, _tests_for_pattern as ch3_tests_for_pattern  # noqa: E402
from arrays_ch4_user_payload import CH4_TASK_META, _tests_for_pattern as ch4_tests_for_pattern  # noqa: E402
from strings_ch5_user_payload import CH5_TASK_META, _tests_for_pattern as ch5_tests_for_pattern  # noqa: E402

_LANGS = ("pascal", "python", "cpp", "csharp", "java")
_LANG_ATTR = {
    "pascal": "PASCAL",
    "python": "PYTHON",
    "cpp": "CPP",
    "csharp": "CSHARP",
    "java": "JAVA",
}
_FIXED_ATTR = {
    "pascal": "FIXED_PASCAL",
    "python": "FIXED_PYTHON",
    "cpp": "FIXED_CPP",
    "csharp": "FIXED_CSHARP",
    "java": "FIXED_JAVA",
}
_BUGGY_ATTR = {
    "pascal": "BUGGY_PASCAL",
    "python": "BUGGY_PYTHON",
    "cpp": "BUGGY_CPP",
    "csharp": "BUGGY_CSHARP",
    "java": "BUGGY_JAVA",
}

# Catalog primary_action aligned with ch2_user_codes (debug slots have buggy/fixed pairs).
_CH2_CATALOG_ACTION: dict[str, str] = {
    pid: meta["action"] for pid, meta in CH2_TASK_META.items()
}

_PITFALL_BY_PATTERN: dict[str, str] = {
    "task_004": "filter_positive",
    "task_006": "integer_division",
    "task_007": "threshold_count",
    "task_012": "branch_logic",
    "task_015": "multi_branch_discount",
    "task_020": "for_range_off_by_one",
    "task_028": "index_1based",
}


def _empty_impl() -> dict[str, Any]:
    return {
        "assembly_blocks": [],
        "placeholder_code": "",
        "gaps": [],
        "translation_code": "",
        "buggy_code": "",
        "fixed_code": "",
        "error_descriptions": [],
    }


def _load_ch2_module(task_num: int):
    return importlib.import_module(f"ch2_user_codes.task_{task_num:03d}")


def _load_ch3_module(task_num: int):
    return importlib.import_module(f"ch3_user_codes.task_{task_num:03d}")


def _load_ch4_module(task_num: int):
    return importlib.import_module(f"ch4_user_codes.task_{task_num:03d}")


def _load_ch5_module(task_num: int):
    return importlib.import_module(f"ch5_user_codes.task_{task_num:03d}")


def _reference_from_module(mod, lang: str) -> str:
    fixed_key = _FIXED_ATTR[lang]
    plain_key = _LANG_ATTR[lang]
    if hasattr(mod, fixed_key):
        return str(getattr(mod, fixed_key)).strip()
    return str(getattr(mod, plain_key)).strip()


def _build_implementations(mod, action: str) -> dict[str, dict[str, Any]]:
    impls: dict[str, dict[str, Any]] = {}
    for lang in _LANGS:
        row = _empty_impl()
        ref = _reference_from_module(mod, lang)
        if action == "debug":
            row["buggy_code"] = str(getattr(mod, _BUGGY_ATTR[lang])).strip()
            row["fixed_code"] = str(getattr(mod, _FIXED_ATTR[lang])).strip()
            row["translation_code"] = row["fixed_code"]
        elif action == "implement":
            row["translation_code"] = ref
            row["fixed_code"] = ref
        else:
            row["translation_code"] = ref
            row["fixed_code"] = ref
        impls[lang] = row
    return impls


def _reference_codes(mod) -> dict[str, str]:
    return {lang: _reference_from_module(mod, lang) for lang in _LANGS}


def build_branches_ch2_overlay() -> dict[str, dict[str, Any]]:
    overlay: dict[str, dict[str, Any]] = {}
    for task_num in range(9, 17):
        pattern = f"task_{task_num:03d}"
        mod = _load_ch2_module(task_num)
        action = _CH2_CATALOG_ACTION[pattern]
        patch: dict[str, Any] = {
            "test_cases": ch2_tests_for_pattern(pattern),
            "reference_codes": _reference_codes(mod),
            "implementations": _build_implementations(mod, action),
            "action": action,
            "format_ru": CH2_TASK_META[pattern]["format_ru"],
            "title": CH2_TASK_META[pattern]["title"],
            "short_goal": CH2_TASK_META[pattern]["goal"],
            "detailed_description": CH2_TASK_META[pattern]["goal"],
        }
        from application.curriculum.display.chapter2_branches_expected_concepts import (
            chapter2_expected_concepts_for_pattern,
        )

        concepts = chapter2_expected_concepts_for_pattern(pattern)
        if concepts:
            patch["expected_concepts"] = concepts
        pitfall_id = _PITFALL_BY_PATTERN.get(pattern)
        if pitfall_id:
            patch["pitfall_id"] = pitfall_id
        overlay[pattern] = patch
    return overlay


def build_loops_ch3_overlay() -> dict[str, dict[str, Any]]:
    """P0/P2: loops chapter (task_017–task_024) — real tests + reference from ch3_user_codes."""
    from application.curriculum.display.chapter3_loops_pitfalls import (
        chapter3_binding_overrides,
    )

    ch3_bindings = chapter3_binding_overrides()
    overlay: dict[str, dict[str, Any]] = {}
    for task_num in range(17, 25):
        pattern = f"task_{task_num:03d}"
        mod = _load_ch3_module(task_num)
        action = CH3_TASK_META[pattern]["action"]
        meta = CH3_TASK_META[pattern]
        patch: dict[str, Any] = {
            "test_cases": ch3_tests_for_pattern(pattern),
            "reference_codes": _reference_codes(mod),
            "implementations": _build_implementations(mod, action),
            "action": action,
            "format_ru": meta["format_ru"],
            "title": meta["title"],
            "short_goal": meta["goal"].split(".")[0].strip() + ".",
            "detailed_description": meta["goal"],
        }
        binding = ch3_bindings.get(pattern) or {}
        pitfall_id = binding.get("dominant_pitfall_id")
        if pitfall_id:
            patch["pitfall_id"] = pitfall_id
        overlay[pattern] = patch
    return overlay


def build_arrays_ch4_overlay() -> dict[str, dict[str, Any]]:
    """P0/P2: arrays chapter (task_025–task_032) — real tests + reference from ch4_user_codes."""
    from application.curriculum.display.chapter4_arrays_pitfalls import (
        chapter4_binding_overrides,
    )

    ch4_bindings = chapter4_binding_overrides()
    overlay: dict[str, dict[str, Any]] = {}
    for task_num in range(25, 33):
        pattern = f"task_{task_num:03d}"
        mod = _load_ch4_module(task_num)
        action = CH4_TASK_META[pattern]["action"]
        meta = CH4_TASK_META[pattern]
        patch: dict[str, Any] = {
            "test_cases": ch4_tests_for_pattern(pattern),
            "reference_codes": _reference_codes(mod),
            "implementations": _build_implementations(mod, action),
            "action": action,
            "format_ru": meta["format_ru"],
            "title": meta["title"],
            "short_goal": meta["goal"].split(".")[0].strip() + ".",
            "detailed_description": meta["goal"],
        }
        binding = ch4_bindings.get(pattern) or {}
        pitfall_id = binding.get("dominant_pitfall_id")
        if pitfall_id:
            patch["pitfall_id"] = pitfall_id
        overlay[pattern] = patch
    return overlay


def build_strings_ch5_overlay() -> dict[str, dict[str, Any]]:
    """P0/P2: strings chapter (task_033–task_040) — real tests + reference from ch5_user_codes."""
    from application.curriculum.display.chapter5_strings_pitfalls import (
        chapter5_binding_overrides,
    )

    ch5_bindings = chapter5_binding_overrides()
    overlay: dict[str, dict[str, Any]] = {}
    for task_num in range(33, 41):
        pattern = f"task_{task_num:03d}"
        mod = _load_ch5_module(task_num)
        action = CH5_TASK_META[pattern]["action"]
        meta = CH5_TASK_META[pattern]
        patch: dict[str, Any] = {
            "test_cases": ch5_tests_for_pattern(pattern),
            "reference_codes": _reference_codes(mod),
            "implementations": _build_implementations(mod, action),
            "action": action,
            "format_ru": meta["format_ru"],
            "title": meta["title"],
            "short_goal": meta["goal"].split(".")[0].strip() + ".",
            "detailed_description": meta["goal"],
        }
        binding = ch5_bindings.get(pattern) or {}
        pitfall_id = binding.get("dominant_pitfall_id")
        if pitfall_id:
            patch["pitfall_id"] = pitfall_id
        overlay[pattern] = patch
    return overlay


def _basics_pitfall_meta_overlay() -> dict[str, dict[str, Any]]:
    return {
        pattern: {"pitfall_id": pitfall_id}
        for pattern, pitfall_id in _PITFALL_BY_PATTERN.items()
        if pattern in {"task_004", "task_006", "task_007"}
    }


def _debug_buggy_fixed_sanity_overlay() -> dict[str, dict[str, Any]]:
    """Fix legacy slots where python buggy_code == fixed_code.

    Stage-1 readiness criterion: debug tasks must contain a meaningful diff.
    """

    # task_060 — bubble sort ascending integers
    fixed_060 = (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "for i in range(n):\n"
        "    for j in range(0, n - 1 - i):\n"
        "        if a[j] > a[j + 1]:\n"
        "            a[j], a[j + 1] = a[j + 1], a[j]\n"
        "print(' '.join(str(x) for x in a))"
    )
    buggy_060 = (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "for i in range(n):\n"
        "    for j in range(0, n - 1 - i):\n"
        "        # BUG: wrong comparison -> sorts descending\n"
        "        if a[j] < a[j + 1]:\n"
        "            a[j], a[j + 1] = a[j + 1], a[j]\n"
        "print(' '.join(str(x) for x in a))"
    )

    # task_063 — sort descending integers (legacy goal) using bubble sort
    fixed_063 = (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "for i in range(n):\n"
        "    for j in range(0, n - 1 - i):\n"
        "        if a[j] < a[j + 1]:\n"
        "            a[j], a[j + 1] = a[j + 1], a[j]\n"
        "print(' '.join(str(x) for x in a))"
    )
    buggy_063 = (
        "n = int(input())\n"
        "a = [int(input()) for _ in range(n)]\n"
        "for i in range(n):\n"
        "    for j in range(0, n - 1 - i):\n"
        "        # BUG: wrong comparison -> sorts ascending\n"
        "        if a[j] > a[j + 1]:\n"
        "            a[j], a[j + 1] = a[j + 1], a[j]\n"
        "print(' '.join(str(x) for x in a))"
    )

    impl = _empty_impl()
    return {
        "task_060": {
            "implementations": {
                "python": {**impl, "buggy_code": buggy_060, "fixed_code": fixed_060, "translation_code": fixed_060},
            },
            "reference_codes": {"python": fixed_060},
        },
        "task_063": {
            "implementations": {
                "python": {**impl, "buggy_code": buggy_063, "fixed_code": fixed_063, "translation_code": fixed_063},
            },
            "reference_codes": {"python": fixed_063},
        },
    }


def build_stage1_overlays() -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for part in (
        build_branches_ch2_overlay(),
        build_loops_ch3_overlay(),
        build_arrays_ch4_overlay(),
        build_strings_ch5_overlay(),
        _basics_pitfall_meta_overlay(),
        _debug_buggy_fixed_sanity_overlay(),
    ):
        merged.update(part)
    return merged


STAGE1_OVERLAYS: dict[str, dict[str, Any]] = build_stage1_overlays()


def merge_task_meta(base: dict[str, Any], patch: dict[str, Any]) -> None:
    """Deep-merge patch into an ALGO_SYNTAX_META task entry."""
    for key, value in patch.items():
        if key == "implementations" and isinstance(value, dict):
            impl_root = base.setdefault("implementations", {})
            for lang, lang_patch in value.items():
                if isinstance(impl_root.get(lang), dict) and isinstance(lang_patch, dict):
                    impl_root[lang].update(lang_patch)
                else:
                    impl_root[lang] = lang_patch
        elif key == "reference_codes" and isinstance(value, dict):
            refs = base.setdefault("reference_codes", {})
            refs.update(value)
        elif key == "expected_concepts" and isinstance(value, dict):
            concepts = base.setdefault("expected_concepts", {})
            for lang, items in value.items():
                concepts[lang] = items
        else:
            base[key] = value


def apply_stage1_overlays(meta: dict[str, dict[str, Any]]) -> None:
    for pattern, patch in STAGE1_OVERLAYS.items():
        if pattern not in meta:
            continue
        merge_task_meta(meta[pattern], patch)
