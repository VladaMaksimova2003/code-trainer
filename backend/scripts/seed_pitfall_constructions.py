#!/usr/bin/env python3
"""Seed Construction library rows from pitfall_catalog (MPLT §2.5.2).

Usage:
  cd backend
  poetry run python scripts/seed_pitfall_constructions.py
  poetry run python scripts/seed_pitfall_constructions.py --dry-run
  poetry run python scripts/seed_pitfall_constructions.py --link-showcase-tasks
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.display.pitfall_catalog import PITFALLS, list_pitfall_ids
from application.curriculum.display.pitfall_construction_sync import sync_pitfall_constructions
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def main() -> int:
    parser = argparse.ArgumentParser(description="Export pitfall catalog to Construction library")
    parser.add_argument("--dry-run", action="store_true", help="Plan only, no DB writes")
    parser.add_argument(
        "--link-showcase-tasks",
        action="store_true",
        help="Attach MPLT Construction rows to platform tasks with matching pitfall_id",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Check catalog size only (no DB)",
    )
    args = parser.parse_args()

    catalog_ids = list_pitfall_ids()
    if len(catalog_ids) != len(PITFALLS):
        print(
            json.dumps(
                {
                    "validation": "FAILED",
                    "error": "list_pitfall_ids() mismatch with PITFALLS",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    if args.validate_only:
        print(
            json.dumps(
                {
                    "validation": "OK",
                    "pitfalls_in_catalog": len(PITFALLS),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    load_models()
    session = SessionLocal()
    try:
        report = sync_pitfall_constructions(
            session,
            dry_run=args.dry_run,
            link_showcase_tasks=args.link_showcase_tasks,
        )
        if not args.dry_run:
            session.commit()
        payload = report.to_dict()
        payload["validation"] = "OK"
        payload["pitfalls_in_catalog"] = len(PITFALLS)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
