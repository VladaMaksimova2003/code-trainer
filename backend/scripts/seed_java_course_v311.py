#!/usr/bin/env python3
"""Attach Java language tracks to Universal Core (all stages or one MVP stage).

Run full course (270 tasks, 26 chapters):
  poetry run python scripts/seed_java_course_v311.py --stage all

Requires Python v3.1.1 showcase in DB for mirror attach rows (py_* slots).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.java.catalog.java_curriculum_v3_catalog import (
    catalog_summary,
    validate_v311_catalog,
)
from application.curriculum.java.showcase.java_showcase_core import (
    list_java_tasks_for_collection,
    seed_java_collection,
)
from application.curriculum.java.showcase.java_v311_showcase_all_specs import specs_for_chapters
from application.curriculum.mirror.curriculum_slot_mirror_cpp import chapters_for_stage
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import DEFAULT_SEED_TEACHER_EMAIL, resolve_seed_teacher_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed / attach Java Course v1 tracks")
    parser.add_argument(
        "--stage",
        default="all",
        help="all (default, 26 chapters) | MVP-1 | MVP-2 | MVP-3 | v1-full | v1.1 | v1.2",
    )
    parser.add_argument("--collection", default=None, help="Single chapter key override")
    parser.add_argument("--skip-purge", action="store_true", help="No-op placeholder (never full purge)")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--teacher-email", default=DEFAULT_SEED_TEACHER_EMAIL)
    args = parser.parse_args()

    catalog_errors = validate_v311_catalog()
    summary = catalog_summary()
    if catalog_errors:
        print(json.dumps({"validation": "FAILED", "errors": catalog_errors}, ensure_ascii=False, indent=2))
        return 1
    if args.validate_only:
        print(json.dumps({"validation": "OK", "summary": summary}, ensure_ascii=False, indent=2))
        return 0

    try:
        if args.collection:
            chapter_keys = (args.collection,)
        else:
            chapter_keys = chapters_for_stage(args.stage)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1

    all_specs = specs_for_chapters(chapter_keys)
    load_models()
    session = SessionLocal()
    reports: list[dict] = []
    exit_code = 0
    try:
        teacher_id = resolve_seed_teacher_id(session, args.teacher_email)
        for key in chapter_keys:
            if key not in all_specs:
                print(json.dumps({"error": f"Unknown collection: {key}"}, ensure_ascii=False))
                return 1
            report = seed_java_collection(
                session,
                key,
                all_specs[key],
                teacher_id=teacher_id,
            )
            payload = report.to_dict()
            payload["tasks"] = list_java_tasks_for_collection(session, key)
            reports.append(payload)
            if payload["errors"]:
                exit_code = 1
        session.commit()
        output = {
            "validation": "OK",
            "stage": args.stage,
            "skip_purge": args.skip_purge,
            "summary": summary,
            "collections_seeded": len(reports),
            "tasks_in_db": sum(len(r.get("tasks") or []) for r in reports),
            "collections": reports,
            "totals": {
                "attached": sum(r["totals"]["attached"] for r in reports),
                "created": sum(r["totals"]["created"] for r in reports),
                "skipped": sum(r["totals"]["skipped"] for r in reports),
                "errors": sum(len(r["errors"]) for r in reports),
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return exit_code
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
