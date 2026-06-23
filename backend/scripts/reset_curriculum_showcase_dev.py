#!/usr/bin/env python3
"""
Dev-only cleanup: remove legacy/showcase tasks, keep Pascal curriculum v2 showcase.

Safety:
  ENV=dev  OR  ALLOW_DEV_RESET=1

Usage (from backend/):
  poetry run python scripts/reset_curriculum_showcase_dev.py --dry-run
  ALLOW_DEV_RESET=1 poetry run python scripts/reset_curriculum_showcase_dev.py --yes
  ALLOW_DEV_RESET=1 poetry run python scripts/reset_curriculum_showcase_dev.py --yes --seed-after

Then (if not using --seed-after):
  poetry run alembic upgrade head
  poetry run python scripts/seed_pascal_curriculum_loops_showcase.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import list_showcase_tasks, seed_pascal_loops_showcase
from application.curriculum.pascal.dev.showcase_dev_reset import (
    DevResetNotAllowedError,
    apply_showcase_dev_reset,
    assert_dev_reset_allowed,
    plan_showcase_dev_reset,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from shared.config import Settings


def _confirm(force: bool) -> bool:
    print("WARNING: DEVELOPMENT-ONLY — removes legacy/showcase tasks from the dev database.")
    print("Keeps tasks with code_examples.curriculum_showcase.group = pascal_curriculum_loops_v1")
    print(f"Target DB: {Settings().db.host}:{Settings().db.port}/{Settings().db.name}")
    if force:
        return True
    typed = input("Type 'RESET SHOWCASE DEV' to continue: ").strip()
    return typed == "RESET SHOWCASE DEV"


def _run_seed() -> dict:
    load_models()
    session = SessionLocal()
    try:
        report = seed_pascal_loops_showcase(session)
        session.commit()
        payload = report.to_dict()
        payload["tasks"] = list_showcase_tasks(session)
        return payload
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _run_alembic_upgrade() -> None:
    cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
    print(f">>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=BACKEND_ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-only curriculum showcase DB cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Print plan only, no deletes")
    parser.add_argument("--yes", action="store_true", help="Skip interactive confirmation")
    parser.add_argument(
        "--seed-after",
        action="store_true",
        help="Run alembic upgrade head + seed_pascal_curriculum_loops_showcase after cleanup",
    )
    args = parser.parse_args()

    try:
        assert_dev_reset_allowed()
    except DevResetNotAllowedError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not args.dry_run and not _confirm(args.yes):
        print("Aborted.")
        return 1

    load_models()
    session = SessionLocal()
    try:
        plan = plan_showcase_dev_reset(session)
        print(json.dumps({"plan": plan.to_dict()}, ensure_ascii=False, indent=2))

        report = apply_showcase_dev_reset(session, dry_run=args.dry_run)
        if not args.dry_run:
            session.commit()
        print(json.dumps({"report": report.to_dict()}, ensure_ascii=False, indent=2))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    if args.dry_run:
        return 0

    if args.seed_after:
        try:
            _run_alembic_upgrade()
        except subprocess.CalledProcessError as exc:
            print(
                json.dumps(
                    {
                        "alembic_warning": (
                            "alembic upgrade head failed (schema may already be current); "
                            "continuing with seed"
                        ),
                        "detail": str(exc),
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
        seed_payload = _run_seed()
        print(json.dumps({"seed": seed_payload}, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


