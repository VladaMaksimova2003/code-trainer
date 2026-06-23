"""Read/update flowchart (diagram) tasks for teacher authoring."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.execution.services.flow_block_constructions import DEFAULT_ALLOWED_BLOCKS
from application.tasks.services.flowchart_authoring import validate_flowchart_assignment
from application.tasks.services.flowchart_diagram_storage import (
    extract_diagram_from_flow_spec,
    merge_diagram_into_flow_spec,
)
from application.tasks.services.task_patterns import apply_patterns_and_tests
from application.tasks.services.task_editor_type_migration import ensure_task_supports_assignment_type
from application.users.services.teacher_activity_service import record_teacher_activity
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import AssignmentType


def _is_flowchart_task_type(task_type: str) -> bool:
    try:
        return AssignmentType.parse(task_type) == AssignmentType.TASK_FLOWCHART_TO_CODE
    except ValueError:
        return task_type in {"diagram", "blocks", "task_flowchart_to_code"}


def _normalize_flow_spec(raw: dict[str, Any] | None) -> dict[str, Any]:
    spec: dict[str, Any] = {"allowed_blocks": list(DEFAULT_ALLOWED_BLOCKS)}
    if isinstance(raw, dict):
        if raw.get("allowed_blocks"):
            spec["allowed_blocks"] = list(raw["allowed_blocks"])
        langs = raw.get("student_reference_languages")
        if isinstance(langs, list) and langs:
            spec["student_reference_languages"] = [str(item) for item in langs if str(item).strip()]
        seq = raw.get("required_sequence")
        if isinstance(seq, list) and seq:
            spec["required_sequence"] = [
                str(item).strip() for item in seq if str(item).strip()
            ]
        text_checks = raw.get("required_text_checks")
        if isinstance(text_checks, list) and text_checks:
            spec["required_text_checks"] = text_checks
        if "allow_extra_nodes" in raw:
            spec["allow_extra_nodes"] = bool(raw["allow_extra_nodes"])
        if raw.get("require_loop_back_edge"):
            spec["require_loop_back_edge"] = True
    return spec


def _merge_flow_spec(
    raw: dict[str, Any] | None,
    *,
    language: str,
    reference_code: str | None,
    expose_reference_code: bool,
) -> dict[str, Any]:
    spec = _normalize_flow_spec(raw)
    primary = str(language or "python").strip().lower() or "python"
    spec["primary_language"] = primary
    code = str(reference_code or "").strip()
    if expose_reference_code and code:
        spec["student_reference_languages"] = [primary]
    else:
        spec.pop("student_reference_languages", None)
    return spec


def _apply_reference_code(
    task_row: TaskModel,
    *,
    language: str,
    reference_code: str | None,
) -> None:
    examples = dict(task_row.code_examples or {})
    patterns = examples.pop("patterns", None)
    code = str(reference_code or "").strip()
    lang = str(language or "python").strip().lower() or "python"
    if code:
        examples[lang] = code
    elif lang in examples:
        del examples[lang]
    if patterns:
        examples["patterns"] = patterns
    task_row.code_examples = examples


def _diagram_from_task(task_row: TaskModel) -> dict[str, Any]:
    return extract_diagram_from_flow_spec(task_row.flow_spec)


def get_flowchart_authoring_payload(db: Session, task_id: int) -> dict[str, Any] | None:
    task_row = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.is_delete == False)
        .first()
    )
    if not task_row or not _is_flowchart_task_type(task_row.task_type):
        return None

    diagram = _diagram_from_task(task_row)
    flow_spec = _normalize_flow_spec(task_row.flow_spec)
    examples = dict(task_row.code_examples or {})
    student_langs = flow_spec.get("student_reference_languages") or []
    primary_lang = str(student_langs[0] if student_langs else "python").lower()
    reference_code = str(examples.get(primary_lang) or "").strip()
    if not reference_code:
        for key, value in examples.items():
            if key == "patterns":
                continue
            text = str(value or "").strip()
            if text:
                primary_lang = str(key).lower()
                reference_code = text
                break

    return {
        "id": task_row.id,
        "task_id": task_row.id,
        "title": task_row.title,
        "description": task_row.description,
        "difficulty": task_row.difficulty,
        "type": "task_flowchart_to_code",
        "task_type": task_row.task_type,
        "diagram": diagram,
        "flow_spec": flow_spec,
        "language": primary_lang,
        "reference_code": reference_code,
        "expose_reference_code": bool(student_langs and reference_code),
        "test_cases": task_row.test_cases or [],
        "patterns": examples.get("patterns") or [],
    }


def update_flowchart_task(
    db: Session,
    task_id: int,
    *,
    title: str,
    description: str,
    difficulty: str,
    diagram: dict[str, Any],
    flow_spec: dict[str, Any] | None = None,
    reference_code: str | None = None,
    expose_reference_code: bool = False,
    language: str = "python",
    test_cases: list[dict[str, Any]] | None = None,
    patterns: list[str] | None = None,
    task_type: str | None = None,
    teacher_id: int | None = None,
) -> dict[str, Any] | None:
    validate_flowchart_assignment(
        diagram=diagram,
        reference_code=reference_code,
        expose_reference_code=expose_reference_code,
    )

    task_row = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.is_delete == False)
        .first()
    )
    if not task_row:
        return None

    if task_type:
        ensure_task_supports_assignment_type(
            db,
            task_row,
            task_type,
            language=language,
            source_code=reference_code,
        )
        db.refresh(task_row)

    if not _is_flowchart_task_type(task_row.task_type):
        return None

    task_row.title = title
    task_row.description = description
    task_row.difficulty = difficulty
    merged_spec = _merge_flow_spec(
        flow_spec,
        language=language,
        reference_code=reference_code,
        expose_reference_code=expose_reference_code,
    )
    task_row.flow_spec = merge_diagram_into_flow_spec(merged_spec, diagram)
    _apply_reference_code(
        task_row,
        language=language,
        reference_code=reference_code,
    )

    apply_patterns_and_tests(
        task_row,
        patterns=patterns,
        test_cases=test_cases,
    )

    from application.tasks.services.teacher_assembly_preservation import mark_teacher_assembly_override

    mark_teacher_assembly_override(task_row)

    from application.tasks.services.task_version_service import record_task_version_after_edit

    db.flush()
    record_task_version_after_edit(db, task_id)
    db.commit()
    db.refresh(task_row)

    if teacher_id:
        record_teacher_activity(db, teacher_id, "edited_task")

    payload = get_flowchart_authoring_payload(db, task_id)
    return payload
