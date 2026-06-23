"""Find duplicate pedagogical_slot_id and problematic showcase rows."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.curriculum_slot_mirror_map import all_mirrored_pairs
from application.curriculum.mirror.pedagogical_task_model import available_language_tracks
from application.curriculum.mirror.pedagogical_task_store import (
    iter_showcase_tasks,
    pedagogical_slot_id_from_showcase,
    track_slug,
)
from application.curriculum.mirror.universal_core_validation import run_all_validations
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal

load_models()

TARGETS = {"lop_11", "pit_01", "pit_04", "pit_12", "pit_13", "pys_06", "pypit_12", "pypit_13", "pypit_01", "pypit_04"}


def main() -> None:
    session = SessionLocal()
    try:
        by_ped: dict[str, list[tuple[int, dict]]] = defaultdict(list)
        for row, showcase in iter_showcase_tasks(session):
            ped = pedagogical_slot_id_from_showcase(showcase) or ""
            if ped:
                by_ped[ped].append((row.id, showcase))
            slug = str(showcase.get("slug") or "")
            pas = track_slug(showcase, "pascal") or ""
            py = track_slug(showcase, "python") or ""
            if slug in TARGETS or pas in TARGETS or py in TARGETS or ped in TARGETS:
                print(
                    f"id={row.id} ped={ped!r} slug={slug} tracks={available_language_tracks(showcase)} "
                    f"pas={pas} py={py}"
                )

        print("\n--- duplicates ---")
        for ped, owners in sorted(by_ped.items()):
            if len(owners) > 1:
                print(f"DUPLICATE ped={ped} ids={[o[0] for o in owners]}")

        print("\n--- validation ---")
        for name, issues in run_all_validations(session).items():
            print(f"{name}: {len(issues)}")
            for issue in issues[:15]:
                print(f"  {issue}")

        print("\n--- strict unmerged ---")
        merged_peds = set()
        for row, showcase in iter_showcase_tasks(session):
            ped = pedagogical_slot_id_from_showcase(showcase) or ""
            if len(available_language_tracks(showcase)) == 2 and ped:
                merged_peds.add(ped)
        for pas, py in sorted(all_mirrored_pairs().items()):
            if pas not in merged_peds:
                print(f"unmerged: {pas}<->{py}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
