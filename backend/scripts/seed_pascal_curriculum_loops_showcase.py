#!/usr/bin/env python3
"""
Seed Pascal curriculum v2 showcase tasks for LC `loops`.

Run:
  cd backend
  poetry run python scripts/seed_pascal_curriculum_loops_showcase.py

Optional:
  poetry run python scripts/seed_pascal_curriculum_loops_showcase.py --teacher-email admin@test.com
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import (
    list_showcase_tasks,
    seed_pascal_loops_showcase,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import DEFAULT_SEED_TEACHER_EMAIL, resolve_seed_teacher_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Pascal loops curriculum showcase tasks")
    parser.add_argument(
        "--teacher-email",
        default=DEFAULT_SEED_TEACHER_EMAIL,
        help=f"Task author for manual editing (default: {DEFAULT_SEED_TEACHER_EMAIL})",
    )
    args = parser.parse_args()

    load_models()
    session = SessionLocal()
    try:
        teacher_id = resolve_seed_teacher_id(session, args.teacher_email)
        report = seed_pascal_loops_showcase(session, teacher_id=teacher_id)
        session.commit()
        payload = report.to_dict()
        payload["tasks"] = list_showcase_tasks(session)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if not payload["errors"] else 1
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())

