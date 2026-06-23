"""Sync v128 catalog titles into DB (title only, preserves task bodies)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks
from application.curriculum.pascal.showcase.pascal_v311_registry import v311_collection_by_key
from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from pascal_v31_tasks import V31_TASKS  # noqa: E402
from v128_task_titles import V128_TASK_TITLES  # noqa: E402


def _catalog_title_by_slot() -> dict[str, str]:
    by_slot: dict[str, str] = {}
    for row in V31_TASKS:
        slot_id, chapter, _old_title, *_rest = row
        num = int(str(slot_id).rsplit("_", 1)[-1])
        new_suffix = V128_TASK_TITLES[num]
        col = v311_collection_by_key(chapter)
        prefix = col.title_prefix if col is not None else ""
        full = f"{prefix}{new_suffix}"
        by_slot[str(slot_id)] = full
        num_part = str(slot_id).split("_", 1)[-1]
        for prefix_lang in ("pas", "py", "cpp", "cs", "java"):
            by_slot[f"{prefix_lang}_{num_part}"] = full
    return by_slot


def sync_titles(*, dry_run: bool = False) -> dict[str, int]:
    catalog = _catalog_title_by_slot()
    stats = {"tasks": 0, "updated": 0, "missing": 0, "unchanged": 0}

    session = SessionLocal()
    try:
        for row, showcase in iter_showcase_tasks(session):
            stats["tasks"] += 1
            slot = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
            new_title = catalog.get(slot)
            if not new_title:
                stats["missing"] += 1
                continue
            current = str(row.title or "").strip()
            if current == new_title:
                stats["unchanged"] += 1
                continue
            # keep chapter prefix from DB if catalog title uses suffix-only mismatch
            stripped = strip_showcase_title_prefix(current)
            col_key = str(showcase.get("collection_key") or "")
            col = v311_collection_by_key(col_key)
            if col is not None and stripped and not new_title.startswith(col.title_prefix):
                candidate = f"{col.title_prefix}{V128_TASK_TITLES[int(slot.rsplit('_',1)[-1])]}"
                if candidate != current:
                    row.title = candidate
                    stats["updated"] += 1
                else:
                    stats["unchanged"] += 1
            else:
                row.title = new_title
                stats["updated"] += 1

        if dry_run:
            session.rollback()
        else:
            session.commit()
            invalidate_showcase_task_index_cache()
        return stats
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync v128 titles to DB (title field only)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    load_models()
    stats = sync_titles(dry_run=args.dry_run)
    print(json.dumps({"dry_run": args.dry_run, **stats}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
