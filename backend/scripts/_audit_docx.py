#!/usr/bin/env python3
"""Quick audit of parsed docx course."""
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from scripts.build_algorithm_syntax_course_from_docx import (
    _repair_duplicate_task_metadata,
    _report_docx_duplicates,
    parse_course,
    paras,
)

DOCX = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)


def main() -> None:
    lines = paras(DOCX)
    fmts = {ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("Тип реализации:")}
    impls = {ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("Реализация задания:")}
    print("format types:", sorted(fmts))
    print("impl headers:", sorted(impls))
    tasks, _, failures = parse_course(lines)
    _repair_duplicate_task_metadata(tasks)
    print("tasks", len(tasks), "failures", len(failures))
    if failures:
        for f in failures[:15]:
            print(" ", f)
    _report_docx_duplicates(tasks)
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 66]:
        t = next(x for x in tasks if x["task_num"] == n)
        print(f"\n=== {n}: {t['title']} ({t['format_ru']})")
        print("  short:", (t.get("short_goal") or "")[:100])
        print("  detail:", (t.get("detailed_description") or "")[:120])
        print("  tc:", t.get("test_cases"))
        pas = t.get("implementations", {}).get("pascal", {})
        if pas.get("placeholder_code"):
            print("  ph:", pas["placeholder_code"][:140])
        if pas.get("assembly_blocks"):
            print("  blocks:", len(pas["assembly_blocks"]), pas["assembly_blocks"][:2])
        ref = (t.get("reference_codes") or {}).get("pascal", "")
        print("  ref:", ref[:120])


if __name__ == "__main__":
    main()
