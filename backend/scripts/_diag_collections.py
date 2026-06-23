#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.pascal.showcase.pascal_showcase_next import order_collection_showcase_tasks
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import all_pascal_v311_showcase_specs
from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def main() -> None:
    load_models()
    session = SessionLocal()
    try:
        specs = all_pascal_v311_showcase_specs().get("maps", ())
        rows = order_collection_showcase_tasks(session, "maps", specs)
        for row in rows:
            title = strip_showcase_title_prefix(str(row.get("title") or ""))
            print(f"{row['task_id']:3} {row.get('action'):10} {title[:40]}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
