#!/usr/bin/env python3
"""Apply DEMO content for task_006 (FCC assemble) and task_003 (AFCC implement).

Does NOT change slot_id, pattern_id, action, or format.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import Json

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(BACKEND))

from demo_fcc_afcc_content import (  # noqa: E402
    T003_BUGGY,
    T003_CONCEPTS,
    T003_DESC,
    T003_HINTS,
    T003_POST,
    T003_REF,
    T003_TESTS,
    T003_TITLE,
    T006_BUGGY,
    T006_CONCEPTS,
    T006_DESC,
    T006_FORMAT,
    T006_HINTS,
    T006_POST,
    T006_REF,
    T006_TESTS,
    T006_TITLE,
)
from import_recursion_slot_fixes import (  # noqa: E402
    DB,
    LANGS,
    build_assembly_variants,
    merge_task_code_examples,
    validate_all as _unused,
    validate_buggy_fails,
    validate_python,
)

T006_SPEC = {
    "kind": "assemble",
    "title": T006_TITLE,
    "description": T006_DESC,
    "ref": T006_REF,
    "buggy": T006_BUGGY,
    "tests": T006_TESTS,
    "concepts": T006_CONCEPTS,
    "hints": T006_HINTS,
    "post_solve": T006_POST,
    "task_format": T006_FORMAT,
}

T003_SPEC = {
    "kind": "implement",
    "title": T003_TITLE,
    "description": T003_DESC,
    "ref": T003_REF,
    "buggy": T003_BUGGY,
    "tests": T003_TESTS,
    "concepts": T003_CONCEPTS,
    "hints": T003_HINTS,
    "post_solve": T003_POST,
}

SPECS = {"task_006": T006_SPEC, "task_003": T003_SPEC}


def merge_with_buggy(ce: dict, spec: dict, pid: str) -> dict:
    new_ce = merge_task_code_examples(ce, spec, pid)
    for lang in LANGS:
        buggy = str((spec.get("buggy") or {}).get(lang) or "").strip()
        if buggy:
            new_ce[f"buggy_{lang}"] = buggy
    return new_ce


def validate_specs() -> bool:
    ok = True
    for pid, spec in SPECS.items():
        fv = validate_python(spec["ref"]["python"], spec["tests"])
        bv = validate_buggy_fails(spec["buggy"]["python"], spec["tests"])
        print(f"  [validate] {pid} fixed python {fv['pass']}")
        if fv["notes"]:
            print(f"    {fv['notes']}")
            ok = False
        print(f"  [validate] {pid} buggy python fail {bv['fail']}")
        if bv["pass_notes"]:
            print(f"    passes: {bv['pass_notes']}")
        if bv["fail"].split("/")[0] == "0":
            print(f"  [validate] {pid} WARNING: buggy passes all tests")
            ok = False
        if spec["kind"] == "assemble":
            variants = build_assembly_variants(spec["ref"], spec["task_format"], pattern_id=pid)
            for lang in LANGS:
                blocks = list((variants.get(lang) or {}).get("blocks") or [])
                if len(blocks) < 2:
                    print(f"  [validate] {pid} {lang} blocks too few: {len(blocks)}")
                    ok = False
    return ok


def apply_specs(cur, apply: bool) -> None:
    for pid, spec in SPECS.items():
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            print(f"  {pid}: NOT FOUND")
            continue
        did, old_title, _desc, _tc, ce = row
        if isinstance(ce, str):
            ce = json.loads(ce)
        showcase = (ce or {}).get("curriculum_showcase") or {}
        new_ce = merge_with_buggy(ce or {}, spec, pid)

        print(f"  {pid} (DB id {did})")
        print(f"    title: {old_title!r} -> {spec['title']!r}")
        print(f"    action/format unchanged: {showcase.get('primary_action')!r} / {showcase.get('task_format')!r}")
        print(f"    tests: {len(spec['tests'])}")

        if spec["kind"] == "assemble":
            variants = build_assembly_variants(spec["ref"], spec["task_format"], pattern_id=pid)
            primary = variants.get("pascal") or variants.get("python") or {}
            print(f"    assemble blocks (pascal): {len(primary.get('blocks') or [])}")
            if apply and primary:
                cur.execute(
                    """update block_reorder_task set
                         language=%s,
                         original_code=%s,
                         template=%s,
                         blocks=%s,
                         correct_order=%s,
                         language_variants=%s
                       where task_id=%s""",
                    (
                        "pascal",
                        primary.get("original_code"),
                        primary.get("template"),
                        Json(primary.get("blocks") or []),
                        Json(primary.get("correct_order") or []),
                        Json(variants),
                        did,
                    ),
                )

        if apply:
            cur.execute(
                """update task set title=%s, description=%s,
                          code_examples=%s, test_cases=%s, updated_at=now()
                   where id=%s""",
                (
                    spec["title"],
                    spec["description"],
                    json.dumps(new_ce, ensure_ascii=False),
                    json.dumps(spec["tests"], ensure_ascii=False),
                    did,
                ),
            )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    print("== VALIDATION ==")
    if not validate_specs():
        print("Validation failed.")
        return 1

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    print("\n== %s ==" % ("APPLY" if args.apply else "DRY-RUN"))
    apply_specs(cur, args.apply)
    if args.apply:
        conn.commit()
        print("Committed.")
    else:
        conn.rollback()
    cur.close()
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
