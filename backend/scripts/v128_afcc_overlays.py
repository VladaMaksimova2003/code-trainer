"""AFCC contrast test overlays for v128/v192 demo slots (stage 5)."""

from __future__ import annotations

from typing import Any

# pitfall_id round_semantics → index 1 must expose avg .5 (div vs Round).
_ROUND_SEMANTICS_CONTRAST_CASE = {
    "inputs": "2\n1\n4\n",
    "tag": "contrast",
    "input_kind": "array",
    "mplt_contrast": True,
}

# task_008: max, integer average (div), count >= 3
_TASK_008_CONTRAST = {
    **_ROUND_SEMANTICS_CONTRAST_CASE,
    "output": "4 2 1",
}

# task_163 (expansion debug): Round(average) — Pascal Round(2.5)=3, trunc=2
_TASK_163_CONTRAST = {
    **_ROUND_SEMANTICS_CONTRAST_CASE,
    "output": "3",
}

# task_027: delete at pos — contrast exposes static-array vs Python list semantics
_TASK_027_CONTRAST = {
    "inputs": "3\n1\n2\n3\n3\n",
    "output": "1 2",
    "tag": "contrast",
    "input_kind": "array",
    "mplt_contrast": True,
}


def _patch_contrast_case(
    meta: dict[str, dict[str, Any]],
    pattern: str,
    *,
    index: int,
    case: dict[str, Any],
) -> None:
    row = meta.get(pattern)
    if not row:
        return
    tests = [dict(item) for item in (row.get("test_cases") or [])]
    if len(tests) <= index:
        return
    tests[index] = dict(case)
    row["test_cases"] = tests


def apply_afcc_overlays(meta: dict[str, dict[str, Any]]) -> None:
    """Patch contrast-index test cases for AFCC demo slots."""
    _patch_contrast_case(meta, "task_008", index=1, case=_TASK_008_CONTRAST)
    _patch_contrast_case(meta, "task_163", index=1, case=_TASK_163_CONTRAST)
    _patch_contrast_case(meta, "task_027", index=0, case=_TASK_027_CONTRAST)

    row = meta.get("task_003")
    if row and row.get("test_cases"):
        tests = [dict(item) for item in row["test_cases"]]
        if tests:
            tests[0] = {**tests[0], "mplt_contrast": True, "tag": tests[0].get("tag") or "typical"}
            row["test_cases"] = tests
