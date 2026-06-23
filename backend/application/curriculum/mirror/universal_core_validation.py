"""Validation helpers for Universal Core merge integrity."""

from __future__ import annotations

from collections import Counter
from typing import Any

from application.curriculum.mirror.curriculum_slot_mirror_map import (
    PYTHON_ONLY_CHAPTERS,
    PYTHON_ONLY_SLOTS,
    all_mirrored_pairs,
    all_semantic_related_pairs,
    is_python_only_slot,
    is_semantic_related_pair,
)
from application.curriculum.mirror.pedagogical_task_model import (
    FORBIDDEN_PRIMARY_ACTIONS,
    FORBIDDEN_TASK_FORMATS,
    PASCAL_ONLY_CONCEPTS,
    PYTHON_ONLY_CONCEPTS,
    available_language_tracks,
    concept_id_for_showcase,
    is_universal_core_showcase,
    neutral_title_for_showcase,
)
from application.curriculum.mirror.pedagogical_task_store import (
    iter_showcase_tasks,
    pedagogical_slot_id_from_showcase,
)
from sqlalchemy.orm import Session


def _active_showcase_tasks(session: Session) -> list[tuple[Any, dict[str, Any]]]:
    return [(row, showcase) for row, showcase in iter_showcase_tasks(session)]


def validate_no_duplicate_pedagogical_slot_ids(session: Session) -> list[str]:
    errors: list[str] = []
    counts: Counter[str] = Counter()
    owners: dict[str, list[int]] = {}
    for row, showcase in _active_showcase_tasks(session):
        ped = pedagogical_slot_id_from_showcase(showcase)
        if not ped:
            continue
        counts[ped] += 1
        owners.setdefault(ped, []).append(int(row.id))
    for ped, count in counts.items():
        if count > 1:
            errors.append(f"duplicate pedagogical_slot_id={ped} task_ids={owners[ped]}")
    return errors


def validate_mirror_pairs_merged(session: Session) -> list[str]:
    errors: list[str] = []
    by_ped: dict[str, dict[str, Any]] = {}
    for _row, showcase in _active_showcase_tasks(session):
        ped = pedagogical_slot_id_from_showcase(showcase)
        if ped:
            by_ped[ped] = showcase

    for pascal_slot, python_slot in all_mirrored_pairs().items():
        ped = pascal_slot
        showcase = by_ped.get(ped)
        if showcase is None:
            errors.append(f"missing unified task for pair {pascal_slot}<->{python_slot}")
            continue
        tracks = available_language_tracks(showcase)
        if "pascal" not in tracks or "python" not in tracks:
            errors.append(
                f"pair {pascal_slot}<->{python_slot} missing tracks: {tracks}"
            )
        p_track = (showcase.get("language_tracks") or {}).get("pascal") or {}
        py_track = (showcase.get("language_tracks") or {}).get("python") or {}
        if str(p_track.get("slug") or "") != pascal_slot:
            errors.append(
                f"{ped}: expected pascal slug {pascal_slot}, got {p_track.get('slug')}"
            )
        if str(py_track.get("slug") or "") != python_slot:
            errors.append(
                f"{ped}: expected python slug {python_slot}, got {py_track.get('slug')}"
            )
    return errors


def validate_semantic_pairs_not_merged_as_strict(session: Session) -> list[str]:
    """Type B pairs must not appear as a single unified strict-mirror task."""
    errors: list[str] = []
    for row, showcase in _active_showcase_tasks(session):
        if not is_universal_core_showcase(showcase):
            continue
        tracks = available_language_tracks(showcase)
        if len(tracks) != 2:
            continue
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        p_track = (showcase.get("language_tracks") or {}).get("pascal") or {}
        py_track = (showcase.get("language_tracks") or {}).get("python") or {}
        pas_slug = str(p_track.get("slug") or "").strip()
        py_slug = str(py_track.get("slug") or "").strip()
        if is_semantic_related_pair(pas_slug, py_slug) or is_semantic_related_pair(ped, py_slug):
            errors.append(
                f"semantic pair {pas_slug}<->{py_slug} wrongly merged as strict (task {row.id})"
            )
    return errors


def validate_group_c_not_merged(session: Session) -> list[str]:
    errors: list[str] = []
    for row, showcase in _active_showcase_tasks(session):
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        tracks = available_language_tracks(showcase)
        slug = str(showcase.get("slug") or "").strip()
        chapter = str(showcase.get("collection_key") or "").strip()
        concept = concept_id_for_showcase(showcase)

        if is_python_only_slot(slug) or chapter in PYTHON_ONLY_CHAPTERS:
            if "pascal" in tracks:
                errors.append(f"python-only {slug} incorrectly has pascal track")
            if slug in PYTHON_ONLY_SLOTS and "python" not in tracks and len(tracks) != 1:
                errors.append(f"python-only slot {slug} should have single python track")
            continue

        if concept in PASCAL_ONLY_CONCEPTS and "python" in tracks:
            errors.append(f"pascal-only concept {concept} on {ped} has python track")

        if concept in PYTHON_ONLY_CONCEPTS and "pascal" in tracks and is_universal_core_showcase(showcase):
            errors.append(f"python-only concept {concept} on {ped} merged with pascal")

        if len(tracks) == 2 and is_python_only_slot(slug):
            errors.append(f"python-only slot {slug} merged into universal core")
    return errors


