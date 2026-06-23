"""Next-task selection for Pascal showcase collections."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.curriculum.display.chapter_task_display_order import showcase_row_sort_key
from application.curriculum.collections.curriculum_next_service import (
    NEXT_TASK_ACTION_ORDER,
    _collection_button_label,
    _display_title,
    _progress_summary,
    _task_payload,
    resolve_next_in_ordered_tasks,
)
from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    PascalShowcaseTaskSpec,
    _is_v311_spec,
    collection_spec_seed_index,
    list_showcase_tasks_for_collection,
)
from application.curriculum.pascal.showcase.pascal_showcase_registry import (
    collection_by_key,
    effective_title_prefix,
)
from application.curriculum.pascal.showcase.pascal_v311_registry import v311_collection_by_key, v311_title_prefix
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import all_pascal_v311_showcase_specs
from application.curriculum.progress.student_curriculum_progress_service import (
    StudentCurriculumProgressService,
)

LANGUAGE = "pascal"


def _action_sort_key(action: str | None) -> int:
    if not action:
        return len(NEXT_TASK_ACTION_ORDER)
    try:
        return NEXT_TASK_ACTION_ORDER.index(action)
    except ValueError:
        return len(NEXT_TASK_ACTION_ORDER)


def order_collection_showcase_tasks(
    session: Session,
    chapter_key: str,
    specs: tuple[PascalShowcaseTaskSpec, ...],
) -> list[dict[str, Any]]:
    col = collection_by_key(chapter_key)
    v311_col = v311_collection_by_key(chapter_key)
    if col is None and v311_col is None:
        return []
    study_order = col.study_order_tc if col is not None else v311_col.study_order_tc  # type: ignore[union-attr]
    curriculum_version = "3.1.1" if specs and _is_v311_spec(specs[0]) else "2"
    rows = list_showcase_tasks_for_collection(
        session, chapter_key, curriculum_version=curriculum_version
    )
    tc_index = {tc_id: index for index, tc_id in enumerate(study_order)}
    spec_index = collection_spec_seed_index(specs)

    def sort_key(row: dict[str, Any]) -> tuple[int, int, int, int, int]:
        slug = str(row.get("slug") or "")
        return showcase_row_sort_key(
            row,
            tc_index=tc_index,
            spec_index=spec_index,
            action_sort_key=_action_sort_key,
        )

    return sorted(rows, key=sort_key)


def _progress_map_for_tasks(
    session: Session,
    user_id: int | None,
    task_ids: list[int],
    *,
    yaml_chapter_id: str,
) -> dict[int, str]:
    if user_id is None or not task_ids:
        return {}
    progress = StudentCurriculumProgressService(session).get_progress_for_learning_concept(
        user_id,
        LANGUAGE,
        yaml_chapter_id,
        task_ids=task_ids,
    )
    return {
        int(tid): item["progress_status"]
        for tid, item in progress["by_task_id"].items()
    }


def build_pascal_showcase_collection_next(
    session: Session,
    chapter_key: str,
    user_id: int | None,
) -> dict[str, Any]:
    col = collection_by_key(chapter_key)
    if col is None:
        raise ValueError(f"Unknown showcase chapter: {chapter_key}")

    specs = all_pascal_showcase_specs().get(chapter_key, ())
    ordered = order_collection_showcase_tasks(session, chapter_key, specs)
    task_ids = [int(row["task_id"]) for row in ordered]
    progress_by_task = _progress_map_for_tasks(
        session,
        user_id,
        task_ids,
        yaml_chapter_id=col.yaml_chapter_id,
    )
    progress = _progress_summary(len(task_ids), progress_by_task, task_ids)
    prefix = effective_title_prefix(chapter_key)
    next_task, completed = resolve_next_in_ordered_tasks(
        ordered,
        progress_by_task,
        title_prefix=prefix,
    )

    return {
        "collection_id": col.collection_id,
        "collection_key": chapter_key,
        "language": LANGUAGE,
        "learning_concept_id": col.yaml_chapter_id,
        "title_ru": col.title_ru,
        "next_task": next_task,
        "completed": completed,
        "button_label": _collection_button_label(
            passed_tasks=progress["passed_tasks"],
            total_tasks=progress["total_tasks"],
            completed=completed,
        ),
        "progress": progress,
    }


def build_pascal_v311_showcase_collection_next(
    session: Session,
    chapter_key: str,
    user_id: int | None,
) -> dict[str, Any]:
    col = v311_collection_by_key(chapter_key)
    if col is None:
        raise ValueError(f"Unknown v3.1.1 showcase chapter: {chapter_key}")

    specs = all_pascal_v311_showcase_specs().get(chapter_key, ())
    ordered = order_collection_showcase_tasks(session, chapter_key, specs)
    task_ids = [int(row["task_id"]) for row in ordered]
    progress_by_task = _progress_map_for_tasks(
        session,
        user_id,
        task_ids,
        yaml_chapter_id=col.yaml_chapter_id,
    )
    progress = _progress_summary(len(task_ids), progress_by_task, task_ids)
    prefix = v311_title_prefix(chapter_key)
    next_task, completed = resolve_next_in_ordered_tasks(
        ordered,
        progress_by_task,
        title_prefix=prefix,
    )

    return {
        "collection_id": col.collection_id,
        "collection_key": chapter_key,
        "language": LANGUAGE,
        "learning_concept_id": col.yaml_chapter_id,
        "title_ru": col.title_ru,
        "curriculum_version": "3.1.1",
        "next_task": next_task,
        "completed": completed,
        "button_label": _collection_button_label(
            passed_tasks=progress["passed_tasks"],
            total_tasks=progress["total_tasks"],
            completed=completed,
        ),
        "progress": progress,
    }


def build_pascal_conditions_showcase_next(session: Session, user_id: int | None) -> dict[str, Any]:
    return build_pascal_showcase_collection_next(session, "conditions", user_id)


def build_pascal_loops_showcase_next(session: Session, user_id: int | None) -> dict[str, Any]:
    return build_pascal_showcase_collection_next(session, "loops", user_id)

