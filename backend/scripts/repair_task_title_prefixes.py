#!/usr/bin/env python3
"""Strip curriculum chapter prefixes from stored task titles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task_version import TaskVersion
from infrastructure.db.session import SessionLocal


def _clean_title(title: str | None) -> str:
    return strip_showcase_title_prefix(str(title or ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove chapter bracket prefixes from task titles")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_models()
    session = SessionLocal()
    task_updates: list[dict[str, str | int]] = []
    version_updates: list[dict[str, str | int]] = []
    try:
        for row in session.scalars(select(TaskModel)).all():
            old_title = str(row.title or "")
            new_title = _clean_title(old_title)
            if new_title and new_title != old_title:
                task_updates.append({"task_id": int(row.id), "old": old_title, "new": new_title})
                if not args.dry_run:
                    row.title = new_title

        for version in session.scalars(select(TaskVersion)).all():
            old_title = str(version.title or "")
            new_title = _clean_title(old_title)
            if new_title and new_title != old_title:
                version_updates.append(
                    {"version_id": int(version.id), "task_id": int(version.task_id), "old": old_title, "new": new_title}
                )
                if not args.dry_run:
                    version.title = new_title

        if args.dry_run:
            session.rollback()
        else:
            session.commit()
            invalidate_showcase_task_index_cache()
    finally:
        session.close()

    print(
        json.dumps(
            {
                "tasks_updated": len(task_updates),
                "versions_updated": len(version_updates),
                "sample_tasks": task_updates[:12],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
