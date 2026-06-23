#!/usr/bin/env python3
"""Hard-delete legacy showcase rows with task.id above the canonical v128 range."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.showcase.showcase_task_index import (  # noqa: E402
    invalidate_showcase_task_index_cache,
)
from infrastructure.db.models.task.registry import load_models  # noqa: E402
from infrastructure.db.session import SessionLocal  # noqa: E402
from scripts.reseed_v4_all import purge_showcase_tasks_above_id  # noqa: E402

load_models()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Delete showcase task rows with id > max-id (default 128).",
    )
    parser.add_argument(
        "--max-id",
        type=int,
        default=128,
        help="Keep tasks with id <= max-id; delete the rest (default: 128).",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        report = purge_showcase_tasks_above_id(
            session,
            max_id=args.max_id,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            session.commit()
            invalidate_showcase_task_index_cache()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
