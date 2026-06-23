#!/usr/bin/env python3
"""Apply chapter-only titles + per-language expected concepts to seeded showcase tasks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.cpp.catalog.cpp_v311_expected_concepts import expected_concept_ids_for_row as cpp_expected
from application.curriculum.csharp.catalog.csharp_v311_expected_concepts import (
    expected_concept_ids_for_row as csharp_expected,
)
from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from application.curriculum.java.catalog.java_v311_expected_concepts import expected_concept_ids_for_row as java_expected
from application.curriculum.mirror.pedagogical_task_model import normalize_unified_showcase
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks, track_slug
from application.curriculum.pascal.catalog.pascal_v311_expected_concepts import (
    expected_concept_ids_for_row as pascal_expected,
)
from application.curriculum.pascal.showcase.pascal_v311_registry import v311_collection_by_key
from application.curriculum.python.catalog.python_v311_expected_concepts import (
    expected_concept_ids_for_row as python_expected,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal

RESOLVERS = {
    "pascal": lambda slot, chapter: pascal_expected(
        slot_id=slot,
        chapter_key=chapter,
        pascal_features="",
        task_format="",
    ),
    "python": lambda slot, chapter: python_expected(
        slot_id=slot,
        chapter_key=chapter,
        python_features="",
        task_format="",
    ),
    "cpp": lambda slot, chapter: cpp_expected(slot, chapter),
    "csharp": lambda slot, chapter: csharp_expected(slot, chapter),
    "java": lambda slot, chapter: java_expected(slot, chapter),
}


def _chapter_prefix(collection_key: str) -> str:
    col = v311_collection_by_key(collection_key)
    if col is None:
        return ""
    return col.title_prefix


def _resolve_concepts(lang: str, slot: str, chapter_key: str) -> list[str]:
    resolver = RESOLVERS.get(lang)
    if resolver is None or not slot:
        return []
    return list(resolver(slot, chapter_key))


def apply(session, *, dry_run: bool = False) -> dict:
    stats = {"titles": 0, "tracks": 0, "tasks": 0}
    for row, showcase in iter_showcase_tasks(session):
        stats["tasks"] += 1
        collection_key = str(showcase.get("collection_key") or "").strip()
        prefix = _chapter_prefix(collection_key)
        clean = strip_showcase_title_prefix(str(row.title or ""))
        if prefix and clean:
            new_title = f"{prefix}{clean}"
            if row.title != new_title:
                row.title = new_title
                stats["titles"] += 1

        examples = dict(row.code_examples or {})
        merged = dict(examples.get("curriculum_showcase") or {})
        tracks = dict(merged.get("language_tracks") or {})
        changed = False

        for lang in ("pascal", "python", "cpp", "csharp", "java"):
            track = dict(tracks.get(lang) or {})
            slug = track_slug(merged, lang) or str(track.get("slug") or "")
            if not slug:
                continue
            chapter = str(track.get("collection_key") or collection_key or "")
            concepts = _resolve_concepts(lang, slug, chapter)
            if concepts and track.get("expected_concept_ids") != concepts:
                track["expected_concept_ids"] = concepts
                tracks[lang] = track
                changed = True
                stats["tracks"] += 1

        if changed:
            merged["language_tracks"] = tracks
            merged = normalize_unified_showcase(merged)
            primary_lang = str(merged.get("target_language") or "pascal").lower()
            primary_track = tracks.get(primary_lang) or {}
            if primary_track.get("expected_concept_ids"):
                merged["expected_concept_ids"] = primary_track["expected_concept_ids"]
            examples["curriculum_showcase"] = merged
            row.code_examples = examples
            flag_modified(row, "code_examples")

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
        stats = apply(session, dry_run=args.dry_run)
        print(json.dumps({"dry_run": args.dry_run, **stats}, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
