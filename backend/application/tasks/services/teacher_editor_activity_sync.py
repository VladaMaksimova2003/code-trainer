"""Keep curriculum_showcase activity labels aligned with teacher editor saves."""

from __future__ import annotations

from application.tasks.use_cases.debug_codes import demote_from_debug_task, promote_to_debug_task
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import AssignmentType


def _showcase(row: TaskModel) -> dict:
    raw = (row.code_examples or {}).get("curriculum_showcase")
    return dict(raw) if isinstance(raw, dict) else {}


def _strip_debug_starters(showcase: dict) -> None:
    for key in list(showcase.keys()):
        if str(key).startswith("starter_"):
            del showcase[key]


def sync_teacher_editor_activity_metadata(
    row: TaskModel,
    *,
    task_type: str | None = None,
    is_debug_task: bool | None = None,
) -> None:
    """Update primary_action / task_format after teacher saves type or debug flag."""
    raw_type = str(task_type or row.task_type or "").strip()
    if not raw_type:
        return

    try:
        parsed = AssignmentType.parse(raw_type)
    except ValueError:
        return

    if is_debug_task is True and parsed.is_translation():
        promote_to_debug_task(row)
        return

    if is_debug_task is False:
        demote_from_debug_task(row)

    from application.curriculum.display.chapter_task_display_order import merge_showcase_preserving_order

    examples = dict(row.code_examples or {})
    showcase = merge_showcase_preserving_order(_showcase(row), dict(_showcase(row)))

    if parsed == AssignmentType.TASK_BUILD_FROM_BLOCKS:
        showcase["primary_action"] = "assemble"
        if showcase.get("task_format") in {"исправление", "поиск_ошибки"}:
            showcase.pop("task_format", None)
        _strip_debug_starters(showcase)
    elif parsed.is_translation() and is_debug_task is not True:
        showcase["primary_action"] = "implement"
        if showcase.get("task_format") in {"исправление", "поиск_ошибки"}:
            showcase.pop("task_format", None)
        _strip_debug_starters(showcase)

    if showcase:
        examples["curriculum_showcase"] = showcase
        row.code_examples = examples
