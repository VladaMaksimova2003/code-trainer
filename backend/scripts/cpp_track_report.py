#!/usr/bin/env python3
"""Quick C++ track stats after seed."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.curriculum_slot_mirror_cpp import is_cpp_only_slot
from application.curriculum.mirror.pedagogical_task_model import available_language_tracks
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def main() -> int:
    load_models()
    session = SessionLocal()
    triple = dual = with_cpp = cpp_only = partial = 0
    partial_samples: list[str] = []
    try:
        for row, showcase in iter_showcase_tasks(session):
            tracks = set(available_language_tracks(showcase))
            if "cpp" in tracks:
                with_cpp += 1
            if tracks >= {"pascal", "python", "cpp"}:
                triple += 1
            elif tracks == {"pascal", "python"}:
                dual += 1
            elif "cpp" in tracks:
                partial += 1
                partial_samples.append(f"{row.id}:{sorted(tracks)}")
            slug = str(showcase.get("slug") or "")
            if is_cpp_only_slot(slug):
                cpp_only += 1
    finally:
        session.close()

    print(f"tasks_with_cpp_track: {with_cpp}")
    print(f"triple_track_pascal_python_cpp: {triple}")
    print(f"dual_track_pascal_python_only: {dual}")
    print(f"cpp_partial_track_tasks: {partial}")
    if partial_samples:
        print("partial_samples:", ", ".join(partial_samples[:10]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
