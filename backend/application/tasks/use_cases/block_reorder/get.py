"""Use cases: read block-reorder tasks (public & authoring views)."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.tasks.services.block_reorder_helpers import (
    _decode_newlines,
    build_canonical_code,
    build_entity_from_db,
    is_build_from_blocks_task_type,
    parse_difficulty,
)
from application.tasks.services.authoring_expected_concepts import (
    resolve_authoring_expected_concept_ids,
    resolve_authoring_expected_concepts_by_language,
)


def _variant_reference_code(variant: dict) -> str:
    if not isinstance(variant, dict):
        return ""
    for key in ("original_code", "reference_code", "code"):
        raw = variant.get(key)
        if raw:
            return _decode_newlines(raw).strip()
    return ""


def _reference_code_for_language(
    entity,
    relation,
    language: str,
    task_examples: dict | None = None,
) -> str:
    lang = str(language or "").lower()
    primary = str(relation.language or "python").lower()
    examples = {
        str(key).lower(): _decode_newlines(value).strip()
        for key, value in dict(task_examples or {}).items()
        if _decode_newlines(value).strip()
    }
    if lang in examples:
        return examples[lang]

    if lang == primary:
        code = _decode_newlines(relation.original_code or "").strip()
        if code:
            return code
        return build_canonical_code(entity, language=lang).strip()

    variant_code = _variant_reference_code(dict(relation.language_variants or {}).get(lang) or {})
    return variant_code


def _languages_with_reference(entity, relation, task) -> set[str]:
    primary = str(relation.language or "python").lower()
    langs: set[str] = set()

    for key, value in dict(task.code_examples or {}).items():
        if _decode_newlines(value).strip():
            langs.add(str(key).lower())

    if _decode_newlines(relation.original_code or "").strip():
        langs.add(primary)
    elif build_canonical_code(entity, language=primary).strip():
        langs.add(primary)

    for lang, raw in dict(relation.language_variants or {}).items():
        if _variant_reference_code(raw if isinstance(raw, dict) else {}):
            langs.add(str(lang).lower())

    return langs


_STRUCTURED_CODE_EXAMPLE_KEYS = frozenset(
    {
        "curriculum_showcase",
        "patterns",
        "mcq_options",
        "known_language_variants",
        "teacher_assembly_override",
    }
)


def _build_code_examples(entity, relation, task) -> dict[str, Any]:
    """Public view: language code plus structured curriculum metadata."""
    examples: dict[str, Any] = {}
    for key, value in dict(task.code_examples or {}).items():
        key_lower = str(key).lower()
        if key_lower in _STRUCTURED_CODE_EXAMPLE_KEYS:
            examples[key_lower] = value
            continue
        decoded = _decode_newlines(value).strip()
        if decoded:
            examples[key_lower] = decoded
    return examples


def _format_block_reorder_template(template: str | None, language: str) -> str:
    from application.curriculum.content.v4_code_format import format_assembly_template

    decoded = _decode_newlines(template or "")
    return format_assembly_template(decoded, language)


def _public_language_variants(entity, relation) -> dict:
    variants: dict = {}
    for lang, raw in dict(relation.language_variants or {}).items():
        if not isinstance(raw, dict):
            continue
        lang_key = str(lang).lower()
        item = dict(raw)
        if item.get("template") is not None:
            item["template"] = _format_block_reorder_template(item.get("template"), lang_key)
        for code_key in ("original_code", "reference_code", "code"):
            item.pop(code_key, None)
        variants[lang_key] = item
    return variants


def _merge_teacher_language_variant(
    relation: Any,
    *,
    language: str,
    original_code: str,
    template: str | None,
    blocks: list[str] | None,
    correct_order: list[int] | None,
) -> None:
    lang = str(language or relation.language or "python").strip().lower()
    variants = dict(getattr(relation, "language_variants", None) or {})
    entry = dict(variants.get(lang) or {})
    entry["original_code"] = original_code
    if template is not None:
        entry["template"] = template
    if blocks is not None:
        entry["blocks"] = list(blocks)
    if correct_order is not None:
        entry["correct_order"] = list(correct_order)
    variants[lang] = entry
    relation.language_variants = variants


def _sync_primary_relation_variant(relation: Any, payload: dict[str, Any]) -> None:
    lang = str(relation.language or payload.get("language") or "python").lower()
    variants = dict(payload.get("language_variants") or {})
    entry = dict(variants.get(lang) or {})
    if relation.template is not None:
        entry["template"] = _format_block_reorder_template(relation.template, lang)
    if relation.blocks is not None:
        entry["blocks"] = list(relation.blocks or [])
    if relation.correct_order is not None:
        entry["correct_order"] = list(relation.correct_order or [])
    variants[lang] = entry
    payload["language_variants"] = variants
    payload["language"] = lang
    payload["template"] = _format_block_reorder_template(relation.template, lang)
    payload["blocks"] = list(relation.blocks or [])
    payload["correct_order"] = list(relation.correct_order or [])


def _relation_has_stored_assembly(relation: Any | None) -> bool:
    if relation is None:
        return False
    if str(getattr(relation, "template", None) or "").strip():
        return True
    if list(getattr(relation, "blocks", None) or []):
        return True
    for raw in dict(getattr(relation, "language_variants", None) or {}).values():
        if not isinstance(raw, dict):
            continue
        if str(raw.get("template") or "").strip() or list(raw.get("blocks") or []):
            return True
    return False


def _sync_stored_assembly_variants_to_payload(relation: Any, payload: dict[str, Any]) -> None:
    payload["language_variants"] = _public_language_variants(None, relation)
    lang = str(relation.language or payload.get("language") or "python").lower()
    variants = dict(payload.get("language_variants") or {})
    entry = dict(variants.get(lang) or {})
    if relation.template is not None:
        entry["template"] = _format_block_reorder_template(relation.template, lang)
    if relation.blocks is not None:
        entry["blocks"] = list(relation.blocks or [])
    if relation.correct_order is not None:
        entry["correct_order"] = list(relation.correct_order or [])
    variants[lang] = entry
    payload["language_variants"] = variants


def _refresh_curriculum_assembly_variants(task: TaskModel, payload: dict[str, Any]) -> None:
    from application.tasks.services.teacher_assembly_preservation import (
        should_preserve_teacher_assembly,
    )

    relation = getattr(task, "block_reorder_task", None)
    if relation is not None:
        _sync_stored_assembly_variants_to_payload(relation, payload)

    if should_preserve_teacher_assembly(task, relation):
        return

    examples = dict(task.code_examples or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    task_format = str(showcase.get("task_format") or "").strip()
    slot_pattern_id = str(showcase.get("slot_pattern_id") or "").strip() or None
    if not slot_id or not task_format:
        return
    if str(showcase.get("primary_action") or "").strip().lower() != "assemble":
        return

    from application.curriculum.content.ch1_fragment_assembly import CH1_FRAGMENT_ASSEMBLY
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_multilingual_assembly,
        resolve_slot_pattern_key,
    )

    pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
    force_refresh = (
        task_format == "сборка_фрагмента"
        and pattern in CH1_FRAGMENT_ASSEMBLY
    )
    if not force_refresh and _relation_has_stored_assembly(relation):
        return

    refreshed = algo_multilingual_assembly(
        slot_id,
        task_format=task_format,
        slot_pattern_id=slot_pattern_id,
    )
    if not refreshed:
        return
    public: dict[str, Any] = {}
    for lang, variant in refreshed.items():
        lang_key = str(lang).lower()
        item = dict(variant)
        if item.get("template") is not None:
            item["template"] = _format_block_reorder_template(item.get("template"), lang_key)
        for code_key in ("original_code", "reference_code", "code"):
            item.pop(code_key, None)
        public[lang_key] = item
    payload["language_variants"] = public


from application.tasks.services.flowchart_diagram_storage import extract_diagram_from_flow_spec
from infrastructure.db.models.task import Task as TaskModel


def get_block_reorder_public_task(db: Session, task_id: int) -> dict[str, Any] | None:
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.is_delete == False)
        .first()
    )
    if not task or not is_build_from_blocks_task_type(task.task_type):
        return None
    relation = task.block_reorder_task
    if not relation:
        return None
    from application.tasks.services.catalog.task_query import (
        _pick_construction_hints,
        _resolve_task_constructions,
    )
    from shared.enums import AssignmentType

    entity = build_entity_from_db(task, relation)
    payload = entity.to_public_payload()
    payload["id"] = task.id
    payload["title"] = task.title
    payload["description"] = task.description
    payload["difficulty"] = task.difficulty
    assignment_type = str(task.task_type or "")
    try:
        assignment_type = AssignmentType.parse(task.task_type).value
    except ValueError:
        pass
    payload["type"] = assignment_type
    payload["task_type"] = assignment_type
    payload["test_cases"] = task.test_cases or []
    payload["language"] = str(relation.language or "python").lower()
    payload["blocks"] = list(relation.blocks or [])
    payload["correct_order"] = list(relation.correct_order or [])
    examples = _build_code_examples(entity, relation, task)
    payload["code_examples"] = examples
    constructions = _resolve_task_constructions(task.code_examples, [])
    payload["constructions"] = constructions
    payload["required_structures"] = constructions
    payload["construction_hints"] = _pick_construction_hints(constructions, {})
    payload["language_variants"] = _public_language_variants(entity, relation)
    from application.tasks.services.teacher_assembly_preservation import (
        has_teacher_assembly_override,
    )

    if has_teacher_assembly_override(task.code_examples):
        payload["teacher_assembly_override"] = True
    _refresh_curriculum_assembly_variants(task, payload)
    stored = extract_diagram_from_flow_spec(task.flow_spec)
    if stored.get("nodes"):
        payload["diagram"] = stored
    return payload


def get_block_reorder_authoring_payload(db: Session, task_id: int) -> dict[str, Any] | None:
    """Teacher/admin authoring snapshot (includes reference code)."""
    task_row = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.is_delete == False
    ).first()
    if not task_row or not is_build_from_blocks_task_type(task_row.task_type):
        return None
    relation = task_row.block_reorder_task
    if not relation:
        return None
    entity = build_entity_from_db(task_row, relation)
    payload = entity.to_public_payload()
    payload["title"] = task_row.title
    payload["description"] = task_row.description
    payload["original_code"] = relation.original_code
    payload["correct_order"] = relation.correct_order
    payload["blocks"] = list(relation.blocks or [])
    payload["template"] = relation.template
    payload["language_variants"] = dict(relation.language_variants or entity.language_variants or {})
    difficulty = parse_difficulty(task_row.difficulty)
    payload["difficulty"] = str(difficulty.value)
    payload["type"] = "code_assembly"
    payload["task_type"] = "code_assembly"
    payload["test_cases"] = task_row.test_cases or []
    payload["patterns"] = resolve_authoring_expected_concept_ids(task_row.code_examples)
    payload["patterns_by_language"] = resolve_authoring_expected_concepts_by_language(
        task_row.code_examples,
    )
    return payload
