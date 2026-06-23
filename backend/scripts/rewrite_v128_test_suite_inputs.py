#!/usr/bin/env python3
"""Rewrite v128_test_suites_data.py inputs using pattern-aware stdin layouts."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "scripts"))

from application.curriculum.content.v4_test_cases_io import normalize_test_case_inputs
from algo_v128_catalog import ALGO_SYNTAX_META, _TASK_INDEX
from v128_test_suites_data import V128_TEST_SUITES

DATA_PATH = Path(__file__).resolve().parent / "v128_test_suites_data.py"


def _goal_by_pattern() -> dict[str, str]:
    out: dict[str, str] = {}
    for row in _TASK_INDEX:
        pid = str(row.get("pattern_id") or "").strip()
        if pid:
            out[pid] = str(row.get("goal") or "")
    return out


def _rewrite_file(suites: dict[str, list[dict[str, str]]]) -> None:
    lines = [
        '"""Tagged diversified test suites for v128 algorithm course (task_001–task_128)."""',
        "",
        "from __future__ import annotations",
        "",
        "V128_TEST_SUITES: dict[str, list[dict[str, str]]] = {",
    ]
    for pattern in sorted(suites, key=lambda k: int(k.split("_")[1])):
        lines.append(f'    "{pattern}": [')
        for case in suites[pattern]:
            lines.append(
                "        {"
                f'"tag": {case["tag"]!r}, '
                f'"inputs": {case["inputs"]!r}, '
                f'"output": {case["output"]!r}'
                "},"
            )
        lines.append("    ],")
    lines.append("}")
    lines.append("")
    DATA_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    goals = _goal_by_pattern()
    updated: dict[str, list[dict[str, str]]] = {}
    changed = 0
    for pattern, cases in V128_TEST_SUITES.items():
        meta = ALGO_SYNTAX_META.get(pattern) or {}
        refs = meta.get("reference_codes") or {}
        goal = str(meta.get("detailed_description") or goals.get(pattern) or "")
        rows: list[dict[str, str]] = []
        for case in cases:
            row = dict(case)
            before = str(row.get("inputs") or "")
            after = normalize_test_case_inputs(
                before,
                str(refs.get("python") or ""),
                pattern_id=pattern,
                pascal_code=str(refs.get("pascal") or ""),
                goal=goal,
            )
            if after != before:
                changed += 1
            row["inputs"] = after
            rows.append(row)
        updated[pattern] = rows
    _rewrite_file(updated)
    print(f"rewrote {DATA_PATH.name}: {changed} inputs updated across {len(updated)} patterns")


if __name__ == "__main__":
    main()
