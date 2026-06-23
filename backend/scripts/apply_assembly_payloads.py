#!/usr/bin/env python3
"""Refresh block-reorder payloads for seeded showcase tasks from catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks
from application.curriculum.python.catalog.python_curriculum_v3_catalog import all_v311_slots
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def _catalog_slot_for_slug(slug: str, slots: dict) -> object | None:
    key = str(slug or "").strip()
    if key in slots:
        return slots[key]
    import re

    m = re.match(r"^(?:pas|py|cpp|cs|java|csharp)_(\d+)$", key)
    if m:
        py_key = f"py_{int(m.group(1)):03d}"
        if py_key in slots:
            return slots[py_key]
    return None


def refresh_assembly(session, *, dry_run: bool = False) -> dict:
    stats = {"updated": 0, "skipped": 0}
    slots = {slot.slot_id: slot for slot in all_v311_slots()}

    for row, showcase in iter_showcase_tasks(session):
        slug = str(showcase.get("slug") or "")
        slot = _catalog_slot_for_slug(slug, slots)
        if slot is None or slot.builder_key != "block_reorder_python":
            continue
        extra = dict(slot.extra or {})
        br = row.block_reorder_task
        if br is None:
            stats["skipped"] += 1
            continue
        changed = False
        for key in ("original_code", "template", "blocks", "correct_order"):
            val = extra.get(key)
            if val is not None and getattr(br, key) != val:
                setattr(br, key, val)
                changed = True
        variants = extra.get("language_variants")
        if isinstance(variants, dict) and br.language_variants != variants:
            br.language_variants = variants
            changed = True
        test_cases = extra.get("test_cases")
        if isinstance(test_cases, list) and test_cases and row.test_cases != test_cases:
            row.test_cases = test_cases
            changed = True
        if changed:
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

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
        stats = refresh_assembly(session, dry_run=args.dry_run)
        print(json.dumps({"dry_run": args.dry_run, **stats}, ensure_ascii=False, indent=2))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
