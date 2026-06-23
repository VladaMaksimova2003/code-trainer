"""Resolve expected concept ids for teacher authoring views (display TC catalog)."""

from __future__ import annotations

from typing import Any

from application.curriculum.validation.expected_concept_checker import (
    normalize_expected_display_tc_ids,
)
from application.curriculum.validation.technical_concept_registry import (
    build_display_tc_ui_card,
    list_display_tc_cards,
)

_AUTHORING_LANGS = ("pascal", "python", "cpp", "csharp", "java")


def _dedupe_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _validate_tc_ids(raw: list[Any]) -> list[str]:
    """Normalize legacy / technical ids to display TC card ids."""
    return normalize_expected_display_tc_ids(
        [str(item).strip() for item in raw if str(item).strip()]
    )


def _merge_validated_by_language(
    merged: dict[str, list[str]],
    source: dict[str, Any] | None,
    *,
    overwrite: bool,
) -> None:
    if not isinstance(source, dict):
        return
    for lang, ids in source.items():
        if not isinstance(ids, list):
            continue
        validated = _validate_tc_ids(ids)
        if not validated:
            continue
        lang_key = str(lang).lower()
        if overwrite or lang_key not in merged:
            merged[lang_key] = validated


def resolve_authoring_expected_concepts_by_language(
    code_examples: dict[str, Any] | None,
) -> dict[str, list[str]]:
    """Per-language display TC ids stored on the task."""
    examples = dict(code_examples or {})
    showcase = examples.get("curriculum_showcase")
    teacher_override = bool(examples.get("teacher_assembly_override"))
    merged: dict[str, list[str]] = {}

    if teacher_override:
        raw_by_lang = examples.get("expected_concepts")
        if isinstance(raw_by_lang, dict):
            _merge_validated_by_language(merged, raw_by_lang, overwrite=True)
        if merged:
            return merged
        raw_patterns = examples.get("patterns")
        if isinstance(raw_patterns, list) and raw_patterns:
            validated = _validate_tc_ids(raw_patterns)
            if validated:
                primary = "pascal"
                if isinstance(showcase, dict):
                    primary = str(
                        showcase.get("target_language")
                        or examples.get("primary_language")
                        or primary
                    ).lower()
                if primary not in _AUTHORING_LANGS:
                    primary = "pascal"
                return {primary: validated}
        return {}

    if isinstance(showcase, dict) and not teacher_override:
        tracks = showcase.get("language_tracks")
        if isinstance(tracks, dict):
            for lang, track in tracks.items():
                if not isinstance(track, dict):
                    continue
                ids = track.get("expected_concept_ids")
                if isinstance(ids, list):
                    _merge_validated_by_language(
                        merged,
                        {str(lang).lower(): ids},
                        overwrite=True,
                    )

    if isinstance(showcase, dict):
        showcase_expected = showcase.get("expected_concepts")
        if isinstance(showcase_expected, dict):
            _merge_validated_by_language(merged, showcase_expected, overwrite=True)

    raw_by_lang = examples.get("expected_concepts")
    if isinstance(raw_by_lang, dict):
        _merge_validated_by_language(merged, raw_by_lang, overwrite=True)

    if merged:
        return merged

    examples = dict(code_examples or {})
    showcase = examples.get("curriculum_showcase")
    if isinstance(showcase, dict):
        explicit = showcase.get("expected_concept_ids")
        if isinstance(explicit, list) and explicit:
            validated = _validate_tc_ids(explicit)
            if validated:
                primary = str(
                    showcase.get("target_language")
                    or examples.get("primary_language")
                    or "pascal"
                ).lower()
                if primary not in _AUTHORING_LANGS:
                    primary = "pascal"
                return {primary: validated}

    return {}


def resolve_authoring_expected_concept_ids(code_examples: dict[str, Any] | None) -> list[str]:
    """Flat list for backward compatibility (primary language or union)."""
    by_lang = resolve_authoring_expected_concepts_by_language(code_examples)
    if by_lang:
        examples = dict(code_examples or {})
        showcase = examples.get("curriculum_showcase")
        primary = "pascal"
        if isinstance(showcase, dict):
            primary = str(showcase.get("target_language") or primary).lower()
        if primary in by_lang:
            return by_lang[primary]
        first = next(iter(by_lang.values()), [])
        return list(first)

    examples = dict(code_examples or {})
    showcase = examples.get("curriculum_showcase")
    if isinstance(showcase, dict):
        explicit = showcase.get("expected_concept_ids")
        if isinstance(explicit, list) and explicit:
            validated = _validate_tc_ids(explicit)
            if validated:
                return validated

    raw_patterns = examples.get("patterns")
    if isinstance(raw_patterns, list) and raw_patterns:
        tc_ids = _validate_tc_ids(raw_patterns)
        if tc_ids:
            return tc_ids
        from application.analysis.educational_vocabulary import normalize_construction_tags

        return normalize_construction_tags([str(item) for item in raw_patterns])

    return []


def build_tc_catalog_card(concept_id: str) -> dict[str, Any] | None:
    """Student-style concept card from tc_display_registry (+ admin overrides)."""
    normalized = normalize_expected_display_tc_ids([concept_id])
    if not normalized:
        return None
    card = build_display_tc_ui_card(normalized[0])
    return dict(card) if card else None


def list_tc_catalog_entries() -> list[tuple[str, dict[str, Any]]]:
    """Display TC cards in registry order."""
    cards = list_display_tc_cards()
    entries: list[tuple[str, dict[str, Any]]] = []
    for display_id in cards:
        card = build_display_tc_ui_card(display_id)
        if card:
            entries.append((display_id, dict(card)))
    return entries
