#!/usr/bin/env python3
"""
Sync algo-syntax chapter metadata in DB after catalog reorder.

Updates slot_pattern_id, known_language_variants and showcase fields from the
current catalog without overwriting teacher-locked task bodies.

Usage:
  cd backend
  poetry run python scripts/sync_algo_chapter_catalog.py --chapter algo_basics
  poetry run python scripts/sync_algo_chapter_catalog.py --chapter algo_basics --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.pascal.catalog.pascal_known_language import (
    build_known_language_variants,
)
from application.curriculum.content.algo_syntax_task_extra import resolve_slot_pattern_key
from application.curriculum.content.v4_reference_code import get_reference_code
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks
from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from application.tasks.services.teacher_assembly_preservation import should_skip_catalog_seed_refresh
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal

_SCRIPTS = BACKEND_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pascal_v31_tasks import V31_TASKS  # noqa: E402


def _catalog_rows_for_chapter(chapter_key: str) -> dict[str, dict[str, str | int]]:
    rows: dict[str, dict[str, str | int]] = {}
    for row in V31_TASKS:
        slot_id, chapter, title, fmt, action, pattern, goal, _features, diff, _legacy = row
        if chapter != chapter_key:
            continue
        task_num = int(str(slot_id).rsplit("_", 1)[-1])
        for prefix in ("pas", "py", "cpp", "cs", "java"):
            num = slot_id.split("_", 1)[-1]
            lang_slot = f"{prefix}_{num}"
            rows[lang_slot] = {
                "pattern": pattern,
                "title": title,
                "task_format": fmt,
                "primary_action": action,
                "difficulty": diff,
                "educational_goal": goal,
                "task_num": task_num,
                "display_order": task_num * 10,
            }
    return rows


def _reference_variants(slot_id: str, pattern: str) -> tuple[dict, dict[str, str]]:
    pattern_key = resolve_slot_pattern_key(slot_id, slot_pattern_id=pattern)
    pascal = get_reference_code(slot_id, "pascal", pattern_key=pattern_key)
    variants = build_known_language_variants(
        python=get_reference_code(slot_id, "python", pattern_key=pattern_key),
        cpp=get_reference_code(slot_id, "cpp", pattern_key=pattern_key),
        java=get_reference_code(slot_id, "java", pattern_key=pattern_key),
        csharp=get_reference_code(slot_id, "csharp", pattern_key=pattern_key),
    )
    examples = {lang: str(entry.get("source_code") or "") for lang, entry in variants.items()}
    if pascal.strip():
        examples["pascal"] = pascal
    return variants, examples


def sync_chapter(session, *, chapter_key: str, dry_run: bool = False) -> dict[str, int]:
    catalog = _catalog_rows_for_chapter(chapter_key)
    stats = {"matched": 0, "updated": 0, "skipped_teacher": 0, "unknown_slot": 0}

    for row, showcase in iter_showcase_tasks(session):
        collection = str(showcase.get("collection_key") or "").strip()
        if collection != chapter_key:
            continue
        slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
        meta = catalog.get(slot_id)
        if meta is None:
            stats["unknown_slot"] += 1
            continue
        stats["matched"] += 1
        pattern = meta["pattern"]
        preserve_body = should_skip_catalog_seed_refresh(row)

        showcase = dict(showcase)
        changed = False
        for field, value in (
            ("slot_pattern_id", pattern),
            ("task_num", meta["task_num"]),
            ("display_order", meta["display_order"]),
        ):
            if showcase.get(field) != value:
                showcase[field] = value
                changed = True

        if not preserve_body:
            for field, value in (
                ("task_format", meta["task_format"]),
                ("primary_action", meta["primary_action"]),
                ("educational_goal", meta["educational_goal"]),
            ):
                if showcase.get(field) != value:
                    showcase[field] = value
                    changed = True

            from application.curriculum.python.catalog.python_v311_builder_mapping import (
                assignment_for_task_format,
            )

            catalog_title = str(meta["title"])
            if str(row.title or "").strip() != catalog_title:
                row.title = catalog_title
                changed = True
            assignment_type = assignment_for_task_format(str(meta["task_format"]))
            if str(row.task_type or "") != assignment_type:
                row.task_type = assignment_type
                changed = True
            catalog_difficulty = str(meta["difficulty"])
            if str(row.difficulty or "") != catalog_difficulty:
                row.difficulty = catalog_difficulty
                changed = True

            variants, lang_examples = _reference_variants(slot_id, pattern)
            if showcase.get("known_language_variants") != variants:
                showcase["known_language_variants"] = variants
                changed = True

            examples = dict(row.code_examples or {})
            for lang, code in lang_examples.items():
                if code.strip() and examples.get(lang) != code:
                    examples[lang] = code
                    changed = True
        else:
            stats["skipped_teacher"] += 1
            examples = dict(row.code_examples or {})

        examples["curriculum_showcase"] = showcase
        if examples != dict(row.code_examples or {}):
            row.code_examples = examples
            flag_modified(row, "code_examples")
            changed = True

        if changed:
            stats["updated"] += 1

    if dry_run:
        session.rollback()
    else:
        session.commit()
        invalidate_showcase_task_index_cache()
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync algo chapter catalog metadata in DB")
    parser.add_argument("--chapter", required=True, help="e.g. algo_basics")
    parser.add_argument("--dry-run", action="store_true")
    from scripts.catalog_sync_guard import add_force_catalog_sync_argument, ensure_catalog_sync_allowed

    add_force_catalog_sync_argument(parser)
    args = parser.parse_args()

    if not ensure_catalog_sync_allowed(force=args.force_catalog_sync):
        return 2

    load_models()
    session = SessionLocal()
    try:
        stats = sync_chapter(session, chapter_key=args.chapter, dry_run=args.dry_run)
        print(json.dumps({"chapter": args.chapter, "dry_run": args.dry_run, **stats}, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
