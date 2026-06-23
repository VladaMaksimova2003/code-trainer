"""Read/update translation tasks for teacher authoring."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.tasks.services.task_patterns import apply_patterns_and_tests
from application.tasks.services.task_editor_type_migration import ensure_task_supports_assignment_type
from application.users.services.teacher_activity_service import record_teacher_activity
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask as TranslationTaskModel
from shared.enums import AssignmentType
from shared.language import parse_language


def _is_translation_task_type(task_type: str) -> bool:
    try:
        return AssignmentType.parse(task_type).is_translation()
    except ValueError:
        return task_type in {"translation", "translation_task"}


def _assignment_type_value(task_type: str) -> str:
    try:
        return AssignmentType.parse(task_type).value
    except ValueError:
        return task_type


_RESERVED_CODE_EXAMPLE_KEYS = frozenset(
    {"patterns", "expected_concepts", "curriculum_showcase", "teacher_assembly_override"}
)


def _coerce_code_text(code: str | None) -> str:
    return str(code or "")


def _has_code_text(code: str | None) -> bool:
    return bool(_coerce_code_text(code).strip())


def _language_codes_from_examples(examples: dict[str, Any]) -> dict[str, str]:
    codes: dict[str, str] = {}
    for key, value in dict(examples or {}).items():
        if key in _RESERVED_CODE_EXAMPLE_KEYS:
            continue
        text = _coerce_code_text(value if isinstance(value, str) else None)
        if _has_code_text(text):
            codes[str(key).lower()] = text
    return codes


def _apply_source_code(
    task_row: TaskModel,
    *,
    source_language: str,
    source_code: str | None,
    language_codes: dict[str, str] | None = None,
) -> None:
    from application.curriculum.display.chapter_task_display_order import merge_showcase_preserving_order

    examples = dict(task_row.code_examples or {})
    patterns = examples.get("patterns")
    expected = examples.get("expected_concepts")
    previous_showcase = examples.get("curriculum_showcase")
    showcase = (
        merge_showcase_preserving_order(previous_showcase, dict(previous_showcase))
        if isinstance(previous_showcase, dict)
        else previous_showcase
    )
    override = examples.get("teacher_assembly_override")

    merged = _language_codes_from_examples(examples)
    if language_codes:
        for lang, code in language_codes.items():
            lang_key = parse_language(str(lang))
            text = _coerce_code_text(code)
            if _has_code_text(text):
                merged[lang_key] = text
            elif lang_key in merged:
                del merged[lang_key]

    lang = parse_language(source_language)
    code = _coerce_code_text(source_code)
    if _has_code_text(code):
        merged[lang] = code
    elif lang in merged and not language_codes:
        del merged[lang]

    examples = {key: merged[key] for key in sorted(merged)}
    if patterns:
        examples["patterns"] = patterns
    if expected:
        examples["expected_concepts"] = expected
    if showcase:
        examples["curriculum_showcase"] = showcase
    if override:
        examples["teacher_assembly_override"] = override
    task_row.code_examples = examples


def get_translation_authoring_payload(db: Session, task_id: int) -> dict[str, Any] | None:
    task_row = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.is_delete == False)
        .first()
    )
    if not task_row or not _is_translation_task_type(task_row.task_type):
        return None

    relation = task_row.translation_task
    examples = dict(task_row.code_examples or {})
    source_language = ""
    source_code = ""
    if relation is not None:
        source_language = str(relation.source_language or "").strip().lower()
        source_code = _coerce_code_text(relation.source_code)
    if not source_language:
        for key, value in examples.items():
            if key in {"patterns", "expected_concepts", "curriculum_showcase"}:
                continue
            text = _coerce_code_text(value if isinstance(value, str) else None)
            if _has_code_text(text):
                source_language = str(key).lower()
                source_code = text
                break
    if not _has_code_text(source_code) and source_language:
        source_code = _coerce_code_text(examples.get(source_language))

    from application.tasks.services.authoring_expected_concepts import (
        resolve_authoring_expected_concepts_by_language,
    )

    assignment_type = _assignment_type_value(task_row.task_type)
    language_codes = _language_codes_from_examples(examples)
    return {
        "id": task_row.id,
        "task_id": task_row.id,
        "title": task_row.title,
        "description": task_row.description,
        "difficulty": task_row.difficulty,
        "type": assignment_type,
        "task_type": assignment_type,
        "source_language": source_language or "python",
        "source_code": source_code,
        "language": source_language or "python",
        "language_codes": language_codes,
        "test_cases": task_row.test_cases or [],
        "patterns": examples.get("patterns") or [],
        "patterns_by_language": resolve_authoring_expected_concepts_by_language(examples),
    }


def update_translation_task(
    db: Session,
    task_id: int,
    *,
    title: str,
    description: str,
    difficulty: str,
    source_code: str,
    source_language: str = "python",
    language_codes: dict[str, str] | None = None,
    test_cases: list[dict[str, Any]] | None = None,
    patterns: list[str] | None = None,
    patterns_by_language: dict[str, list[str]] | None = None,
    task_type: str | None = None,
    is_debug_task: bool | None = None,
    teacher_id: int | None = None,
) -> dict[str, Any] | None:
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
            language=source_language,
            source_code=source_code,
        )
        db.refresh(task_row)

    if not _is_translation_task_type(task_row.task_type):
        return None

    lang = parse_language(source_language)
    code = _coerce_code_text(source_code)

    task_row.title = title
    task_row.description = description
    task_row.difficulty = difficulty
    _apply_source_code(
        task_row,
        source_language=lang,
        source_code=code,
        language_codes=language_codes,
    )

    relation = task_row.translation_task
    if relation is None:
        relation = TranslationTaskModel(
            task_id=task_id,
            source_code=code,
            source_language=lang,
        )
        db.add(relation)
    else:
        relation.source_code = code
        relation.source_language = lang

    apply_patterns_and_tests(
        task_row,
        patterns=patterns,
        patterns_by_language=patterns_by_language,
        test_cases=test_cases,
    )

    from application.tasks.services.teacher_editor_activity_sync import (
        sync_teacher_editor_activity_metadata,
    )

    sync_teacher_editor_activity_metadata(
        task_row,
        task_type=task_row.task_type,
        is_debug_task=is_debug_task,
    )

    from application.tasks.services.teacher_assembly_preservation import mark_teacher_assembly_override

    mark_teacher_assembly_override(task_row)

    from application.curriculum.display.chapter_task_display_order import (
        sync_showcase_order_fields_across_mirror_group,
    )

    sync_showcase_order_fields_across_mirror_group(db, task_row)

    from application.tasks.services.task_version_service import record_task_version_after_edit

    db.flush()
    record_task_version_after_edit(db, task_id)
    db.commit()
    db.refresh(task_row)

    if teacher_id:
        record_teacher_activity(db, teacher_id, "edited_task")

    return get_translation_authoring_payload(db, task_id)
