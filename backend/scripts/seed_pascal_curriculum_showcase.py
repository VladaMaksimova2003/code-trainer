#!/usr/bin/env python3
"""
Seed Pascal curriculum showcase tasks (all or one collection).

Run:
  cd backend
  poetry run python scripts/seed_pascal_curriculum_showcase.py
  poetry run python scripts/seed_pascal_curriculum_showcase.py --collection loops
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    SeedReport,
    list_showcase_tasks_for_collection,
    seed_pascal_showcase_collection,
)
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import DEFAULT_SEED_TEACHER_EMAIL, resolve_seed_teacher_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Pascal curriculum showcase tasks")
    parser.add_argument(
        "--collection",
        default=None,
        help="Chapter key (e.g. loops, conditions, variables_and_io). Default: all.",
    )
    parser.add_argument(
        "--teacher-email",
        default=DEFAULT_SEED_TEACHER_EMAIL,
        help=f"Task author for manual editing (default: {DEFAULT_SEED_TEACHER_EMAIL})",
    )
    args = parser.parse_args()

    all_specs = all_pascal_showcase_specs()
    keys = [args.collection] if args.collection else [c.chapter_key for c in PASCAL_SHOWCASE_COLLECTIONS]
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
            report = seed_pascal_showcase_collection(
                session,
                key,
                all_specs[key],
                teacher_id=teacher_id,
            )
            payload = report.to_dict()
            payload["tasks"] = list_showcase_tasks_for_collection(session, key)
            reports.append(payload)
            if payload["errors"]:
                exit_code = 1
        session.commit()
        summary = {
            "collections": reports,
            "totals": {
                "collections": len(reports),
                "tasks": sum(len(r.get("tasks") or []) for r in reports),
                "created": sum(r["totals"]["created"] for r in reports),
                "errors": sum(len(r["errors"]) for r in reports),
            },
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return exit_code
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())

