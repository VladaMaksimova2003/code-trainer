"""Curriculum metadata for teacher task list (chapters, activity types)."""

from __future__ import annotations

from dataclasses import dataclass

from application.curriculum.display.chapter_task_display_order import (
    compute_pedagogical_display_order,
    effective_display_order,
    effective_chapter_rank,
)
from application.curriculum.display.curriculum_labels import ACTION_LABELS
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    PASCAL_V311_SHOWCASE_COLLECTIONS,
)
from application.tasks.services.teacher_assembly_preservation import has_teacher_assembly_override
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import AssignmentType

from application.curriculum.display.chapter_task_display_order import pedagogical_action_sort_key

_ACTION_SORT_ORDER = {
    action: pedagogical_action_sort_key(action)
    for action in ("assemble", "debug", "translate", "implement", "analyze", "recognize")
}

_CHAPTER_ORDER: dict[str, int] = {}
_CHAPTER_TITLES: dict[str, str] = {}
for _index, _col in enumerate(PASCAL_V311_SHOWCASE_COLLECTIONS):
    key = str(_col.chapter_key)
    if key not in _CHAPTER_ORDER:
        _CHAPTER_ORDER[key] = _index
        _CHAPTER_TITLES[key] = str(_col.title_ru)


@dataclass(frozen=True)
class TaskTeacherListMeta:
    chapter_key: str | None = None
    chapter_title: str | None = None
    chapter_order: int | None = None
    display_order: int | None = None
    primary_action: str | None = None
    activity_label: str | None = None
    task_format: str | None = None
    is_debug_task: bool = False
    action_sort_order: int = 99


def _primary_action_from_task_type(row: TaskModel) -> str | None:
    raw_type = str(getattr(row, "task_type", None) or "").strip()
    if not raw_type:
        return None
    try:
        parsed = AssignmentType.parse(raw_type)
    except ValueError:
        return None
    if parsed == AssignmentType.TASK_BUILD_FROM_BLOCKS:
        return "assemble"
    if parsed.is_translation():
        return "implement"
    if parsed == AssignmentType.TASK_FLOWCHART_TO_CODE:
        return "recognize"
    return None


def teacher_list_meta_for_row(
    row: TaskModel,
    *,
    chapter_titles: dict[str, str] | None = None,
) -> TaskTeacherListMeta:
    examples = dict(row.code_examples or {})
    showcase_raw = examples.get("curriculum_showcase")
    showcase = dict(showcase_raw) if isinstance(showcase_raw, dict) else {}
    teacher_override = has_teacher_assembly_override(examples)

    chapter_key = str(showcase.get("collection_key") or "").strip() or None
    task_format = str(showcase.get("task_format") or "").strip() or None
    primary_action = str(
        showcase.get("primary_action") or showcase.get("action") or ""
    ).strip().lower() or None
    showcase_action = primary_action

    if teacher_override:
        is_debug_override = (
            showcase_action == "debug"
            or task_format in {"исправление", "поиск_ошибки"}
        )
        if is_debug_override:
            primary_action = "debug"
        else:
            from_task_type = _primary_action_from_task_type(row)
            if from_task_type:
                primary_action = from_task_type
            elif showcase_action:
                primary_action = showcase_action
    elif not primary_action:
        from_task_type = _primary_action_from_task_type(row)
        if from_task_type:
            primary_action = from_task_type

    if not primary_action and task_format:
        if task_format in {"исправление", "поиск_ошибки"}:
            primary_action = "debug"
        elif task_format.startswith("перевод") or task_format.startswith("реализация"):
            primary_action = "implement"
        elif task_format.startswith("сборка"):
            primary_action = "assemble"

    activity_label = ACTION_LABELS.get(primary_action or "", "") or None
    is_debug = (
        task_format in {"исправление", "поиск_ошибки"}
        or primary_action == "debug"
    )

    chapter_title = None
    if chapter_key:
        if chapter_titles and chapter_key in chapter_titles:
            chapter_title = chapter_titles[chapter_key]
        else:
            chapter_title = _CHAPTER_TITLES.get(chapter_key)
    default_chapter_order = _CHAPTER_ORDER.get(chapter_key or "") if chapter_key else None
    chapter_order = (
        effective_chapter_rank(showcase, default=default_chapter_order)
        if chapter_key
        else None
    )
    raw_display_order = effective_display_order(showcase) if chapter_key else None
    normalized_display_order = (
        raw_display_order
        if raw_display_order is not None and raw_display_order < 999_999
        else None
    )

    return TaskTeacherListMeta(
        chapter_key=chapter_key,
        chapter_title=chapter_title,
        chapter_order=chapter_order,
        display_order=normalized_display_order,
        primary_action=primary_action,
        activity_label=activity_label,
        task_format=task_format,
        is_debug_task=is_debug,
        action_sort_order=_ACTION_SORT_ORDER.get(primary_action or "", 99),
    )
