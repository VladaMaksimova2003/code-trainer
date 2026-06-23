"""Re-apply teacher-edited task fields on public/student payloads (after catalog enrich)."""

from __future__ import annotations

from typing import Any

from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from application.curriculum.mirror.pedagogical_task_store import sync_assembly_fields_for_language
from application.curriculum.validation.expected_concept_checker import (
    build_display_expected_concept_cards,
)
from application.tasks.services.authoring_expected_concepts import (
    resolve_authoring_expected_concept_ids,
    resolve_authoring_expected_concepts_by_language,
)
from application.tasks.services.block_reorder_helpers import (
    _decode_newlines,
    build_entity_from_db,
    is_build_from_blocks_task_type,
)
from application.tasks.services.teacher_assembly_preservation import (
    should_preserve_teacher_assembly,
)
from application.tasks.use_cases.block_reorder.get import (
    _format_block_reorder_template,
    _public_language_variants,
)
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import AssignmentType


def _assignment_type_value(task_type: str | None) -> str:
    try:
        return AssignmentType.parse(str(task_type or "")).value
    except ValueError:
        return str(task_type or "")


def _display_language(
    payload: dict[str, Any],
    showcase: dict[str, Any],
    learning_language: str | None,
) -> str:
    return str(
        learning_language
        or payload.get("target_language")
        or payload.get("language")
        or showcase.get("target_language")
        or "pascal",
    ).strip().lower()


def _apply_expected_concepts(
    result: dict[str, Any],
    curriculum: dict[str, Any],
    examples: dict[str, Any],
    display_lang: str,
) -> None:
    by_lang = resolve_authoring_expected_concepts_by_language(examples)
    if by_lang:
        curriculum["expected_concept_ids_by_language"] = {
            lang: list(ids) for lang, ids in by_lang.items()
        }
        curriculum["expected_concepts_by_language"] = {
            lang: build_display_expected_concept_cards(ids)
            for lang, ids in by_lang.items()
        }
        result["expected_concept_ids_by_language"] = curriculum[
            "expected_concept_ids_by_language"
        ]
        result["expected_concepts_by_language"] = curriculum["expected_concepts_by_language"]

    lang_ids = list(by_lang.get(display_lang) or [])
    if not lang_ids:
        lang_ids = resolve_authoring_expected_concept_ids(examples)
    if not lang_ids:
        return

    cards = build_display_expected_concept_cards(lang_ids)
    curriculum["expected_concept_ids"] = lang_ids
    curriculum["expected_concepts"] = cards
    result["expected_concept_ids"] = lang_ids
    result["expected_concepts"] = cards
    result["constructions"] = lang_ids
    result["required_structures"] = lang_ids


