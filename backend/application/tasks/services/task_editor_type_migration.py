"""Ensure a task row has the relations required for teacher editor assignment type."""

from __future__ import annotations

from sqlalchemy.orm import Session

from application.tasks.services.block_reorder_helpers import build_shuffled_blocks
from application.tasks.services.flowchart_diagram_storage import (
    empty_diagram,
    extract_diagram_from_flow_spec,
    merge_diagram_into_flow_spec,
)
from infrastructure.db.models.task import (
    BlockReorderTask as BlockReorderTaskModel,
    Task as TaskModel,
    TranslationTask as TranslationTaskModel,
)
from shared.enums import AssignmentType
from shared.language import parse_language

_RESERVED_CODE_KEYS = frozenset(
    {
        "patterns",
        "expected_concepts",
        "curriculum_showcase",
        "teacher_assembly_override",
        "mcq_options",
    }
)


def _extract_primary_code(task_row: TaskModel) -> tuple[str, str]:
    relation = task_row.translation_task
    if relation is not None:
        code = str(relation.source_code or "").strip()
        if code:
            lang = str(relation.source_language or "python").strip().lower() or "python"
            return lang, code

    block = task_row.block_reorder_task
    if block is not None:
        code = str(block.original_code or "").strip()
        if code:
            lang = str(block.language or "python").strip().lower() or "python"
            return lang, code

    examples = dict(task_row.code_examples or {})
    for key, value in examples.items():
        if key in _RESERVED_CODE_KEYS:
            continue
        text = str(value or "").strip()
        if text:
            return str(key).lower(), text
    return "python", ""


def ensure_task_supports_assignment_type(
    db: Session,
    task_row: TaskModel,
    raw_task_type: str,
    *,
    language: str | None = None,
    source_code: str | None = None,
) -> str:
    parsed = AssignmentType.parse(raw_task_type)
    target = parsed.value
    if str(task_row.task_type or "") == target:
        return target

    lang = parse_language(language or "")
    code = str(source_code or "").strip()
    if not code:
        default_lang, default_code = _extract_primary_code(task_row)
        lang = lang or default_lang
        code = default_code

    task_row.task_type = target

    if parsed.is_translation():
        relation = task_row.translation_task
        if relation is None:
            relation = TranslationTaskModel(
                task_id=task_row.id,
                source_code=code,
                source_language=lang or "python",
            )
            db.add(relation)
        else:
            if code:
                relation.source_code = code
            if lang:
                relation.source_language = lang
    elif parsed == AssignmentType.TASK_BUILD_FROM_BLOCKS:
        relation = task_row.block_reorder_task
        if relation is None:
            blocks, order = build_shuffled_blocks(code or "pass\n")
            relation = BlockReorderTaskModel(
                task_id=task_row.id,
                original_code=code or "pass",
                template=None,
                blocks=blocks,
                correct_order=order,
                language=lang or "python",
            )
            db.add(relation)
        elif code and not str(relation.original_code or "").strip():
            relation.original_code = code
            if lang:
                relation.language = lang
    elif parsed == AssignmentType.TASK_FLOWCHART_TO_CODE:
        spec = dict(task_row.flow_spec or {})
        if not extract_diagram_from_flow_spec(spec).get("nodes"):
            task_row.flow_spec = merge_diagram_into_flow_spec(spec, empty_diagram())
        if code:
            examples = dict(task_row.code_examples or {})
            showcase = examples.get("curriculum_showcase")
            patterns = examples.get("patterns")
            expected = examples.get("expected_concepts")
            override = examples.get("teacher_assembly_override")
            examples = {str(lang or "python").lower(): code}
            if patterns:
                examples["patterns"] = patterns
            if expected:
                examples["expected_concepts"] = expected
            if showcase:
                examples["curriculum_showcase"] = showcase
            if override:
                examples["teacher_assembly_override"] = override
            task_row.code_examples = examples

    db.flush()
    return target
