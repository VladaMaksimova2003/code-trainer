#!/usr/bin/env python3
"""Fix technical_concept_id on imported algo_v4 showcase tasks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks
from application.curriculum.shared.algo_v128_showcase import CHAPTER_STUDY_TC, primary_tc_for_chapter
from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def _expected_tc(chapter_key: str, current: str) -> str | None:
    order = CHAPTER_STUDY_TC.get(chapter_key, ())
    if not order:
        return None
    if current in order:
        return None
    return primary_tc_for_chapter(chapter_key)


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair showcase technical_concept_id per chapter")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_models()
    session = SessionLocal()
    updated: list[dict[str, int | str]] = []
    try:
        for row, showcase in iter_showcase_tasks(session):
            chapter_key = str(showcase.get("collection_key") or "").strip()
            if not chapter_key:
                continue
            current = str(showcase.get("technical_concept_id") or "").strip()
            expected = _expected_tc(chapter_key, current)
            if expected is None:
                continue

            if not args.dry_run:
                showcase["technical_concept_id"] = expected
                tracks = dict(showcase.get("language_tracks") or {})
                for lang, track in tracks.items():
                    if not isinstance(track, dict):
                        continue
                    track_tc = str(track.get("technical_concept_id") or current).strip()
                    if track_tc not in CHAPTER_STUDY_TC.get(chapter_key, ()):
                        track["technical_concept_id"] = expected
                        tracks[lang] = track
                showcase["language_tracks"] = tracks
                examples = dict(row.code_examples or {})
                examples["curriculum_showcase"] = showcase
                row.code_examples = examples
                flag_modified(row, "code_examples")

            updated.append({"task_id": int(row.id), "chapter_key": chapter_key, "tc": expected})

        if args.dry_run:
            session.rollback()
        else:
            session.commit()
            invalidate_showcase_task_index_cache()
    finally:
        session.close()

    print(json.dumps({"updated": len(updated), "items": updated}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
