"""Next-task selection for C# showcase collections."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.curriculum.display.chapter_task_display_order import (
    effective_display_order,
    showcase_row_sort_key,
)
from application.curriculum.collections.curriculum_next_service import (
    NEXT_TASK_ACTION_ORDER,
    _collection_button_label,
    _progress_summary,
    _task_payload,
    resolve_next_in_ordered_tasks,
)
from application.curriculum.csharp.showcase.csharp_showcase_core import list_csharp_tasks_for_collection
from application.curriculum.csharp.showcase.csharp_v311_registry import v311_collection_by_key, v311_showcase_group
from application.curriculum.csharp.showcase.csharp_v311_showcase_all_specs import all_csharp_v311_showcase_specs
from application.curriculum.mirror.pedagogical_task_store import (
    learning_language_title,
    resolved_showcase,
)
from application.curriculum.progress.student_curriculum_progress_service import StudentCurriculumProgressService
from infrastructure.db.models.task.task import Task as TaskModel

LANGUAGE = "csharp"


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
    specs: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    col = v311_collection_by_key(chapter_key)
    if col is None:
        return []
    spec_index = {str(s["slug"]): idx for idx, s in enumerate(specs)}
    tc_index = {tc_id: index for index, tc_id in enumerate(col.study_order_tc)}
    rows = list_csharp_tasks_for_collection(session, chapter_key)

    def sort_key(row: dict[str, Any]) -> tuple[int, int, int, int, int]:
        return showcase_row_sort_key(
            row,
            tc_index=tc_index,
            spec_index=spec_index,
            action_sort_key=_action_sort_key,
        )

    return sorted(rows, key=sort_key)


def _row_from_task(task: TaskModel) -> dict[str, Any]:
    raw = dict((task.code_examples or {}).get("curriculum_showcase") or {})
    showcase = resolved_showcase(raw, LANGUAGE)
    return {
        "task_id": task.id,
        "slug": showcase.get("slug") or showcase.get("slot_id"),
        "title": learning_language_title(raw, LANGUAGE, fallback=task.title),
        "task_type": task.task_type,
        "technical_concept_id": showcase.get("technical_concept_id"),
        "action": showcase.get("primary_action"),
        "display_order": effective_display_order(showcase),
    }


def build_csharp_v311_showcase_collection_next(
    session: Session,
    chapter_key: str,
    user_id: int | None,
) -> dict[str, Any]:
    col = v311_collection_by_key(chapter_key)
    if col is None:
        raise ValueError(f"Unknown C# showcase chapter: {chapter_key}")

    specs = all_csharp_v311_showcase_specs().get(chapter_key, ())
    ordered = order_collection_showcase_tasks(session, chapter_key, specs)
    task_ids = [int(row["task_id"]) for row in ordered]
    ordered_rows: list[dict[str, Any]] = []
    for row in ordered:
        task = session.get(TaskModel, int(row["task_id"]))
        if task is None:
            continue
        ordered_rows.append(_row_from_task(task))
    progress_by_task: dict[int, str] = {}
    if user_id is not None and task_ids:
        progress = StudentCurriculumProgressService(session).get_progress_for_learning_concept(
            user_id,
            LANGUAGE,
            col.yaml_chapter_id,
            task_ids=task_ids,
        )
        progress_by_task = {
            int(tid): item["progress_status"] for tid, item in progress["by_task_id"].items()
        }
    progress = _progress_summary(len(task_ids), progress_by_task, task_ids)
    prefix = col.title_prefix
    enriched = [
        _task_payload(row, progress_by_task.get(int(row["task_id"]), "not_started"), title_prefix=prefix)
        for row in ordered_rows
    ]
    next_task, completed = resolve_next_in_ordered_tasks(
        enriched,
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
