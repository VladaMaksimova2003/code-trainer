"""Repair corrupted Universal Core merges and re-apply strict mirror pairs."""

from __future__ import annotations

import argparse
import sys
from copy import deepcopy
from pathlib import Path

from sqlalchemy.orm.attributes import flag_modified

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.curriculum_slot_mirror_map import (
    all_mirrored_pairs,
    all_semantic_related_pairs,
    is_semantic_related_pair,
)
from application.curriculum.mirror.pedagogical_task_model import (
    available_language_tracks,
    extract_track_fields,
    is_universal_core_showcase,
    merge_showcase_pair,
    normalize_unified_showcase,
)
from application.curriculum.mirror.pedagogical_task_store import (
    _TRACK_FIELD_KEYS,
    canonical_pedagogical_slot_id,
    pedagogical_slot_id_from_showcase,
)
from application.curriculum.mirror.universal_core_validation import (
    validate_mirror_pairs_merged,
    validate_semantic_pairs_not_merged_as_strict,
)
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    find_showcase_task_by_slug as find_pascal,
)
from application.curriculum.python.showcase.python_showcase_core import (
    find_showcase_task_by_slug as find_python,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.session import SessionLocal
from scripts.merge_mirrored_showcase_tasks import merge_pair

load_models()


def _track_slug(showcase: dict, lang: str) -> str:
    track = (showcase.get("language_tracks") or {}).get(lang) or {}
    return str(track.get("slug") or "").strip()


def _iter_showcase_rows(session, *, include_deleted: bool = False):
    rows = session.query(TaskModel).all()
    for row in rows:
        if not include_deleted and row.is_delete:
            continue
        examples = row.code_examples or {}
        showcase = examples.get("curriculum_showcase")
        if isinstance(showcase, dict) and showcase:
            yield row, showcase


def find_task_by_track_slug(
    session,
    slug: str,
    *,
    language: str | None = None,
    include_deleted: bool = False,
) -> TaskModel | None:
    slug = str(slug or "").strip()
    if not slug:
        return None
    for row, showcase in _iter_showcase_rows(session, include_deleted=include_deleted):
        top = str(showcase.get("slug") or "").strip()
        if top == slug:
            if language is None:
                return row
            target = str(showcase.get("target_language") or "").lower()
            if target == language:
                return row
        tracks = showcase.get("language_tracks") or {}
        if isinstance(tracks, dict):
            if language:
                if _track_slug(showcase, language) == slug:
                    return row
            else:
                for lang in tracks:
                    if _track_slug(showcase, lang) == slug:
                        return row
    return None


def _single_language_showcase(track: dict, *, language: str) -> dict:
    showcase = dict(track)
    showcase.pop("language_tracks", None)
    showcase["target_language"] = language
    showcase["language"] = language
    slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
    ped = canonical_pedagogical_slot_id(slot_id=slug, slug=slug, language=language)
    if ped:
        showcase["pedagogical_slot_id"] = ped
    return showcase


def _language_for_track_slug(slug: str, fallback: str) -> str:
    prefix = slug.split("_")[0]
    if prefix.startswith("py") and prefix not in {"pyl", "pyt"}:
        return "python"
    if prefix in {"pyk", "pyt", "pyi", "pye", "pyc", "pyl", "pyf", "pypr", "pya", "pyd", "pys", "pyr", "pyfl", "pym", "pyrc", "pyo", "pypit", "pydg"}:
        return "python"
    return fallback


def split_unified_task(session, row: TaskModel, *, dry_run: bool) -> list[str]:
    examples = dict(row.code_examples or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    if not is_universal_core_showcase(showcase):
        return []

    tracks = showcase.get("language_tracks") or {}
    if not isinstance(tracks, dict) or len(tracks) < 2:
        return []

    actions: list[str] = []
    saved_tracks = {lang: dict(track) for lang, track in tracks.items() if isinstance(track, dict)}

    pascal_track = saved_tracks.get("pascal")
    if pascal_track:
        pas_slug = str(pascal_track.get("slug") or "").strip()
        pas_lang = _language_for_track_slug(pas_slug, "pascal")
        actions.append(f"split-pascal:{pas_slug}:task-{row.id}")
        if not dry_run:
            pas_single = _single_language_showcase(pascal_track, language=pas_lang)
            new_examples = deepcopy(row.code_examples or {})
            new_examples["curriculum_showcase"] = pas_single
            row.code_examples = new_examples
            flag_modified(row, "code_examples")
            session.flush()

    python_track = saved_tracks.get("python")
    if python_track:
        py_slug = str(python_track.get("slug") or "").strip()
        py_lang = _language_for_track_slug(py_slug, "python")
        existing = find_task_by_track_slug(session, py_slug, language=py_lang, include_deleted=True)
        actions.append(f"split-python:{py_slug}:task-{row.id}")
        if not dry_run:
            py_single = _single_language_showcase(python_track, language=py_lang)
            if existing and existing.id != row.id:
                existing.is_delete = False
                ex = deepcopy(existing.code_examples or {})
                ex["curriculum_showcase"] = py_single
                existing.code_examples = ex
                flag_modified(existing, "code_examples")
            else:
                py_row = TaskModel(
                    title=row.title,
                    description=row.description,
                    task_type=row.task_type,
                    difficulty=row.difficulty,
                    is_delete=False,
                    code_examples={},
                )
                py_examples = deepcopy(row.code_examples or {})
                py_examples["curriculum_showcase"] = py_single
                py_row.code_examples = py_examples
                session.add(py_row)
                session.flush()
                actions[-1] = f"split-python-created:{py_slug}:task-{py_row.id}"
    return actions


def repair_semantic_merges(session, *, dry_run: bool) -> list[str]:
    actions: list[str] = []
    for row, showcase in _iter_showcase_rows(session):
        if not is_universal_core_showcase(showcase):
            continue
        pas_slug = _track_slug(showcase, "pascal")
        py_slug = _track_slug(showcase, "python")
        if is_semantic_related_pair(pas_slug, py_slug):
            actions.append(f"split-semantic:{pas_slug}<->{py_slug}:task-{row.id}")
            actions.extend(split_unified_task(session, row, dry_run=dry_run))
    return actions


def repair_wrong_ped_tasks(session, *, dry_run: bool) -> list[str]:
    """Split unified tasks whose pedagogical_slot_id does not match expected pascal track slug."""
    actions: list[str] = []
    pairs = all_mirrored_pairs()
    for row, showcase in _iter_showcase_rows(session):
        if not is_universal_core_showcase(showcase):
            continue
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        pas_slug = _track_slug(showcase, "pascal")
        py_slug = _track_slug(showcase, "python")
        expected_py = pairs.get(ped) or pairs.get(pas_slug)
        if is_semantic_related_pair(pas_slug, py_slug) or is_semantic_related_pair(ped, py_slug):
            actions.append(f"split-semantic-strict:{pas_slug}<->{py_slug}:task-{row.id}")
            actions.extend(split_unified_task(session, row, dry_run=dry_run))
        elif ped in pairs and (pas_slug != ped or py_slug != expected_py):
            actions.append(f"split-wrong-ped:{ped}:task-{row.id}:got-{pas_slug}+{py_slug}")
            actions.extend(split_unified_task(session, row, dry_run=dry_run))
        elif ped and ped not in pairs and pas_slug in pairs:
            expected = pairs[pas_slug]
            if py_slug != expected:
                actions.append(f"split-wrong-py:{pas_slug}:task-{row.id}:got-{py_slug}")
                actions.extend(split_unified_task(session, row, dry_run=dry_run))
    return actions


def restore_deleted_pascal_tasks(session, *, dry_run: bool) -> list[str]:
    actions: list[str] = []
    for pas, _py in all_mirrored_pairs().items():
        if find_task_by_track_slug(session, pas, language="pascal"):
            continue
        deleted = find_task_by_track_slug(session, pas, language="pascal", include_deleted=True)
        if deleted and deleted.is_delete:
            actions.append(f"restore-pascal:{pas}:task-{deleted.id}")
            if not dry_run:
                deleted.is_delete = False
                flag_modified(deleted, "is_delete")
    return actions


def restore_deleted_python_tasks(session, *, dry_run: bool) -> list[str]:
    actions: list[str] = []
    for _pas, py_slug in all_mirrored_pairs().items():
        if find_python(session, py_slug):
            continue
        deleted = find_task_by_track_slug(session, py_slug, language="python", include_deleted=True)
        if deleted and deleted.is_delete:
            actions.append(f"restore:{py_slug}:task-{deleted.id}")
            if not dry_run:
                deleted.is_delete = False
                flag_modified(deleted, "is_delete")
    return actions


def cleanup_bogus_split_tasks(session, *, dry_run: bool) -> list[str]:
    """Remove orphan rows created from corrupted unified splits (wrong-language slug)."""
    actions: list[str] = []
    for row, showcase in _iter_showcase_rows(session):
        if is_universal_core_showcase(showcase):
            continue
        lang = str(showcase.get("target_language") or "").lower()
        slug = str(showcase.get("slug") or "").strip()
        if lang == "python" and slug.startswith(("lop_", "pit_", "dyn_", "str_", "cdg_")):
            actions.append(f"delete-bogus-python:{slug}:task-{row.id}")
            if not dry_run:
                row.is_delete = True
                flag_modified(row, "is_delete")
    return actions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remerge", action="store_true", help="Re-run strict merge after repair")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        all_actions: list[str] = []
        all_actions.extend(repair_semantic_merges(session, dry_run=args.dry_run))
        all_actions.extend(repair_wrong_ped_tasks(session, dry_run=args.dry_run))
        all_actions.extend(restore_deleted_pascal_tasks(session, dry_run=args.dry_run))
        all_actions.extend(restore_deleted_python_tasks(session, dry_run=args.dry_run))
        all_actions.extend(cleanup_bogus_split_tasks(session, dry_run=args.dry_run))

        if not args.dry_run:
            session.commit()

        if args.remerge and not args.dry_run:
            session.close()
            session = SessionLocal()
            for pas, py in sorted(all_mirrored_pairs().items()):
                result = merge_pair(session, pas, py, dry_run=False)
                if result and not result.endswith("already-unified"):
                    all_actions.append(result)

        if not args.dry_run:
            session.commit()

        for line in all_actions:
            print(line)

        if not args.dry_run:
            print(f"semantic_pairs: {len(all_semantic_related_pairs())}")
            print(f"strict_issues: {len(validate_mirror_pairs_merged(session))}")
            print(f"semantic_merged: {len(validate_semantic_pairs_not_merged_as_strict(session))}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
