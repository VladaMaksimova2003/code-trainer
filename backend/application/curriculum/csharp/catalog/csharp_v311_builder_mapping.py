"""task_format → builder mapping for C# Course v1."""
from __future__ import annotations

from shared.enums import AssignmentType

TASK_FORMAT_TO_BUILDER: dict[str, str] = {
    "перевод_программы": "translation_to_csharp",
    "перевод_фрагмента": "translation_snippet_to_csharp",
    "исправление": "csharp_debug_starter",
    "поиск_ошибки": "csharp_debug_starter",
    "сборка_программы": "block_reorder_csharp",
    "сборка_фрагмента": "block_reorder_csharp",
    "код_по_блок-схеме": "flowchart_csharp",
    "блок-схема_по_коду": "flowchart_csharp",
    "выбор_фрагмента": "mcq_csharp_fragment",
}

TASK_FORMAT_TO_ASSIGNMENT: dict[str, str] = {
    "перевод_программы": AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
    "перевод_фрагмента": AssignmentType.TASK_TRANSLATE_SNIPPET.value,
    "исправление": AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
    "поиск_ошибки": AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
    "сборка_программы": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
    "сборка_фрагмента": AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
    "код_по_блок-схеме": AssignmentType.TASK_FLOWCHART_TO_CODE.value,
    "блок-схема_по_коду": AssignmentType.TASK_FLOWCHART_TO_CODE.value,
    "выбор_фрагмента": AssignmentType.TASK_TRANSLATE_SNIPPET.value,
}


def builder_for_task_format(task_format: str) -> str:
    try:
        return TASK_FORMAT_TO_BUILDER[task_format]
    except KeyError as exc:
        raise KeyError(f"No builder mapping for task_format={task_format!r}") from exc


def assignment_for_task_format(task_format: str) -> str:
    try:
        return TASK_FORMAT_TO_ASSIGNMENT[task_format]
    except KeyError as exc:
        raise KeyError(f"No assignment mapping for task_format={task_format!r}") from exc
