#!/usr/bin/env python3
"""Recover v128_test_suites_data.py from course JSON + corrections + layout normalization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

from application.curriculum.content.v4_test_cases_io import normalize_test_case_inputs
from v128_test_suites_corrections import V128_TEST_CORRECTIONS

COURSE_JSON = BACKEND / "algo_syntax_course.json"
OUT_PATH = SCRIPTS / "v128_test_suites_data.py"

_TAG_CYCLE = ("typical", "single", "negative", "boundary", "duplicate", "not_found", "all_equal")


def _py_repr(suites: dict[str, list[dict[str, str]]]) -> str:
    lines = [
        '"""Tagged diversified test suites for v128 algorithm course (task_001–task_128)."""',
        "",
        "from __future__ import annotations",
        "",
        "V128_TEST_SUITES: dict[str, list[dict[str, str]]] = {",
    ]
    for pid in sorted(suites, key=lambda k: int(k.split("_")[1])):
        lines.append(f'    "{pid}": [')
        for case in suites[pid]:
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
    return "\n".join(lines)


def main() -> None:
    course = json.loads(COURSE_JSON.read_text(encoding="utf-8"))
    meta_by_pattern: dict[str, dict] = {}
    suites: dict[str, list[dict[str, str]]] = {}

    for row in course:
        num = int(row.get("task_num") or 0)
        if num < 1 or num > 128:
            continue
        pid = str(row.get("pattern_id") or f"task_{num:03d}")
        meta_by_pattern[pid] = row
        tagged: list[dict[str, str]] = []
        for idx, case in enumerate(row.get("test_cases") or []):
            tagged.append(
                {
                    "tag": _TAG_CYCLE[idx % len(_TAG_CYCLE)],
                    "inputs": str(case.get("inputs") or ""),
                    "output": str(case.get("output") or ""),
                }
            )
        if tagged:
            suites[pid] = tagged

    for pid, cases in V128_TEST_CORRECTIONS.items():
        suites[pid] = [dict(c) for c in cases]

    changed = 0
    for pid, cases in suites.items():
        meta = meta_by_pattern.get(pid) or {}
        refs = meta.get("reference_codes") or {}
        goal = str(meta.get("detailed_description") or meta.get("short_goal") or "")
        for case in cases:
            before = case["inputs"]
            after = normalize_test_case_inputs(
                before,
                str(refs.get("python") or ""),
                pattern_id=pid,
                pascal_code=str(refs.get("pascal") or ""),
                goal=goal,
            )
            if after != before:
                changed += 1
            case["inputs"] = after

    OUT_PATH.write_text(_py_repr(suites), encoding="utf-8")
    print(f"wrote {OUT_PATH.name}: {len(suites)} patterns, {changed} inputs normalized")


if __name__ == "__main__":
    main()
