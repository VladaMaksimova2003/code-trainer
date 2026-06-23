"""Remove duplicate mirror task rows — one pedagogical slot = one task id."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from sqlalchemy.orm.attributes import flag_modified

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.curriculum_slot_mirror_map import all_mirrored_pairs  # noqa: E402
from application.curriculum.mirror.pedagogical_task_model import (  # noqa: E402
    available_language_tracks,
)
from application.curriculum.mirror.pedagogical_task_store import (  # noqa: E402
    iter_showcase_tasks,
    pedagogical_slot_id_from_showcase,
    track_slug,
)
from application.curriculum.mirror.universal_core_validation import (  # noqa: E402
    collect_universal_core_stats,
    run_all_validations,
)
from infrastructure.db.models.task.registry import load_models  # noqa: E402
from infrastructure.db.session import SessionLocal  # noqa: E402
from scripts.cleanup_universal_core_duplicates import (  # noqa: E402
    dedupe_pedagogical_slot_ids,
    fix_pedagogical_slot_ids,
    restore_and_merge_pending,
    strip_bogus_language_tracks,
)
from scripts.merge_mirrored_showcase_tasks import merge_pair  # noqa: E402

load_models()


def _score_row(row_id: int, showcase: dict, ped: str) -> tuple[int, int]:
    tracks = available_language_tracks(showcase)
    score = len(tracks) * 100
    if str(showcase.get("pedagogical_slot_id") or "") == ped:
        score += 50
    if showcase.get("language_tracks"):
        score += 25
    return (score, row_id)


def _canonical_owner_by_ped(session) -> dict[str, int]:
    by_ped: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for row, showcase in iter_showcase_tasks(session):
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        if ped:
            by_ped[ped].append((row.id, showcase))
    owners: dict[str, int] = {}
    for ped, items in by_ped.items():
        keep_id, _ = max(items, key=lambda item: _score_row(item[0], item[1], ped))
        owners[ped] = keep_id
    return owners


def _slug_owner_index(session) -> dict[tuple[str, str], int]:
    """Map (language, slug) -> canonical task id that owns this track."""
    index: dict[tuple[str, str], int] = {}
    owners = _canonical_owner_by_ped(session)
    for row, showcase in iter_showcase_tasks(session):
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        owner_id = owners.get(ped, row.id)
        for lang in available_language_tracks(showcase) or [
            str(showcase.get("target_language") or "").lower()
        ]:
            slug = track_slug(showcase, lang) or str(showcase.get("slug") or "").strip()
            if lang and slug:
                index[(lang, slug)] = owner_id
    return index


def delete_mirror_slug_duplicates(session, *, dry_run: bool) -> list[str]:
    """Soft-delete standalone rows whose slug is already on a unified canonical task."""
    actions: list[str] = []
    slug_index = _slug_owner_index(session)
    ped_owners = _canonical_owner_by_ped(session)

    for row, showcase in iter_showcase_tasks(session):
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
        lang = str(showcase.get("target_language") or "").lower()
        tracks = available_language_tracks(showcase)

        owner_id = ped_owners.get(ped)
        if owner_id and owner_id != row.id:
            if dry_run:
                actions.append(f"would-delete-duplicate-ped:{ped}:keep-{owner_id}:drop-{row.id}")
            else:
                row.is_delete = True
                flag_modified(row, "is_delete")
                actions.append(f"deleted-duplicate-ped:{ped}:keep-{owner_id}:drop-{row.id}")
            continue

        if len(tracks) >= 2:
            continue

        if not slug or not lang:
            continue

        canonical_id = slug_index.get((lang, slug))
        if canonical_id is None or canonical_id == row.id:
            continue

        if dry_run:
            actions.append(
                f"would-delete-mirror-slug:{lang}:{slug}:keep-{canonical_id}:drop-{row.id}"
            )
        else:
            row.is_delete = True
            flag_modified(row, "is_delete")
            actions.append(
                f"deleted-mirror-slug:{lang}:{slug}:keep-{canonical_id}:drop-{row.id}"
            )

    return actions


def merge_all_pairs(session, *, dry_run: bool) -> list[str]:
    actions: list[str] = []
    for pas, py in sorted(all_mirrored_pairs().items()):
        if dry_run:
            actions.append(f"would-merge-pair:{pas}<->{py}")
        else:
            result = merge_pair(session, pas, py, dry_run=False)
            if result and not result.endswith("already-unified"):
                actions.append(result)
    return actions


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove mirror task duplicates from DB")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-merge", action="store_true")
    args = parser.parse_args()

    session = SessionLocal()
    actions: list[str] = []
    try:
        if not args.skip_merge:
            actions.extend(merge_all_pairs(session, dry_run=args.dry_run))
            if not args.dry_run:
                session.flush()

        if not args.dry_run:
            actions.extend(strip_bogus_language_tracks(session))
            session.flush()
            actions.extend(fix_pedagogical_slot_ids(session))
            session.flush()
            actions.extend(dedupe_pedagogical_slot_ids(session))
            session.flush()
            actions.extend(restore_and_merge_pending(session))
            session.flush()
            actions.extend(delete_mirror_slug_duplicates(session, dry_run=False))
            session.commit()
        else:
            actions.extend(delete_mirror_slug_duplicates(session, dry_run=True))

        validation = run_all_validations(session)
        stats = collect_universal_core_stats(session)

        for line in actions:
            print(line)

        print("\n--- validation ---")
        for name, issues in validation.items():
            status = "OK" if not issues else f"FAIL ({len(issues)})"
            print(f"  {name}: {status}")
            for issue in issues[:5]:
                print(f"    - {issue}")

        print("\n--- stats ---")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
