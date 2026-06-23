"""Batch 7 dry-run preview for task_063 and task_071 (no DB apply, no OVERRIDES wire)."""
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
from debug_batch7_t063_t071 import BATCH7_OVERRIDES  # noqa: E402
from import_debug_fixes import DB, LANGS, norm, run_python, validate  # noqa: E402

BATCH7 = ["task_063", "task_071"]


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


def fixed_buggy_concept(pid: str) -> dict[str, Any]:
    if pid == "task_063":
        return {
            "fixed": (
                "Read n integers; bubble-sort descending (swap when a[j] < a[j+1]); "
                "print space-separated."
            ),
            "buggy": (
                "Python: ascending sort (wrong comparison). "
                "Pascal/C++/C#/Java: translate-debug syntax mixing + wrong sort direction."
            ),
            "buggy_pitfall": "sort_order / wrong comparison direction",
        }
    return {
        "fixed": (
            "Read n; accumulate pos_sum for x>0 and neg_sum for x<0; skip zeros; "
            "print pos_sum neg_sum."
        ),
        "buggy": (
            "Python: swapped output order (neg_sum pos_sum). "
            "Pascal: x>=0 adds zero to pos; swapped output; Python-like syntax."
        ),
        "buggy_pitfall": "fold_aggregate / wrong branch or output order",
    }


def placeholder_cleanup(pid: str, db_row) -> dict[str, Any]:
    _, _, _, tests, _ = db_row
    if isinstance(tests, str):
        tests = json.loads(tests)
    placeholders = []
    for i, tc in enumerate(tests or []):
        inp = tc.get("inputs", "")
        out = tc.get("output", "")
        if inp.strip() in {"1\n", "1"} and out == "1":
            placeholders.append(f"T{i+1}: inputs={inp!r} output={out!r}")
    spec_tests = BATCH7_OVERRIDES[pid]["tests"]
    return {
        "db_placeholder_tests": placeholders,
        "preview_test_count": len(spec_tests),
        "removed": placeholders,
    }


def build_preview(pid: str, db_row) -> dict[str, Any]:
    spec = dict(BATCH7_OVERRIDES[pid])
    spec_for_import = {
        k: v
        for k, v in spec.items()
        if k not in ("canon_notes", "db_replacements", "legacy_untouched", "risks")
    }
    val = validation_report(pid, spec_for_import)
    ok = validate(pid, spec_for_import)
    entry: dict[str, Any] = {
        "task_id": pid,
        "chapter": next(
            (r.get("chapter_key") for r in _TASK_INDEX if r.get("pattern_id") == pid),
            "",
        ),
        "catalog": catalog_entry(pid),
        "canon": {
            "title": spec["title"],
            "description": spec["description"],
            "tests": spec["tests"],
            "notes": spec.get("canon_notes"),
        },
        "fixed_buggy_concept": fixed_buggy_concept(pid),
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
    if pid == "task_063":
        entry["placeholder_cleanup"] = placeholder_cleanup(pid, db_row)
    else:
        entry["placeholder_cleanup"] = placeholder_cleanup(pid, db_row)
    return entry


def ready_for_apply(previews: list[dict[str, Any]]) -> bool:
    if len(previews) != len(BATCH7):
        return False
    for p in previews:
        if p.get("error"):
            return False
        prop = p.get("proposed") or {}
        if prop.get("fixed_validation") != f"4/4":
            return False
        if not prop.get("validate_ok"):
            return False
        buggy_pass = prop.get("buggy_pass_notes") or []
        buggy_val = prop.get("buggy_validation") or ""
        if buggy_val.startswith("0/"):
            return False
    return True


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    previews: list[dict[str, Any]] = []
    for pid in BATCH7:
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            previews.append({"task_id": pid, "error": "not in DB"})
            continue
        previews.append(build_preview(pid, row))
    cur.close()
    conn.close()

    report: dict[str, Any] = {
        "batch": 7,
        "tasks": BATCH7,
        "apply": False,
        "ready_for_apply": ready_for_apply(previews),
        "previews": previews,
    }

    out = BACKEND.parent / "docs" / "debug_batch7_preview.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
