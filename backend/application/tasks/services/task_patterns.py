"""Persist required concept ids on TaskModel.code_examples."""
from __future__ import annotations

from typing import Any


def _optional_relation_language(row: Any, relation_name: str, attr_name: str) -> str | None:
    try:
        from sqlalchemy.orm.base import instance_state

        state = instance_state(row)
        if relation_name in state.unloaded:
            return None
    except Exception:
        return None

    relation = getattr(row, relation_name, None)
    if relation is None:
        return None
    raw = getattr(relation, attr_name, None)
    text = str(raw or "").strip().lower()
    return text or None


def _primary_language_for_patterns(row: Any, examples: dict[str, Any]) -> str:
    showcase = examples.get("curriculum_showcase")
    if isinstance(showcase, dict):
        target = str(showcase.get("target_language") or "").strip().lower()
        if target:
            return target

    for relation_name, attr_name in (
        ("block_reorder_task", "language"),
        ("translation_task", "source_language"),
    ):
        lang = _optional_relation_language(row, relation_name, attr_name)
        if lang:
            return lang

    primary = str(examples.get("primary_language") or "").strip().lower()
    return primary or "pascal"


def _io_value_to_text(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (int, float, bool)):
        return str(raw)
    if isinstance(raw, dict):
        value = raw.get("value")
        if isinstance(value, list):
            if value and isinstance(value[0], list):
                return "\n".join(" ".join(str(cell) for cell in row) for row in value)
            return "\n".join(str(item) for item in value)
        if value is not None:
            return str(value)
        if raw.get("raw") is not None:
            return str(raw.get("raw"))
        text = raw.get("text")
        if text is not None:
            return str(text)
    return str(raw)


def normalize_test_cases_for_storage(
    test_cases: list[dict[str, Any]] | None,
) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, case in enumerate(test_cases or [], start=1):
        if not isinstance(case, dict):
            continue
        inputs = case.get("inputs")
        if inputs is None and case.get("input") is not None:
            inputs = _io_value_to_text(case.get("input"))
        output = case.get("output")
        if output is None and case.get("expected_output") is not None:
            output = _io_value_to_text(case.get("expected_output"))
        normalized.append(
            {
                "name": str(case.get("name") or f"Тест {index}"),
                "inputs": str(
                    _normalize_stored_inputs(
                        inputs if inputs is not None else "",
                    )
                ),
                "output": str(output if output is not None else ""),
            }
        )
    return normalized


def _normalize_stored_inputs(raw: Any, reference_code: str = "") -> str:
    text = _io_value_to_text(raw)
    if not text.strip():
        return text
    from application.curriculum.content.v4_test_cases_io import stdin_tokens_to_lines

    return stdin_tokens_to_lines(text, reference_code)


def mark_teacher_assembly_override(row: Any) -> None:
    """Teacher edited blocks/template — do not replace with curriculum catalog on read."""
    from application.tasks.services.teacher_assembly_preservation import (
        mark_teacher_assembly_override as _mark,
    )

    _mark(row)


def _normalize_patterns_by_language(
    patterns_by_language: dict[str, list[str]],
) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for lang, ids in patterns_by_language.items():
        lang_key = str(lang or "").strip().lower()
        if not lang_key:
            continue
        cleaned = [str(item).strip() for item in ids if str(item).strip()]
        if cleaned:
            normalized[lang_key] = cleaned
    return normalized


def _clear_expected_concepts(examples: dict[str, Any]) -> None:
    examples.pop("expected_concepts", None)
    examples.pop("patterns", None)
    showcase = examples.get("curriculum_showcase")
    if not isinstance(showcase, dict):
        return
    from application.curriculum.display.chapter_task_display_order import merge_showcase_preserving_order

    updated_showcase = merge_showcase_preserving_order(showcase, dict(showcase))
    updated_showcase.pop("expected_concepts", None)
    updated_showcase.pop("expected_concept_ids", None)
    tracks = dict(updated_showcase.get("language_tracks") or {})
    for lang, track in tracks.items():
        if isinstance(track, dict):
            track_copy = dict(track)
            track_copy.pop("expected_concept_ids", None)
            tracks[lang] = track_copy
    updated_showcase["language_tracks"] = tracks
    examples["curriculum_showcase"] = updated_showcase


def _apply_normalized_patterns(
    row: Any,
    examples: dict[str, Any],
    normalized: dict[str, list[str]],
) -> None:
    examples["expected_concepts"] = normalized
    showcase = examples.get("curriculum_showcase")
    primary_lang = _primary_language_for_patterns(row, examples)
    if isinstance(showcase, dict):
        target = str(showcase.get("target_language") or "").strip().lower()
        if target and target in normalized:
            primary_lang = target
    flat = normalized.get(primary_lang) or next(iter(normalized.values()))
    examples["patterns"] = list(flat)
    showcase = examples.get("curriculum_showcase")
    if isinstance(showcase, dict):
        from application.curriculum.display.chapter_task_display_order import merge_showcase_preserving_order

        updated_showcase = merge_showcase_preserving_order(showcase, dict(showcase))
        updated_showcase["expected_concepts"] = dict(normalized)
        updated_showcase["expected_concept_ids"] = list(flat)
        tracks = dict(updated_showcase.get("language_tracks") or {})
        for lang, ids in normalized.items():
            track = dict(tracks.get(lang) or {})
            track["expected_concept_ids"] = list(ids)
            tracks[lang] = track
        updated_showcase["language_tracks"] = tracks
        examples["curriculum_showcase"] = updated_showcase


def apply_patterns_and_tests(
    row: Any,
    *,
    patterns: list[str] | None,
    patterns_by_language: dict[str, list[str]] | None = None,
    test_cases: list[dict[str, Any]] | None,
) -> None:
    examples = dict(getattr(row, "code_examples", None) or {})

    normalized_by_language: dict[str, list[str]] | None = None
    if patterns_by_language is not None:
        normalized_by_language = _normalize_patterns_by_language(patterns_by_language)

    if normalized_by_language:
        _apply_normalized_patterns(row, examples, normalized_by_language)
        row.code_examples = examples
    elif patterns is not None:
        pattern_list = [str(item) for item in patterns if str(item).strip()]
        if pattern_list:
            existing_raw = examples.get("expected_concepts")
            existing_by_lang: dict[str, list[str]] = {}
            if isinstance(existing_raw, dict):
                existing_by_lang = _normalize_patterns_by_language(existing_raw)
            primary_lang = _primary_language_for_patterns(row, examples)
            existing_by_lang[primary_lang] = pattern_list
            _apply_normalized_patterns(row, examples, existing_by_lang)
        else:
            _clear_expected_concepts(examples)
        row.code_examples = examples
    elif patterns_by_language is not None:
        _clear_expected_concepts(examples)
        row.code_examples = examples

    if test_cases is not None:
        row.test_cases = normalize_test_cases_for_storage(test_cases)
