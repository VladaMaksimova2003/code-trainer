#!/usr/bin/env python3
"""Report tasks with duplicate/wrong test cases vs authoritative v4_test_cases tasks 1-8."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from scripts.build_algorithm_syntax_course_from_docx import (
    _repair_broken_placeholder_gaps,
    _repair_duplicate_task_metadata,
    parse_course,
    paras,
)
from scripts.algo_task_descriptions import enrich_detailed_description

DOCX = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)


def main() -> int:
    lines = paras(DOCX)
    tasks, _, failures = parse_course(lines)
    _repair_duplicate_task_metadata(tasks)
    for task in tasks:
        enrich_detailed_description(task)
    _repair_broken_placeholder_gaps(tasks)

    by_tc: dict[str, list[int]] = defaultdict(list)
    for task in tasks:
        key = json.dumps(task.get("test_cases") or [], ensure_ascii=False, sort_keys=True)
        by_tc[key].append(int(task["task_num"]))

    dup_groups = [(k, nums) for k, nums in by_tc.items() if len(nums) > 1]
    dup_groups.sort(key=lambda item: -len(item[1]))

    out: list[str] = [
        f"tasks={len(tasks)} failures={len(failures)}",
        f"duplicate TC groups={len(dup_groups)}",
    ]
    for key, nums in dup_groups[:15]:
        out.append(f"  {len(nums)} tasks share TC: {nums[:20]}{'...' if len(nums)>20 else ''}")

    for n in [1, 8, 9, 16, 17, 30, 33, 35]:
        t = next(x for x in tasks if x["task_num"] == n)
        ref = (t.get("reference_codes") or {}).get("pascal", "")[:80].replace("\n", "\\n")
        out.append(f"\nTask {n}: {t['title']} | {t['format_ru']}")
        out.append(f"  TC: {t.get('test_cases')}")
        out.append(f"  pas ref: {ref}")

    Path(BACKEND / "_tc_quality.txt").write_text("\n".join(out), encoding="utf-8")
    print("written", BACKEND / "_tc_quality.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
