"""Keep teacher-edited block assembly when serving curriculum tasks to students."""

from __future__ import annotations

from typing import Any


def mark_teacher_assembly_override(row: Any) -> None:
    examples = dict(getattr(row, "code_examples", None) or {})
    examples["teacher_assembly_override"] = True
    row.code_examples = examples


def has_teacher_assembly_override(code_examples: dict[str, Any] | None) -> bool:
    return bool(dict(code_examples or {}).get("teacher_assembly_override"))


def payload_has_teacher_editor_override(
    payload: dict[str, Any],
    code_examples: dict[str, Any] | None = None,
) -> bool:
    """True when a teacher saved edits that must not be replaced by catalog defaults."""
    if payload.get("teacher_assembly_override"):
        return True
    examples = code_examples if code_examples is not None else payload.get("code_examples")
    return has_teacher_assembly_override(examples if isinstance(examples, dict) else None)


def merge_teacher_expected_concepts_into_showcase(
    showcase_fields: dict[str, Any],
    code_examples: dict[str, Any] | None,
) -> None:
    """Copy teacher-authored expected concepts onto student showcase fields."""
    from application.tasks.services.authoring_expected_concepts import (
        resolve_authoring_expected_concept_ids,
        resolve_authoring_expected_concepts_by_language,
    )

    by_lang = resolve_authoring_expected_concepts_by_language(code_examples)
    if by_lang:
        showcase_fields["expected_concepts"] = dict(by_lang)
    flat = resolve_authoring_expected_concept_ids(code_examples)
    if flat:
        showcase_fields["expected_concept_ids"] = list(flat)


def _showcase_meta(code_examples: dict[str, Any] | None) -> tuple[str, str]:
    showcase = dict(code_examples or {}).get("curriculum_showcase") or {}
    if not isinstance(showcase, dict):
        showcase = {}
    slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    task_format = str(showcase.get("task_format") or "").strip()
    return slot_id, task_format


def _catalog_assembly(
    slot_id: str,
    task_format: str,
    language: str,
) -> tuple[str, list[str], list[int]]:
    from application.curriculum.content.algo_syntax_task_extra import algo_assembly_payload

    _original, template, blocks, order = algo_assembly_payload(
        slot_id,
        language,
        task_format=task_format,
    )
    return str(template or ""), list(blocks or []), list(order or [])


def _formatted_template(template: str | None, language: str) -> str:
    from application.curriculum.content.v4_code_format import format_assembly_template
    from application.tasks.services.block_reorder_helpers import _decode_newlines

    return format_assembly_template(_decode_newlines(template or ""), str(language or "python").lower()).strip()


def _variant_differs_from_catalog(
    *,
    slot_id: str,
    task_format: str,
    language: str,
    template: str | None,
    blocks: list[str] | None,
    correct_order: list[int] | None,
) -> bool:
    lang = str(language or "").strip().lower()
    if not lang:
        return False
    try:
        cat_template, cat_blocks, cat_order = _catalog_assembly(slot_id, task_format, lang)
    except Exception:
        return bool(template or blocks)

    db_template = _formatted_template(template, lang)
    cat_template_fmt = _formatted_template(cat_template, lang)
    if db_template and db_template != cat_template_fmt:
        return True
    if list(blocks or []) != list(cat_blocks or []):
        return True
    if list(correct_order or []) and list(correct_order or []) != list(cat_order or []):
        return True
    return False


def relation_assembly_differs_from_catalog(relation: Any, code_examples: dict[str, Any] | None) -> bool:
    """True when DB assembly is not the catalog default (teacher edited, even before override flag)."""
    slot_id, task_format = _showcase_meta(code_examples)
    if not slot_id or not task_format:
        return bool(getattr(relation, "template", None) or getattr(relation, "blocks", None))

    primary = str(getattr(relation, "language", None) or "python").lower()
    if _variant_differs_from_catalog(
        slot_id=slot_id,
        task_format=task_format,
        language=primary,
        template=getattr(relation, "template", None),
        blocks=list(getattr(relation, "blocks", None) or []),
        correct_order=list(getattr(relation, "correct_order", None) or []),
    ):
        return True

    for lang, raw in dict(getattr(relation, "language_variants", None) or {}).items():
        if not isinstance(raw, dict):
            continue
        if _variant_differs_from_catalog(
            slot_id=slot_id,
            task_format=task_format,
            language=str(lang),
            template=raw.get("template"),
            blocks=list(raw.get("blocks") or []),
            correct_order=list(raw.get("correct_order") or []),
        ):
            return True
    return False


