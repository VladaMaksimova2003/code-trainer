#!/usr/bin/env python3
"""
Seed Pascal Course v3.1.1 — 19 collections, 283 tasks.

Run:
  cd backend
  poetry run python scripts/seed_pascal_course_v311.py
  poetry run python scripts/seed_pascal_course_v311.py --collection loops

Tasks are owned by admin@test.com (SEED_ADMIN_EMAIL) so you can edit them in the teacher UI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
    catalog_summary,
    validate_v311_catalog,
)
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    list_showcase_tasks_for_collection,
    seed_pascal_attach_unified_collection,
    seed_pascal_v311_showcase_collection,
)
from application.curriculum.pascal.showcase.pascal_v311_purge import (
    apply_purge_legacy_pascal_tasks,
    plan_purge_legacy_pascal_tasks,
)
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    PASCAL_V311_SHOWCASE_COLLECTIONS,
    V311_CHAPTER_ORDER,
)
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import (
    all_pascal_v311_showcase_specs,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import DEFAULT_SEED_TEACHER_EMAIL, resolve_seed_teacher_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Pascal Course v3.1.1")
    parser.add_argument(
        "--collection",
        default=None,
        help="Chapter key (e.g. loops, error_handling). Default: all 19.",
    )
    parser.add_argument(
        "--teacher-email",
        default=DEFAULT_SEED_TEACHER_EMAIL,
        help=f"Task author for manual editing (default: {DEFAULT_SEED_TEACHER_EMAIL})",
    )
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--attach-unified",
        action="store_true",
        help="Attach Pascal tracks to existing Universal Core (py_*) tasks without creating new rows.",
    )
    parser.add_argument(
        "--skip-purge",
        action="store_true",
        help="Do not delete legacy Pascal showcase tasks before seeding.",
    )
    parser.add_argument(
        "--purge-only",
        action="store_true",
        help="Only delete legacy Pascal showcase tasks (no seed).",
    )
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

    if catalog_errors and not args.attach_unified:
        print(json.dumps({"validation": "FAILED", "errors": catalog_errors}, ensure_ascii=False, indent=2))
        return 1
    if args.validate_only:
        print(json.dumps({"validation": "OK", "summary": summary}, ensure_ascii=False, indent=2))
        return 0

    all_specs = all_pascal_v311_showcase_specs()
    keys = [args.collection] if args.collection else list(V311_CHAPTER_ORDER)
    for key in keys:
        if key not in all_specs:
            print(json.dumps({"error": f"Unknown collection: {key}"}, ensure_ascii=False))
            return 1

    load_models()
    session = SessionLocal()
    reports: list[dict] = []
    exit_code = 0
    purge_report: dict | None = None
    try:
        if not args.skip_purge and not args.attach_unified:
            purge_plan = plan_purge_legacy_pascal_tasks(session)
            purge_report = apply_purge_legacy_pascal_tasks(session, dry_run=False).to_dict()
            purge_report["plan"] = purge_plan.to_dict()
            session.flush()
        if args.purge_only:
            session.commit()
            print(json.dumps({"purge": purge_report}, ensure_ascii=False, indent=2))
            return 0

        teacher_id = resolve_seed_teacher_id(session, args.teacher_email)
        seed_fn = (
            seed_pascal_attach_unified_collection
            if args.attach_unified
            else seed_pascal_v311_showcase_collection
        )
        for key in keys:
            report = seed_fn(
                session,
                key,
                all_specs[key],
                teacher_id=teacher_id,
            )
            payload = report.to_dict()
            payload["tasks"] = list_showcase_tasks_for_collection(
                session, key, curriculum_version="3.1.1"
            )
            reports.append(payload)
            if payload["errors"]:
                exit_code = 1
        session.commit()
        format_counts = summary["format_counts"]
        builder_counts = summary["builder_counts"]
        output = {
            "validation": "OK",
            "purge": purge_report,
            "summary": summary,
            "collections_seeded": len(reports),
            "tasks_imported": sum(len(r.get("tasks") or []) for r in reports),
            "format_counts": format_counts,
            "builder_counts": builder_counts,
            "collections": reports,
            "totals": {
                "created": sum(r["totals"]["created"] for r in reports),
                "linked": sum(r["totals"]["linked"] for r in reports),
                "skipped": sum(r["totals"]["skipped"] for r in reports),
                "errors": sum(len(r["errors"]) for r in reports),
            },
            "registered_collections": len(PASCAL_V311_SHOWCASE_COLLECTIONS),
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
