"""Batch 5 (Phase 2) dry-run preview for task_068 and task_076 (no DB apply)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(BACKEND))

from algo_v128_catalog import ALGO_SYNTAX_META, _TASK_INDEX  # noqa: E402
from debug_batch3_damaged_preview import (  # noqa: E402
    catalog_entry,
    fields_changed,
    merge_override_into_row,
    preview_public_payload,
    validation_report,
)
from debug_batch5_t068_t076 import BATCH5_OVERRIDES  # noqa: E402
from import_debug_fixes import DB, LANGS, norm, run_python, validate  # noqa: E402

BATCH5 = ["task_068", "task_076"]


def current_db_validation(pid: str, db_row) -> dict[str, Any]:
    _, _, _, tests, ce = db_row
    if isinstance(tests, str):
        tests = json.loads(tests)
    if isinstance(ce, str):
        ce = json.loads(ce)
    py = str((ce or {}).get("python") or "")
    fixed_ok = 0
    notes: list[str] = []
    for i, tc in enumerate(tests or []):
        got = run_python(py, tc.get("inputs", ""))
        if norm(got) == norm(tc.get("output", "")):
            fixed_ok += 1
        else:
            notes.append(
                {
                    "test": f"T{i+1}",
                    "inputs": tc.get("inputs"),
                    "expected": tc.get("output"),
                    "got": norm(got),
                    "reason": _fail_reason(pid, i + 1, tc),
                }
            )
    return {
        "fixed_validation": f"{fixed_ok}/{len(tests or [])}",
        "failing_tests": notes,
    }


def _fail_reason(pid: str, idx: int, tc: dict) -> str:
    inp = str(tc.get("inputs", ""))
    out = str(tc.get("output", ""))
    if inp == "3\n1\n2\n3\n" and out == "6":
        return "placeholder/chuzhoe: sum-array test copied from unrelated task"
    if pid == "task_068":
        return "wrong code (positive filter) and/or tests from search-index semantics"
    if pid == "task_076":
        return "wrong code (word frequency) or placeholder T5"
    return "code/tests mismatch"


def build_preview(pid: str, db_row) -> dict[str, Any]:
    spec = dict(BATCH5_OVERRIDES[pid])
    spec_for_import = {k: v for k, v in spec.items() if k not in ("canon_notes", "failing_test_fix", "conflicts")}
    val = validation_report(pid, spec_for_import)
    ok = validate(pid, spec_for_import)
    return {
        "task_id": pid,
        "chapter": next((r.get("chapter_key") for r in _TASK_INDEX if r.get("pattern_id") == pid), ""),
        "catalog": catalog_entry(pid),
        "canon": {
            "title": spec["title"],
            "description": spec["description"],
            "tests": spec["tests"],
            "notes": spec.get("canon_notes"),
            "failing_test_fix": spec.get("failing_test_fix"),
        },
        "conflicts": spec.get("conflicts") or [],
        "current_db": current_db_validation(pid, db_row),
        "proposed": {
            "fixed_validation": val["fixed_validation"],
            "fixed_notes": val["fixed_notes"],
            "buggy_validation": val["buggy_validation"],
            "buggy_pass_notes": val["buggy_pass_notes"],
            "validate_ok": ok,
        },
        "fixed_buggy_x5": {
            "fixed_langs": [lang for lang in LANGS if spec["ref"].get(lang)],
            "buggy_langs": [lang for lang in LANGS if spec["buggy"].get(lang)],
        },
        "expected_concepts": spec.get("concepts"),
        "hints": spec.get("hints"),
        "post_solve": spec.get("post_solve"),
        "fields_changed": fields_changed(db_row, spec_for_import),
        "public_payload_preview": preview_public_payload(db_row, spec_for_import),
        "risks": _risks(pid, spec, val, db_row),
    }


def _risks(pid: str, spec: dict, val: dict, db_row) -> list[str]:
    risks: list[str] = list(spec.get("conflicts") or [])
    if val.get("buggy_pass_notes"):
        risks.append(f"buggy python passes some tests: {val['buggy_pass_notes']}")
    if pid == "task_068":
        meta = ALGO_SYNTAX_META.get(pid) or {}
        if meta.get("raw_title") and "заказ" in str(meta.get("raw_title")).lower():
            risks.append("import replaces order-filter identity with count-equal-x canon")
        risks.append("canon tests differ from current DB v128-correction expected outputs")
    if pid == "task_076":
        risks.append("title canon uses catalog «Поиск value по id»; meta uses «Индекс студентов»")
        if len(spec.get("tests") or []) < len(json.loads(db_row[3]) if isinstance(db_row[3], str) else db_row[3]):
            risks.append("T5 placeholder removed (3\\n1\\n2\\n3\\n→6)")
    if not val.get("fixed_notes"):
        risks.append("low: proposed fixed validation clean")
    return risks


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report: dict[str, Any] = {
        "batch": 5,
        "phase": 2,
        "tasks": BATCH5,
        "apply": False,
        "previews": [],
    }
    for pid in BATCH5:
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            report["previews"].append({"task_id": pid, "error": "not in DB"})
            continue
        report["previews"].append(build_preview(pid, row))
    cur.close()
    conn.close()

    out = BACKEND.parent / "docs" / "debug_import_batch5_preview.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
