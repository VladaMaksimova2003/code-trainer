#!/usr/bin/env python3
"""Validate catalog and optional DB scope for defense stand (128 vs 192-B).

Usage:
  cd backend
  poetry run python scripts/validate_course_scope.py
  poetry run python scripts/validate_course_scope.py --scope 128
  poetry run python scripts/validate_course_scope.py --scope 192 --check-db
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from course_scope import (  # noqa: E402
    collect_db_scope_stats,
    parse_scope,
    scope_report,
    validate_catalog_scope,
    validate_db_scope,
)


def run_validation(*, scope: str, check_db: bool) -> tuple[int, dict]:
    parsed = parse_scope(scope)
    report: dict = {"scope": scope_report(parsed), "catalog_errors": validate_catalog_scope(parsed)}
    exit_code = 0 if not report["catalog_errors"] else 1

    if check_db:
        from infrastructure.db.models.task.registry import load_models
        from infrastructure.db.session import SessionLocal

        load_models()
        session = SessionLocal()
        try:
            stats = collect_db_scope_stats(session)
            report["db_stats"] = stats.to_dict()
            db_errors = validate_db_scope(parsed, session)
            report["db_errors"] = db_errors
            if db_errors:
                exit_code = 1
        finally:
            session.close()

    return exit_code, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate course scope (128 vs 192-B)")
    parser.add_argument(
        "--scope",
        default="192",
        choices=["128", "192"],
        help="Defense stand scope (default: 192 recommended)",
    )
    parser.add_argument(
        "--check-db",
        action="store_true",
        help="Also validate PostgreSQL showcase row count (requires running DB)",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    exit_code, report = run_validation(scope=args.scope, check_db=args.check_db)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        info = report["scope"]
        print(f"Scope {info['scope']} ({info['variant']}): {info['target_tasks']} tasks")
        print(f"  chapters: {info['chapters']} x {info['chapter_tasks']}")
        print(f"  demo slots: {', '.join(info['demo_slots'])}")

        if report["catalog_errors"]:
            print("\nCatalog errors:")
            for err in report["catalog_errors"]:
                print(f"  - {err}")
        else:
            print("\nCatalog: OK")

        if args.check_db:
            stats = report.get("db_stats", {})
            print(
                f"\nDB: rows={stats.get('showcase_rows')} "
                f"max_id={stats.get('max_task_id')} "
                f"patterns={stats.get('pattern_count')}"
            )
            db_errors = report.get("db_errors") or []
            if db_errors:
                print("DB errors:")
                for err in db_errors:
                    print(f"  - {err}")
            else:
                print("DB scope: OK")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
