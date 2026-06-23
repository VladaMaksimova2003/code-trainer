#!/usr/bin/env python3
"""Recompute display_order for curriculum tasks using pedagogical sort rules."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.display.chapter_task_display_order import (
    compute_pedagogical_display_order,
    is_capstone_showcase_row,
    pedagogical_action_sort_key,
    showcase_pedagogical_sort_key,
)
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks
from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def _action_for_row(row, showcase: dict) -> str:
    action = str(
        showcase.get("primary_action") or showcase.get("action") or ""
    ).strip().lower()
    if action:
        return action
    task_format = str(showcase.get("task_format") or "").strip().lower()
    if task_format.startswith("сборка"):
        return "assemble"
    if task_format in {"исправление", "поиск_ошибки"}:
        return "debug"
    if task_format.startswith("перевод") or task_format.startswith("реализация"):
        return "translate"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair pedagogical display_order for curriculum tasks")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_models()
    session = SessionLocal()
    updated: list[dict[str, int | str]] = []
    try:
        by_chapter: dict[str, list[tuple]] = defaultdict(list)
        for row, showcase in iter_showcase_tasks(session):
            chapter_key = str(showcase.get("collection_key") or "").strip()
            if not chapter_key:
                continue
            by_chapter[chapter_key].append((row, showcase))

        for chapter_key, items in by_chapter.items():
            sortable: list[tuple] = []
            for row, showcase in items:
                action = _action_for_row(row, showcase)
                task_num = int(showcase.get("task_num") or row.id)
                title = str(row.title or showcase.get("title") or "")
                sortable.append(
                    (
                        showcase_pedagogical_sort_key(
                            {
                                "title": title,
                                "action": action,
                                "primary_action": action,
                                "display_order": showcase.get("display_order"),
                                "task_id": row.id,
                            }
                        ),
                        row,
                        showcase,
                        action,
                        task_num,
                        title,
                    )
                )
            sortable.sort(key=lambda item: item[0])

            for order_index, (_sort_key, row, showcase, action, task_num, title) in enumerate(sortable):
                new_order = compute_pedagogical_display_order(
                    title=title,
                    action=action,
                    task_num=task_num,
                )
                old_order = showcase.get("display_order")
                if old_order == new_order:
                    continue
                updated.append(
                    {
                        "task_id": int(row.id),
                        "chapter_key": chapter_key,
                        "action": action,
                        "display_order": new_order,
                    }
                )
                if not args.dry_run:
                    showcase["display_order"] = new_order
                    examples = dict(row.code_examples or {})
                    examples["curriculum_showcase"] = showcase
                    row.code_examples = examples
                    flag_modified(row, "code_examples")

        if args.dry_run:
            session.rollback()
        else:
            session.commit()
            invalidate_showcase_task_index_cache()
    finally:
        session.close()

    print(json.dumps({"updated": len(updated), "items": updated[:20]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
