#!/usr/bin/env python3
"""
Seed Python Course v1 — 22 collections, 245 tasks.

Run:
  cd backend
  poetry run python scripts/seed_python_course_v311.py
  poetry run python scripts/seed_python_course_v311.py --collection loops
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.python.catalog.python_curriculum_v3_catalog import (
    catalog_summary,
    validate_v311_catalog,
)
from application.curriculum.python.showcase.python_showcase_core import (
    list_showcase_tasks_for_collection,
    seed_python_v311_showcase_collection,
)
from application.curriculum.python.showcase.python_v311_registry import (
    PYTHON_V311_SHOWCASE_COLLECTIONS,
    V311_CHAPTER_ORDER,
)
from application.curriculum.python.showcase.python_v311_showcase_all_specs import (
    all_python_v311_showcase_specs,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import DEFAULT_SEED_TEACHER_EMAIL, resolve_seed_teacher_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Python Course v1")
    parser.add_argument(
        "--collection",
        default=None,
        help="Chapter key (e.g. loops, program_entry). Default: all.",
    )
    parser.add_argument(
        "--teacher-email",
        default=DEFAULT_SEED_TEACHER_EMAIL,
        help=f"Task author (default: {DEFAULT_SEED_TEACHER_EMAIL})",
    )
    parser.add_argument("--validate-only", action="store_true")
    from scripts.catalog_sync_guard import add_force_catalog_sync_argument, ensure_catalog_sync_allowed

    add_force_catalog_sync_argument(parser)
    args = parser.parse_args()

    catalog_errors = validate_v311_catalog()
    summary = catalog_summary()
    if args.validate_only:
        print(json.dumps({"validation": "OK" if not catalog_errors else "FAILED", "summary": summary, "errors": catalog_errors}, ensure_ascii=False, indent=2))
        return 1 if catalog_errors else 0

    if not ensure_catalog_sync_allowed(force=args.force_catalog_sync):
        return 2

    if catalog_errors:
        print(json.dumps({"validation": "FAILED", "errors": catalog_errors}, ensure_ascii=False, indent=2))
        return 1

    all_specs = all_python_v311_showcase_specs()
    keys = [args.collection] if args.collection else list(V311_CHAPTER_ORDER)
    for key in keys:
        if key not in all_specs:
            print(json.dumps({"error": f"Unknown collection: {key}"}, ensure_ascii=False))
            return 1

    load_models()
    session = SessionLocal()
    reports: list[dict] = []
    exit_code = 0
    try:
        teacher_id = resolve_seed_teacher_id(session, args.teacher_email)
        for key in keys:
            report = seed_python_v311_showcase_collection(
                session,
                key,
                all_specs[key],
                teacher_id=teacher_id,
            )
            payload = report.to_dict()
            payload["tasks"] = list_showcase_tasks_for_collection(
                session, key, curriculum_version="1.0"
            )
            reports.append(payload)
            if payload["errors"]:
                exit_code = 1
        session.commit()
        output = {
            "validation": "OK",
            "summary": summary,
            "collections_seeded": len(reports),
            "tasks_imported": sum(len(r.get("tasks") or []) for r in reports),
            "collections": reports,
            "totals": {
                "created": sum(r["totals"]["created"] for r in reports),
                "linked": sum(r["totals"]["linked"] for r in reports),
                "skipped": sum(r["totals"]["skipped"] for r in reports),
                "errors": sum(len(r["errors"]) for r in reports),
            },
            "registered_collections": len(PYTHON_V311_SHOWCASE_COLLECTIONS),
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
