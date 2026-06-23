"""Lightweight task listing for student home — no heavy payload enrichment."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, load_only

from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from application.curriculum.mirror.curriculum_slot_mirror import canonical_title_for_slot
from application.curriculum.mirror.pedagogical_task_model import (
    available_language_tracks,
    concept_id_for_showcase,
)
from application.curriculum.mirror.pedagogical_task_store import (
    pedagogical_slot_id_from_showcase,
    resolved_showcase,
    showcase_matches_collection,
    unified_pedagogical_slot_key,
)
from infrastructure.db.models.task.task import Task as TaskModel
from shared.enums import AssignmentType

_HEAVY_OVERVIEW_KEYS = frozenset(
    {
        "code_examples",
        "test_cases",
        "blocks",
        "template",
        "construction_hints",
        "solution_description",
        "algorithm_hint",
        "source_code",
        "flow_spec",
        "diagram",
        "language_variants",
        "description",
    }
)


def _public_task_type(task_type: str) -> str:
    try:
        parsed = AssignmentType.parse(task_type)
        return "blocks" if parsed == AssignmentType.TASK_FLOWCHART_TO_CODE else parsed.value
    except ValueError:
        return "blocks" if task_type == "diagram" else task_type


def _showcase_meta(code_examples: dict[str, Any] | None) -> dict[str, Any]:
    raw = (code_examples or {}).get("curriculum_showcase") or {}
    return dict(raw) if isinstance(raw, dict) else {}


def _constructions_from_code_examples(code_examples: dict[str, Any] | None) -> list[str]:
    patterns = (code_examples or {}).get("patterns")
    if not isinstance(patterns, list):
        return []
    return [str(item) for item in patterns if str(item).strip()]


def _overview_dedupe_key(raw_showcase: dict[str, Any], row_id: int) -> str:
    """One pedagogical slot may still have legacy mirror rows in DB."""
    unified = unified_pedagogical_slot_key(raw_showcase)
    if unified:
        return f"ped:{unified}"
    return f"row:{row_id}"


def _display_title(raw_title: str, slot_id: str | None) -> str:
    stripped = strip_showcase_title_prefix(str(raw_title or ""))
    canonical = canonical_title_for_slot(slot_id)
    if stripped and (not canonical or stripped != canonical):
        return stripped
    if canonical:
        return canonical
    return stripped


def _course_title_prefix(course: str | None) -> str | None:
    # Unified v4 tasks use chapter-only titles shared across language tracks.
    del course
    return None


def task_row_to_overview(
    task: TaskModel,
    *,
    target_language: str | None = None,
) -> dict[str, Any]:
    raw_showcase = _showcase_meta(task.code_examples)
    showcase = resolved_showcase(raw_showcase, target_language)
    ped_id = unified_pedagogical_slot_key(raw_showcase) or pedagogical_slot_id_from_showcase(raw_showcase)
    tracks = available_language_tracks(raw_showcase)
    course_key = str(showcase.get("target_language") or "").strip().lower() or None
    if not course_key and tracks:
        course_key = tracks[0]
    chapter_key = showcase.get("collection_key")
    slot_id = showcase.get("slot_id") or showcase.get("slug")
    task_format = showcase.get("task_format")
    concept_id = concept_id_for_showcase(showcase) or concept_id_for_showcase(raw_showcase)
    public_type = _public_task_type(task.task_type)
    display_slot = ped_id or slot_id

    return {
        "id": task.id,
        "slot_id": slot_id,
        "pedagogical_slot_id": ped_id,
        "concept_id": concept_id,
        "title": _display_title(task.title, str(display_slot) if display_slot else None),
        "language": course_key,
        "target_language": course_key,
        "course_key": course_key,
        "chapter_key": chapter_key,
        "available_language_tracks": tracks,
        "task_format": task_format,
        "difficulty": task.difficulty,
        "type": public_type,
        "task_type": public_type,
        "constructions": _constructions_from_code_examples(task.code_examples),
        "attempted": False,
        "solved": False,
        "completed": False,
        "submissions_count": 0,
    }


def _matches_list_filters(
    item: dict[str, Any],
    *,
    search: str | None = None,
    task_type: str | None = None,
    difficulty: str | None = None,
    pattern: str | None = None,
    language: str | None = None,
) -> bool:
    if search:
        needle = search.strip().lower()
        if needle and needle not in str(item.get("title") or "").lower():
            return False
    if task_type:
        normalized = task_type.strip()
        if normalized not in {str(item.get("type") or ""), str(item.get("task_type") or "")}:
            return False
    if difficulty:
        if str(item.get("difficulty") or "").lower() != difficulty.strip().lower():
            return False
    if pattern:
        constructions = [str(c) for c in (item.get("constructions") or [])]
        if pattern.strip() not in constructions:
            return False
    if language:
        normalized = language.strip().lower()
        tracks = [str(t).lower() for t in (item.get("available_language_tracks") or [])]
        course_key = str(item.get("course_key") or item.get("target_language") or "").lower()
        if tracks:
            if normalized not in tracks:
                return False
        elif course_key and course_key != normalized:
            return False
    return True


def _matches_filters(
    item: dict[str, Any],
    *,
    course: str | None,
    chapter: str | None,
    raw_showcase: dict[str, Any] | None = None,
) -> bool:
    if course:
        normalized = course.strip().lower()
        tracks = item.get("available_language_tracks") or []
        if tracks:
            if normalized not in [str(t).lower() for t in tracks]:
                return False
        elif (item.get("course_key") or "").lower() != normalized:
            return False
    if chapter and raw_showcase:
        normalized = chapter.strip().lower()
        lang = str(course or item.get("target_language") or "").strip().lower()
        if lang and showcase_matches_collection(
            raw_showcase,
            language=lang,
            collection_key=normalized,
        ):
            return True
        if (item.get("chapter_key") or "").lower() != normalized:
            return False
    elif chapter:
        normalized = chapter.strip().lower()
        if (item.get("chapter_key") or "").lower() != normalized:
            return False
    return True


def _sql_task_types(task_type: str | None) -> list[str] | None:
    if not task_type or str(task_type).strip().lower() == "all":
        return None
    normalized = str(task_type).strip()
    if normalized == "blocks":
        return ["diagram", AssignmentType.TASK_FLOWCHART_TO_CODE.value]
    return [normalized]


def _apply_sql_overview_filters(
    stmt,
    *,
    search: str | None = None,
    task_type: str | None = None,
    difficulty: str | None = None,
):
    if search and str(search).strip():
        stmt = stmt.where(TaskModel.title.ilike(f"%{search.strip()}%"))
    if difficulty and str(difficulty).strip().lower() != "all":
        stmt = stmt.where(
            func.lower(TaskModel.difficulty) == difficulty.strip().lower()
        )
    sql_types = _sql_task_types(task_type)
    if sql_types:
        stmt = stmt.where(TaskModel.task_type.in_(sql_types))
    return stmt


def _collect_overview_matches(
    rows: list[TaskModel],
    *,
    target_language: str | None,
    course: str | None,
    chapter: str | None,
    search: str | None,
    task_type: str | None,
    difficulty: str | None,
    pattern: str | None,
    language: str | None,
) -> list[dict[str, Any]]:
    lang = str(target_language or course or "").strip().lower() or None
    matched: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for row in rows:
        raw_showcase = _showcase_meta(row.code_examples)
        dedupe_key = _overview_dedupe_key(raw_showcase, int(row.id))
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        overview = task_row_to_overview(row, target_language=lang)
        if course or chapter:
            if not _matches_filters(
                overview,
                course=course or lang,
                chapter=chapter,
                raw_showcase=raw_showcase,
            ):
                continue
        if not _matches_list_filters(
            overview,
            search=search,
            task_type=task_type,
            difficulty=difficulty,
            pattern=pattern,
            language=language or lang,
        ):
            continue
        matched.append(overview)
    return matched


def list_task_overviews(
    db: Session,
    *,
    allowed_task_ids: set[int] | None,
    course: str | None = None,
    chapter: str | None = None,
    target_language: str | None = None,
    search: str | None = None,
    task_type: str | None = None,
    difficulty: str | None = None,
    pattern: str | None = None,
    language: str | None = None,
    restrict_task_ids: set[int] | None = None,
    page: int = 1,
    page_size: int | None = None,
) -> dict[str, Any]:
    effective_allowed = allowed_task_ids
    if restrict_task_ids is not None:
        if effective_allowed is not None:
            effective_allowed = effective_allowed & restrict_task_ids
        else:
            effective_allowed = restrict_task_ids

    stmt = (
        select(TaskModel)
        .where(TaskModel.is_delete.is_(False))
        .options(
            load_only(
                TaskModel.id,
                TaskModel.title,
                TaskModel.difficulty,
                TaskModel.task_type,
                TaskModel.code_examples,
            )
        )
        .order_by(TaskModel.id.asc())
    )
    if effective_allowed is not None:
        if not effective_allowed:
            return {"tasks": [], "total": 0, "page": page, "page_size": page_size or 0}
        stmt = stmt.where(TaskModel.id.in_(effective_allowed))

    lang = str(target_language or course or "").strip().lower() or None
    course_prefix = _course_title_prefix(lang) if lang else None
    if course_prefix:
        stmt = stmt.where(TaskModel.title.like(f"{course_prefix}%"))
    stmt = _apply_sql_overview_filters(
        stmt,
        search=search,
        task_type=task_type,
        difficulty=difficulty,
    )
    rows = list(db.execute(stmt).scalars().all())
    matched_items = _collect_overview_matches(
        rows,
        target_language=lang,
        course=course,
        chapter=chapter,
        search=search,
        task_type=task_type,
        difficulty=difficulty,
        pattern=pattern,
        language=language,
    )

    total = len(matched_items)
    if page_size is not None and page_size > 0:
        safe_page = max(page, 1)
        start = (safe_page - 1) * page_size
        items = matched_items[start : start + page_size]
        return {
            "tasks": items,
            "total": total,
            "page": safe_page,
            "page_size": page_size,
        }

    return {
        "tasks": matched_items,
        "total": total,
        "page": 1,
        "page_size": total,
    }


def count_accessible_tasks(db: Session, allowed_task_ids: set[int] | None) -> int:
    stmt = select(func.count()).select_from(TaskModel).where(TaskModel.is_delete.is_(False))
    if allowed_task_ids is not None:
        if not allowed_task_ids:
            return 0
        stmt = stmt.where(TaskModel.id.in_(allowed_task_ids))
    return int(db.execute(stmt).scalar_one())


def overview_item_has_no_heavy_fields(item: dict[str, Any]) -> bool:
    return not any(key in item for key in _HEAVY_OVERVIEW_KEYS)
