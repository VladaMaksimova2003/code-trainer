"""Batch 6 dry-run preview for task_015 and task_079 (no DB apply, no OVERRIDES)."""
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

from algo_v128_catalog import _TASK_INDEX  # noqa: E402
from debug_batch3_damaged_preview import (  # noqa: E402
    catalog_entry,
    fields_changed,
    preview_public_payload,
    validation_report,
)
from debug_batch6_t015_t079 import BATCH6_OVERRIDES  # noqa: E402
from import_debug_fixes import DB, LANGS, norm, run_python, validate  # noqa: E402

BATCH6 = ["task_015", "task_079"]


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
                    "expected": tc.get("output"),
                    "got": norm(got),
                }
            )
    return {
        "fixed_validation": f"{fixed_ok}/{len(tests or [])}",
        "failing_tests": notes,
    }


def fixed_buggy_concept(pid: str, spec: dict) -> dict[str, Any]:
    if pid == "task_015":
        return {
            "fixed": (
                "Read total, isStudent, hasCoupon; validate; tier discount "
                "7/15/25%; +5 student; +3 coupon; cap 30; print percent or invalid."
            ),
            "buggy": (
                "Translate-debug starter: Python/C#-like syntax in Pascal/C++/Java/C#; "
                "same tier logic where parseable — student fixes syntax + types."
            ),
            "buggy_pitfall": "multi_branch_discount / wrong_language_syntax",
        }
    return {
        "fixed": (
            "Read n key-value pairs into map, then m pairs; sum values on key clash; "
            "print sorted key value lines."
        ),
        "buggy": (
            "Second dict overwrites values instead of summing; Pascal uses fixed index n only; "
            "Python iterates dict incorrectly."
        ),
        "buggy_pitfall": "map merge overwrite instead of sum",
    }


def build_preview(pid: str, db_row) -> dict[str, Any]:
    spec = dict(BATCH6_OVERRIDES[pid])
    spec_for_import = {
        k: v
        for k, v in spec.items()
        if k not in ("canon_notes", "db_replacements", "legacy_untouched", "risks")
    }
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
        },
        "fixed_buggy_concept": fixed_buggy_concept(pid, spec),
        "fixed_buggy_x5": {
            "fixed_langs": [lang for lang in LANGS if spec["ref"].get(lang)],
            "buggy_langs": [lang for lang in LANGS if spec["buggy"].get(lang)],
        },
        "current_db": current_db_validation(pid, db_row),
        "proposed": {
            "fixed_validation": val["fixed_validation"],
            "fixed_notes": val["fixed_notes"],
            "buggy_validation": val["buggy_validation"],
            "buggy_pass_notes": val["buggy_pass_notes"],
            "validate_ok": ok,
        },
        "expected_concepts": spec.get("concepts"),
        "hints": spec.get("hints"),
        "post_solve": spec.get("post_solve"),
        "fields_changed": fields_changed(db_row, spec_for_import),
        "public_payload_preview": preview_public_payload(db_row, spec_for_import),
        "db_will_replace": spec.get("db_replacements"),
        "legacy_untouched": spec.get("legacy_untouched"),
        "risks": spec.get("risks"),
    }


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report: dict[str, Any] = {
        "batch": 6,
        "tasks": BATCH6,
        "apply": False,
        "previews": [],
    }
    for pid in BATCH6:
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

    out = BACKEND.parent / "docs" / "debug_import_batch6_preview.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
