"""Per-language progress for curriculum showcase task cards."""

from __future__ import annotations

from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from application.curriculum.mirror.curriculum_slot_mirror import (
    ALL_CURRICULUM_LANGUAGES,
    ALGO_V4_SLOT_RE,
)
from application.curriculum.mirror.pedagogical_task_model import available_language_tracks
from application.curriculum.progress.student_curriculum_progress_service import (
    PROGRESS_STATUS_FAILED,
    PROGRESS_STATUS_PASSED,
    get_batch_progress_cache,
)
from application.learning.skill_progress_service import normalize_curriculum_language
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task.task import Task as TaskModel

LanguageTrackState = str  # "solved" | "attempted" | "todo"


def effective_collection_total(progress: dict[str, Any] | None) -> int:
    if not progress:
        return 0
    catalog = int(progress.get("catalog_tasks") or 0)
    seeded = int(progress.get("total_tasks") or 0)
    if seeded <= 0:
        return 0
    if catalog > 0 and seeded > catalog:
        return catalog
    return seeded


def display_collection_total(progress: dict[str, Any] | None) -> int:
    """Planned chapter size for UI (catalog), falling back to seeded tasks."""
    if not progress:
        return 0
    catalog = int(progress.get("catalog_tasks") or 0)
    if catalog > 0:
        return catalog
    return int(progress.get("total_tasks") or 0)


def language_is_available(collections: list[dict[str, Any]]) -> bool:
    if not collections:
        return False
    return sum(effective_collection_total(item.get("progress") or {}) for item in collections) > 0


def _tracks_for_task(session: Session, task_id: int, slug: str | None = None) -> list[str]:
    row = session.get(TaskModel, task_id)
    if row is not None:
        showcase = (row.code_examples or {}).get("curriculum_showcase") or {}
        if isinstance(showcase, dict):
            tracks = available_language_tracks(showcase)
            if tracks:
                return tracks
    if slug and ALGO_V4_SLOT_RE.match(str(slug).strip()):
        return list(ALL_CURRICULUM_LANGUAGES)
    return list(ALL_CURRICULUM_LANGUAGES)


def _states_from_submissions(
    session: Session,
    user_id: int,
    task_id: int,
    tracks: list[str],
) -> dict[str, LanguageTrackState]:
    track_set = {normalize_curriculum_language(lang) or str(lang).lower() for lang in tracks}
    rows = session.execute(
        select(
            Submission.language,
            func.max(case((Submission.success.is_(True), 1), else_=0)).label("solved"),
            func.count().label("submissions_count"),
        )
        .where(Submission.user_id == user_id, Submission.task_id == task_id)
        .group_by(Submission.language)
    ).all()
    states: dict[str, LanguageTrackState] = {}
    for row in rows:
        lang = normalize_curriculum_language(row.language)
        if not lang or lang not in track_set:
            continue
        if bool(row.solved):
            states[lang] = "solved"
        elif int(row.submissions_count or 0) > 0:
            states.setdefault(lang, "attempted")
    return states


def build_language_track_states(
    session: Session,
    user_id: int | None,
    task_id: int,
    *,
    slug: str | None = None,
) -> dict[str, LanguageTrackState]:
    if user_id is None:
        return {}
    tracks = _tracks_for_task(session, task_id, slug=slug)
    if not tracks:
        return {}

    states: dict[str, LanguageTrackState] = {}
    cache = get_batch_progress_cache()
    if cache:
        for lang in tracks:
            lang_key = normalize_curriculum_language(lang) or str(lang).lower()
            status = cache.get((int(task_id), lang_key))
            if status == PROGRESS_STATUS_PASSED:
                states[lang_key] = "solved"
            elif status == PROGRESS_STATUS_FAILED:
                states.setdefault(lang_key, "attempted")

    submission_states = _states_from_submissions(session, user_id, task_id, tracks)
    for lang, state in submission_states.items():
        if state == "solved" or states.get(lang) != "solved":
            states[lang] = state

    return states


def enrich_showcase_task_card(
    session: Session,
    user_id: int | None,
    card: dict[str, Any],
) -> dict[str, Any]:
    task_id = int(card.get("task_id") or 0)
    if not task_id:
        return card
    slug = str(card.get("slug") or "") or None
    tracks = _tracks_for_task(session, task_id, slug=slug)
    states = build_language_track_states(session, user_id, task_id, slug=slug)
    return {
        **card,
        "available_language_tracks": tracks,
        "language_track_states": states,
    }