def _showcase_from_examples(code_examples: dict[str, Any] | None) -> dict[str, Any]:
    raw = dict(code_examples or {}).get("curriculum_showcase")
    return dict(raw) if isinstance(raw, dict) else {}


def _is_debug_showcase(showcase: dict[str, Any]) -> bool:
    task_format = str(showcase.get("task_format") or "")
    action = str(showcase.get("primary_action") or "").lower()
    return task_format in {"исправление", "поиск_ошибки"} or action == "debug"


def _normalized_code(value: Any) -> str:
    from application.tasks.services.block_reorder_helpers import _decode_newlines

    return _decode_newlines(str(value or "")).strip()


def _debug_languages(examples: dict[str, Any], showcase: dict[str, Any]) -> list[str]:
    from application.tasks.use_cases.debug_code_keys import is_buggy_code_key

    block_starters = bool(examples.get("teacher_assembly_override"))
    langs: set[str] = set()
    for key, value in examples.items():
        key_str = str(key).lower()
        if is_buggy_code_key(key_str) and _normalized_code(value):
            langs.add(key_str.removeprefix("buggy_"))
            continue
        if key_str in {"pascal", "python", "cpp", "csharp", "java"} and _normalized_code(value):
            langs.add(key_str)
    if not block_starters:
        for key, value in showcase.items():
            key_str = str(key)
            if key_str.startswith("starter_") and _normalized_code(value):
                langs.add(key_str.removeprefix("starter_").lower())
    return sorted(langs)


def debug_content_differs_from_catalog(row: Any) -> bool:
    """True when teacher-authored debug/fixed code differs from catalog defaults."""
    examples = dict(getattr(row, "code_examples", None) or {})
    showcase = _showcase_from_examples(examples)
    if not _is_debug_showcase(showcase):
        return False

    slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    langs = _debug_languages(examples, showcase)
    if not langs:
        return False

    from application.curriculum.content.algo_syntax_task_extra import (
        algo_debug_starter,
        algo_fixed_code,
        is_algo_syntax_slot,
    )

    if not slot_id or not is_algo_syntax_slot(slot_id):
        return True

    for lang in langs:
        fixed_db = _normalized_code(examples.get(lang))
        if fixed_db:
            try:
                catalog_fixed = _normalized_code(algo_fixed_code(slot_id, lang))
            except Exception:
                return True
            if catalog_fixed and fixed_db != catalog_fixed:
                return True

        buggy_db = _normalized_code(examples.get(f"buggy_{lang}"))
        if not buggy_db and not examples.get("teacher_assembly_override"):
            buggy_db = _normalized_code(showcase.get(f"starter_{lang}"))
        if buggy_db:
            try:
                catalog_buggy = _normalized_code(algo_debug_starter(slot_id, lang))
            except Exception:
                return True
            if catalog_buggy and buggy_db != catalog_buggy:
                return True
    return False


def should_preserve_teacher_assembly(task: Any, relation: Any | None = None) -> bool:
    rel = relation or getattr(task, "block_reorder_task", None)
    examples = dict(getattr(task, "code_examples", None) or {})
    if has_teacher_assembly_override(examples):
        return True
    if debug_content_differs_from_catalog(task):
        return True
    if rel is None:
        return False
    return relation_assembly_differs_from_catalog(rel, examples)


def should_skip_catalog_seed_refresh(row: Any) -> bool:
    """Do not overwrite an existing DB task from catalog during showcase seed."""
    return should_preserve_teacher_assembly(row)


def should_skip_catalog_assembly_refresh(payload: dict[str, Any]) -> bool:
    if payload.get("teacher_assembly_override"):
        return True
    examples = payload.get("code_examples")
    if isinstance(examples, dict) and examples.get("teacher_assembly_override"):
        return True
    variants = payload.get("language_variants")
    if isinstance(variants, dict) and variants:
        return True
    if str(payload.get("template") or "").strip() or list(payload.get("blocks") or []):
        return True
    return False
