"""task_format → builder mapping for Python Course v1."""
from __future__ import annotations

from shared.enums import AssignmentType

TASK_FORMAT_TO_BUILDER: dict[str, str] = {
    "перевод_программы": "translation_to_python",
    "перевод_фрагмента": "translation_snippet_to_python",
    "исправление": "python_debug_starter",
    "поиск_ошибки": "python_debug_starter",
    "сборка_программы": "block_reorder_python",
    "сборка_фрагмента": "block_reorder_python",
    "код_по_блок-схеме": "flowchart_python",
    "блок-схема_по_коду": "flowchart_python",
    "выбор_фрагмента": "mcq_python_fragment",
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

CANONICAL_CURRICULUM_PATTERN: dict[str, str] = {
    "translate": "tr_pascal_to_python_code",
    "assemble": "asm_blocks_to_code_pascal",
    "debug": "dbg_pascal_code_fix",
    "implement": "imp_text_spec_to_pascal",
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


def resolve_assignment_for_extra(task_format: str, extra: dict | None) -> str:
    payload = extra or {}
    if payload.get("template") and payload.get("blocks") and payload.get("correct_order") is not None:
        return AssignmentType.TASK_BUILD_FROM_BLOCKS.value
    return assignment_for_task_format(task_format)


def resolve_builder_for_extra(task_format: str, extra: dict | None) -> str:
    payload = extra or {}
    if payload.get("template") and payload.get("blocks") and payload.get("correct_order") is not None:
        return TASK_FORMAT_TO_BUILDER["сборка_фрагмента"]
    return builder_for_task_format(task_format)
