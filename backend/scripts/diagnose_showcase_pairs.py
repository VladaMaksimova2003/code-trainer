"""Diagnose showcase tasks for strict mirror pair validation."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.curriculum_slot_mirror_map import all_mirrored_pairs
from application.curriculum.mirror.pedagogical_task_model import available_language_tracks
from application.curriculum.mirror.pedagogical_task_store import (
    iter_showcase_tasks,
    pedagogical_slot_id_from_showcase,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal

load_models()


def main() -> None:
    session = SessionLocal()
    try:
        by_ped: dict[str, tuple[int, dict]] = {}
        for row, showcase in iter_showcase_tasks(session):
            ped = pedagogical_slot_id_from_showcase(showcase) or str(showcase.get("slug") or "")
            by_ped[ped] = (row.id, showcase)

        for pas, py in sorted(all_mirrored_pairs().items()):
            if not pas.startswith(("lop_", "pit_")):
                continue
            row_id, sh = by_ped.get(pas, (None, {}))
            if row_id is None:
                print(f"MISSING ped={pas} expected_py={py}")
                continue
            tracks = available_language_tracks(sh)
            p = (sh.get("language_tracks") or {}).get("pascal") or {}
            tpy = (sh.get("language_tracks") or {}).get("python") or {}
            ok = (
                "pascal" in tracks
                and "python" in tracks
                and p.get("slug") == pas
                and tpy.get("slug") == py
            )
            if not ok:
                print(
                    f"BAD id={row_id} ped={pas} tracks={tracks} "
                    f"pas_slug={p.get('slug')} py_slug={tpy.get('slug')} expected_py={py}"
                )
    finally:
        session.close()


if __name__ == "__main__":
    main()