def validate_forbidden_formats(session: Session) -> list[str]:
    errors: list[str] = []
    for row, showcase in _active_showcase_tasks(session):
        fmt = str(showcase.get("task_format") or "").strip().lower()
        if fmt in FORBIDDEN_TASK_FORMATS:
            errors.append(f"task {row.id}: forbidden task_format={fmt}")
        action = str(showcase.get("primary_action") or "").strip().lower()
        if action in FORBIDDEN_PRIMARY_ACTIONS:
            errors.append(f"task {row.id}: forbidden primary_action={action}")
        tracks = showcase.get("language_tracks") or {}
        if isinstance(tracks, dict):
            for lang, track in tracks.items():
                if not isinstance(track, dict):
                    continue
                t_fmt = str(track.get("task_format") or fmt).strip().lower()
                if t_fmt in FORBIDDEN_TASK_FORMATS:
                    errors.append(f"task {row.id} track {lang}: forbidden task_format={t_fmt}")
                t_action = str(track.get("primary_action") or action).strip().lower()
                if t_action in FORBIDDEN_PRIMARY_ACTIONS:
                    errors.append(f"task {row.id} track {lang}: forbidden primary_action={t_action}")
    return errors


def validate_neutral_titles(session: Session) -> list[str]:
    errors: list[str] = []
    banned = ("Pascal", "Python", "Java", "C#", "C++")
    for row, showcase in _active_showcase_tasks(session):
        title = str(row.title or "")
        for token in banned:
            if token in title and not title.startswith("["):
                errors.append(f"task {row.id}: non-neutral title contains {token!r}")
                break
        neutral = neutral_title_for_showcase(showcase)
        if is_universal_core_showcase(showcase) and not neutral:
            errors.append(f"task {row.id}: universal core without canonical title")
    return errors


def run_all_validations(session: Session) -> dict[str, list[str]]:
    return {
        "duplicate_pedagogical_slot_ids": validate_no_duplicate_pedagogical_slot_ids(session),
        "mirror_pairs_not_merged": validate_mirror_pairs_merged(session),
        "semantic_pairs_merged_as_strict": validate_semantic_pairs_not_merged_as_strict(session),
        "group_c_incorrectly_merged": validate_group_c_not_merged(session),
        "forbidden_formats": validate_forbidden_formats(session),
        "non_neutral_titles": validate_neutral_titles(session),
    }


def collect_universal_core_stats(session: Session) -> dict[str, Any]:
    pairs = all_mirrored_pairs()
    semantic = all_semantic_related_pairs()
    stats = {
        "active_showcase_tasks": 0,
        "unified_tasks": 0,
        "language_tracks_pascal": 0,
        "language_tracks_python": 0,
        "pascal_only_tasks": 0,
        "python_only_tasks": 0,
        "both_tracks_tasks": 0,
        "pedagogical_slot_ids": set(),
        "unmerged_pairs": [],
        "semantic_related_pairs_count": len(semantic),
        "manual_review": [],
    }
    merged_peds: set[str] = set()
    for row, showcase in _active_showcase_tasks(session):
        stats["active_showcase_tasks"] += 1
        ped = pedagogical_slot_id_from_showcase(showcase) or ""
        if ped:
            stats["pedagogical_slot_ids"].add(ped)
        tracks = available_language_tracks(showcase)
        slug = str(showcase.get("slug") or "").strip()
        chapter = str(showcase.get("collection_key") or "").strip()

        if "pascal" in tracks:
            stats["language_tracks_pascal"] += 1
        if "python" in tracks:
            stats["language_tracks_python"] += 1
        if len(tracks) == 2:
            stats["both_tracks_tasks"] += 1
            stats["unified_tasks"] += 1
            if ped:
                merged_peds.add(ped)
        elif is_python_only_slot(slug) or chapter in PYTHON_ONLY_CHAPTERS:
            stats["python_only_tasks"] += 1
        elif "pascal" in tracks and "python" not in tracks:
            stats["pascal_only_tasks"] += 1
        elif "python" in tracks and "pascal" not in tracks:
            stats["python_only_tasks"] += 1

        if not neutral_title_for_showcase(showcase):
            stats["manual_review"].append({"task_id": row.id, "reason": "missing_canonical_title", "slug": slug})

    for pascal_slot, python_slot in pairs.items():
        if pascal_slot not in merged_peds:
            stats["unmerged_pairs"].append({"pascal": pascal_slot, "python": python_slot})

    stats["pedagogical_slot_count"] = len(stats["pedagogical_slot_ids"])
    stats["mirror_pairs_total"] = len(pairs)
    stats["pedagogical_slot_ids"] = sorted(stats["pedagogical_slot_ids"])
    return stats
