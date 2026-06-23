#!/usr/bin/env python3
"""Remove duplicate files_modules tasks #81-#85 (keep ids 89-93, drop 94-98)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from infrastructure.db.models.task.registry import load_models  # noqa: E402
from infrastructure.db.session import SessionLocal  # noqa: E402
from scripts.reseed_v4_all import hard_delete_tasks_by_ids  # noqa: E402

DUPLICATE_IDS = [94, 95, 96, 97, 98]


def main() -> int:
    parser = argparse.ArgumentParser(description="Delete duplicate files_modules task rows")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_models()
    session = SessionLocal()
    try:
        report = hard_delete_tasks_by_ids(session, DUPLICATE_IDS, dry_run=args.dry_run)
        if not args.dry_run:
            session.commit()
        else:
            session.rollback()
        print(json.dumps({"deleted_ids": DUPLICATE_IDS, **report}, ensure_ascii=False, indent=2))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