def _merge_code_examples_from_row(
    result: dict[str, Any],
    examples: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(result.get("code_examples") or {})
    for key, value in examples.items():
        key_lower = str(key).lower()
        if key_lower in {
            "curriculum_showcase",
            "patterns",
            "expected_concepts",
            "teacher_assembly_override",
        }:
            continue
        if isinstance(value, str):
            decoded = _decode_newlines(value)
            if decoded.strip():
                merged[key_lower] = decoded
        elif isinstance(value, (dict, list)):
            merged[key] = value
    merged["teacher_assembly_override"] = True
    return merged


def _apply_block_task_fields(
    row: TaskModel,
    result: dict[str, Any],
    display_lang: str,
) -> None:
    relation = row.block_reorder_task
    if relation is None:
        return

    entity = build_entity_from_db(row, relation)
    lang = str(relation.language or display_lang or "python").lower()
    result["language"] = lang
    result["target_language"] = lang
    result["blocks"] = list(relation.blocks or [])
    result["correct_order"] = list(relation.correct_order or [])
    result["template"] = _format_block_reorder_template(relation.template, lang)
    result["language_variants"] = _public_language_variants(entity, relation)

    code = _decode_newlines(relation.original_code or "").strip()
    if code:
        examples = dict(result.get("code_examples") or {})
        examples[lang] = code
        result["code_examples"] = examples

    synced = sync_assembly_fields_for_language(result, display_lang or lang)
    result.update(synced)


def _strip_assembly_surface_fields(result: dict[str, Any]) -> None:
    """Debug/implement tasks must not expose block-reorder UI fields."""
    for key in ("blocks", "template", "correct_order", "original_code", "language_variants"):
        result.pop(key, None)
    curriculum = dict(result.get("curriculum") or {})
    for key in ("blocks", "template", "correct_order", "original_code"):
        curriculum.pop(key, None)
    if curriculum:
        result["curriculum"] = curriculum


def _is_debug_showcase(showcase: dict[str, Any]) -> bool:
    task_format = str(showcase.get("task_format") or "")
    action = str(showcase.get("primary_action") or "").lower()
    return task_format in {"исправление", "поиск_ошибки"} or action == "debug"


def _sync_known_language_variants_from_examples(
    result: dict[str, Any],
    examples: dict[str, Any],
) -> None:
    """Keep «Я знаю» reference snippets aligned with teacher-edited fixed codes."""
    langs = ("pascal", "python", "cpp", "csharp", "java")
    curriculum = dict(result.get("curriculum") or {})
    variants = dict(curriculum.get("known_language_variants") or result.get("known_language_variants") or {})
    changed = False
    for lang in langs:
        code = _decode_newlines(str(examples.get(lang) or ""))
        if not code.strip():
            continue
        entry = dict(variants.get(lang) or {})
        if str(entry.get("source_code") or "") != code:
            entry["source_code"] = code
            variants[lang] = entry
            changed = True
        merged_examples = dict(result.get("code_examples") or {})
        if str(merged_examples.get(lang) or "") != code:
            merged_examples[lang] = code
            result["code_examples"] = merged_examples
    if changed:
        curriculum["known_language_variants"] = variants
        result["curriculum"] = curriculum
        result["known_language_variants"] = variants


def _apply_debug_task_fields(
    result: dict[str, Any],
    showcase: dict[str, Any],
    examples: dict[str, Any],
) -> None:
    """Apply teacher-authored debug (исправить) codes from DB — fixed + buggy, not catalog starters."""
    from application.tasks.use_cases.debug_code_keys import (
        KNOWN_DEBUG_LANGS,
        buggy_code_key,
        migrate_legacy_starter_to_buggy,
        read_teacher_buggy_code,
    )

    merged_examples = dict(result.get("code_examples") or {})
    merged_showcase = dict(merged_examples.get("curriculum_showcase") or {})
    merged_showcase.update(showcase)
    working_examples = dict(examples)
    migrate_legacy_starter_to_buggy(working_examples, merged_showcase)

    curriculum = dict(result.get("curriculum") or {})
    for lang in KNOWN_DEBUG_LANGS:
        fixed = _decode_newlines(str(working_examples.get(lang) or ""))
        if fixed.strip():
            merged_examples[lang] = fixed

        buggy = read_teacher_buggy_code(working_examples, merged_showcase, lang)
        if buggy.strip():
            key = buggy_code_key(lang)
            decoded = _decode_newlines(buggy)
            merged_examples[key] = decoded
            curriculum[key] = decoded

        merged_showcase.pop(f"starter_{lang}", None)

    merged_examples["curriculum_showcase"] = merged_showcase
    merged_examples["teacher_assembly_override"] = True
    result["code_examples"] = merged_examples
    result["curriculum"] = curriculum
    _sync_known_language_variants_from_examples(result, working_examples)


def _strip_starter_fields_from_public_payload(result: dict[str, Any]) -> None:
    """Teacher-edited tasks never expose catalog starter_* on student/teacher payloads."""
    from application.tasks.use_cases.debug_code_keys import strip_starter_fields

    strip_starter_fields(result)
    curriculum = dict(result.get("curriculum") or {})
    strip_starter_fields(curriculum)
    if curriculum:
        result["curriculum"] = curriculum

    examples = dict(result.get("code_examples") or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    strip_starter_fields(showcase)
    examples["curriculum_showcase"] = showcase
    result["code_examples"] = examples


def _apply_translation_task_fields(
    row: TaskModel,
    result: dict[str, Any],
    showcase: dict[str, Any],
    display_lang: str,
) -> None:
    relation = row.translation_task
    examples = dict(result.get("code_examples") or {})

    if relation is not None:
        lang = str(relation.source_language or display_lang or "python").lower()
        code = _decode_newlines(relation.source_code or "")
        if str(code).strip():
            examples[lang] = code
            result["source_code"] = code
            result["source_language"] = lang
            result["language"] = lang
            result["target_language"] = lang

    result["code_examples"] = examples


def apply_teacher_editor_public_payload(
    row: TaskModel,
    payload: dict[str, Any],
    *,
    learning_language: str | None = None,
) -> dict[str, Any]:
    """Replace catalog-derived fields with the teacher's saved DB snapshot."""
    if not should_preserve_teacher_assembly(row):
        return payload

    result = dict(payload)
    examples = dict(row.code_examples or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    display_lang = _display_language(result, showcase, learning_language)

    result["title"] = strip_showcase_title_prefix(str(row.title or ""))
    result["description"] = row.description
    result["difficulty"] = row.difficulty
    result["test_cases"] = list(row.test_cases or [])
    result["teacher_assembly_override"] = True

    assignment_type = _assignment_type_value(row.task_type)
    result["type"] = assignment_type
    result["task_type"] = assignment_type

    primary_action = str(showcase.get("primary_action") or "").strip().lower()
    curriculum = dict(result.get("curriculum") or {})
    if primary_action:
        result["primary_action"] = primary_action
        curriculum["action"] = primary_action
    task_format = showcase.get("task_format")
    if task_format:
        curriculum["task_format"] = str(task_format)
    elif primary_action in {"implement", "assemble"}:
        curriculum.pop("task_format", None)

    result["code_examples"] = _merge_code_examples_from_row(result, examples)
    _sync_known_language_variants_from_examples(result, examples)
    _apply_expected_concepts(result, curriculum, examples, display_lang)
    result["curriculum"] = curriculum

    try:
        parsed = AssignmentType.parse(row.task_type)
    except ValueError:
        parsed = None

    if parsed is not None and parsed.is_translation() and not _is_debug_showcase(showcase):
        _apply_translation_task_fields(row, result, showcase, display_lang)
    elif _is_debug_showcase(showcase):
        result["type"] = AssignmentType.LEGACY_ALGORITHM.value
        result["task_type"] = AssignmentType.LEGACY_ALGORITHM.value
        _apply_debug_task_fields(result, showcase, examples)
        _strip_assembly_surface_fields(result)
        _strip_starter_fields_from_public_payload(result)
        return result
    elif is_build_from_blocks_task_type(str(row.task_type or "")):
        _apply_block_task_fields(row, result, display_lang)

    _strip_starter_fields_from_public_payload(result)
    return result
