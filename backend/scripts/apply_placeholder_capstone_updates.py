#!/usr/bin/env python3
"""Refresh seeded plh_* showcase tasks from regenerated catalog metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.python.showcase.python_showcase_core import (  # noqa: E402
    _refresh_showcase_task_content,
    find_showcase_task_by_slug,
)
from application.curriculum.python.showcase.python_v311_showcase_all_specs import (  # noqa: E402
    all_python_v311_showcase_specs,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def refresh_placeholder_capstones(session, *, dry_run: bool = False) -> dict:
    stats = {"updated": 0, "missing": 0, "skipped": 0}
    all_specs = all_python_v311_showcase_specs()
    specs_by_slug = {
        spec.slug: spec
        for specs in all_specs.values()
        for spec in specs
        if str(spec.slug or "").startswith("plh_")
    }

    for slug, spec in sorted(specs_by_slug.items()):
        row = find_showcase_task_by_slug(session, slug)
        if row is None:
            stats["missing"] += 1
            continue
        _refresh_showcase_task_content(session, row, spec)
        stats["updated"] += 1

    if dry_run:
        session.rollback()
    else:
        session.commit()
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    load_models()
    session = SessionLocal()
    try:
        stats = refresh_placeholder_capstones(session, dry_run=args.dry_run)
        print(json.dumps({"dry_run": args.dry_run, **stats}, ensure_ascii=False, indent=2))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
