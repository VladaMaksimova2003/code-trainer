"""Final Universal Core cleanup: duplicate ped ids, artifact rows, pending merges."""

from __future__ import annotations

import sys
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from sqlalchemy.orm.attributes import flag_modified

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.curriculum_slot_mirror_map import (
    PYTHON_ONLY_CHAPTERS,
    PYTHON_ONLY_SLOTS,
    all_mirrored_pairs,
    all_semantic_related_pairs,
    is_semantic_related_pair,
    strict_python_to_pascal_slot,
)
from application.curriculum.mirror.pedagogical_task_model import (
    available_language_tracks,
    is_universal_core_showcase,
    normalize_unified_showcase,
)
from application.curriculum.mirror.pedagogical_task_store import (
    canonical_pedagogical_slot_id,
    iter_showcase_tasks,
    pedagogical_slot_id_from_showcase,
    track_slug,
)
from application.curriculum.mirror.universal_core_validation import (
    collect_universal_core_stats,
    run_all_validations,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.session import SessionLocal
from scripts.merge_mirrored_showcase_tasks import merge_pair

load_models()

# Split artifacts from prior repair runs — wrong ped, safe to soft-delete.
ARTIFACT_TASK_IDS = frozenset({644, 645})


def _set_showcase(row: TaskModel, showcase: dict) -> None:
    examples = deepcopy(row.code_examples or {})
    examples["curriculum_showcase"] = showcase
    row.code_examples = examples
    flag_modified(row, "code_examples")


def _score_canonical(row_id: int, showcase: dict, ped: str) -> tuple[int, int]:
    """Higher is better: unified strict pair > v3.1.1 showcase > single-language canonical slug."""
    tracks = available_language_tracks(showcase)
    pas = track_slug(showcase, "pascal") or str(showcase.get("slug") or "")
    py = track_slug(showcase, "python") or ""
    expected_py = all_mirrored_pairs().get(ped) or all_mirrored_pairs().get(pas)
    score = 0
    group = str(showcase.get("group") or "")
    if group.startswith(("pascal_curriculum_v311_", "python_curriculum_v311_", "cpp_curriculum_v311_")):
        score += 200
    if len(tracks) == 2 and pas == ped and py == expected_py:
        score += 100
    elif pas == ped and "pascal" in tracks:
        score += 50
    elif str(showcase.get("slug") or "") == ped:
        score += 30
    elif py and ped == strict_python_to_pascal_slot(py):
        score += 20
    return (score, row_id)


def strip_bogus_language_tracks(session) -> list[str]:
    """Remove placeholder language_tracks entries without slug (Group C / single-language rows)."""
    actions: list[str] = []
    for row, showcase in iter_showcase_tasks(session):
        tracks = dict(showcase.get("language_tracks") or {})
        if not tracks:
            continue
        slug = str(showcase.get("slug") or "").strip()
        chapter = str(showcase.get("collection_key") or "").strip()
        cleaned = {
            lang: dict(track)
            for lang, track in tracks.items()
            if isinstance(track, dict)
            and str(track.get("slug") or track.get("slot_id") or "").strip()
        }
        if cleaned == tracks:
            continue
        if slug in PYTHON_ONLY_SLOTS or chapter in PYTHON_ONLY_CHAPTERS:
            expected = {"python"}
        elif len(cleaned) == 1 and "pascal" in cleaned:
            expected = {"pascal"}
        elif len(cleaned) == 1 and "python" in cleaned:
            expected = {"python"}
        else:
            expected = set(cleaned.keys())
        if set(cleaned.keys()) != expected and len(expected) == 1:
            lang = next(iter(expected))
            cleaned = {lang: cleaned[lang]} if lang in cleaned else cleaned
        fixed = normalize_unified_showcase({**showcase, "language_tracks": cleaned})
        _set_showcase(row, fixed)
        actions.append(
            f"strip-bogus-tracks:task-{row.id}:slug-{slug}:"
            f"{sorted(tracks.keys())}->{sorted(cleaned.keys())}"
        )
    return actions


def fix_pedagogical_slot_ids(session) -> list[str]:
    actions: list[str] = []
    for row, showcase in iter_showcase_tasks(session):
        slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
        lang = str(showcase.get("target_language") or "pascal").lower()
        if not slug:
            continue
        expected = canonical_pedagogical_slot_id(slot_id=slug, slug=slug, language=lang)
        current = pedagogical_slot_id_from_showcase(showcase) or ""
        if expected and current != expected:
            fixed = dict(showcase)
            fixed["pedagogical_slot_id"] = expected
            _set_showcase(row, fixed)
            actions.append(f"fix-ped:{current}->{expected}:task-{row.id}:slug-{slug}")
    return actions


def dedupe_pedagogical_slot_ids(session) -> list[str]:
    actions: list[str] = []
    by_ped: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for row, showcase in iter_showcase_tasks(session):
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        if ped:
            by_ped[ped].append((row.id, showcase))

    for ped, owners in by_ped.items():
        if len(owners) < 2:
            continue
        ranked = sorted(owners, key=lambda item: _score_canonical(item[0], item[1], ped), reverse=True)
        keep_id, keep_showcase = ranked[0]
        for drop_id, drop_showcase in ranked[1:]:
            if drop_id in ARTIFACT_TASK_IDS:
                row = session.get(TaskModel, drop_id)
                if row and not row.is_delete:
                    row.is_delete = True
                    flag_modified(row, "is_delete")
                    actions.append(f"soft-delete-artifact:ped-{ped}:task-{drop_id}")
                continue
            drop_slug = str(drop_showcase.get("slug") or "")
            keep_tracks = available_language_tracks(keep_showcase)
            drop_tracks = available_language_tracks(drop_showcase)
            if (
                len(keep_tracks) == 2
                and len(drop_tracks) == 2
                and keep_tracks == drop_tracks
            ):
                actions.append(f"manual-review:ped-{ped}:ids={[o[0] for o in owners]}")
                continue
            row = session.get(TaskModel, drop_id)
            if row and not row.is_delete:
                row.is_delete = True
                flag_modified(row, "is_delete")
                actions.append(
                    f"soft-delete-duplicate:ped-{ped}:keep-{keep_id}:drop-{drop_id}:slug-{drop_slug}"
                )
    return actions


def restore_and_merge_pending(session) -> list[str]:
    actions: list[str] = []
    for pas, py in sorted(all_mirrored_pairs().items()):
        merged_peds = {
            pedagogical_slot_id_from_showcase(sh) or ""
            for _r, sh in iter_showcase_tasks(session)
            if len(available_language_tracks(sh)) == 2
        }
        if pas in merged_peds:
            continue
        for slug, lang in ((pas, "pascal"), (py, "python")):
            from scripts.repair_universal_core_merges import find_task_by_track_slug

            row = find_task_by_track_slug(session, slug, language=lang, include_deleted=True)
            if row and row.is_delete:
                row.is_delete = False
                flag_modified(row, "is_delete")
                actions.append(f"restore-for-merge:{slug}:task-{row.id}")
        session.flush()
        result = merge_pair(session, pas, py, dry_run=False)
        if result and not result.endswith("already-unified"):
            actions.append(result)
    return actions


def main() -> None:
    session = SessionLocal()
    all_actions: list[str] = []
    try:
        all_actions.extend(strip_bogus_language_tracks(session))
        session.flush()
        all_actions.extend(fix_pedagogical_slot_ids(session))
        session.flush()
        all_actions.extend(dedupe_pedagogical_slot_ids(session))
        session.commit()

        session.close()
        session = SessionLocal()
        all_actions.extend(restore_and_merge_pending(session))
        session.commit()

        validation = run_all_validations(session)
        stats = collect_universal_core_stats(session)

        for line in all_actions:
            print(line)

        print("\n--- validation ---")
        for name, issues in validation.items():
            status = "OK" if not issues else f"FAIL ({len(issues)})"
            print(f"  {name}: {status}")
            for issue in issues[:10]:
                print(f"    - {issue}")

        print("\n--- final report ---")
        print(f"active_showcase_tasks: {stats['active_showcase_tasks']}")
        print(f"unified_tasks: {stats['unified_tasks']}")
        print(f"pascal_only_tasks: {stats['pascal_only_tasks']}")
        print(f"python_only_tasks: {stats['python_only_tasks']}")
        print(f"semantic_related_pairs_count: {stats['semantic_related_pairs_count']}")
        print(f"strict_mirror_pairs_count: {stats['mirror_pairs_total']}")
        print(f"unmerged_strict_pairs: {len(stats['unmerged_pairs'])}")
        if stats["unmerged_pairs"]:
            for pair in stats["unmerged_pairs"]:
                print(f"  unmerged: {pair}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
