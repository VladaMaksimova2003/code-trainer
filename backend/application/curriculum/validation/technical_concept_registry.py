"""Load AST-based curriculum detection maps (YAML)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from application.curriculum.validation.canonical_technical_ids import canonical_technical_id

_CURRICULUM_DIR = Path(__file__).resolve().parents[3] / "resources" / "curriculum"
_AST_MAP_PATH = _CURRICULUM_DIR / "ast_node_to_technical.yml"
_TC_MAP_PATH = _CURRICULUM_DIR / "technical_to_tc_map.yml"
_DISPLAY_REGISTRY_PATH = _CURRICULUM_DIR / "tc_display_registry.json"


def _load_ast_yaml() -> dict[str, Any]:
    try:
        with _AST_MAP_PATH.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except OSError:
        return {}


@lru_cache(maxsize=1)
def load_ast_node_to_technical() -> dict[str, dict[str, str]]:
    raw = _load_ast_yaml()
    nodes = raw.get("nodes") or {}
    return {
        str(lang): {str(node): str(concept) for node, concept in (mapping or {}).items()}
        for lang, mapping in nodes.items()
    }


@lru_cache(maxsize=1)
def load_ast_signal_to_technical() -> dict[str, dict[str, str]]:
    raw = _load_ast_yaml()
    signals = raw.get("signal_nodes") or {}
    return {
        str(lang): {str(node): str(concept) for node, concept in (mapping or {}).items()}
        for lang, mapping in signals.items()
    }


@lru_cache(maxsize=1)
def load_pascal_token_to_technical() -> dict[str, str]:
    raw = _load_ast_yaml()
    tokens = raw.get("pascal_tokens") or {}
    return {str(token): str(concept) for token, concept in tokens.items()}


@lru_cache(maxsize=1)
def load_technical_to_tc_map() -> dict[str, str]:
    try:
        with _TC_MAP_PATH.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
    except OSError:
        return {}
    mappings = raw.get("mappings") or {}
    return {str(key): str(value) for key, value in mappings.items()}


@lru_cache(maxsize=1)
def load_tc_display_registry() -> dict[str, Any]:
    try:
        with _DISPLAY_REGISTRY_PATH.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def list_technical_concept_ids() -> list[str]:
    ids: set[str] = set(load_technical_to_tc_map().keys())
    for lang_map in load_ast_node_to_technical().values():
        ids.update(lang_map.values())
    for lang_map in load_ast_signal_to_technical().values():
        ids.update(lang_map.values())
    ids.update(load_pascal_token_to_technical().values())
    return sorted(ids)


def list_display_tc_cards() -> dict[str, dict[str, Any]]:
    registry = load_tc_display_registry()
    cards = registry.get("tc_cards") or {}
    return {str(key): dict(value) for key, value in cards.items()}


def display_tc_for_technical(concept_id: str) -> str | None:
    return load_technical_to_tc_map().get(concept_id)


def load_technical_concepts() -> dict[str, dict[str, Any]]:
    """Deprecated shim — canonical ids only, no per-id YAML rules."""
    return {concept_id: {} for concept_id in list_technical_concept_ids()}

 
def normalize_display_card(card: dict[str, Any]) -> dict[str, Any]:
    """Normalize UI registry card to canonical ids and ``illustrates`` hints."""
    normalized = dict(card)
    normalized["technical_concept_ids"] = sorted(
        {canonical_technical_id(item) for item in card.get("technical_concept_ids") or []}
    )
    hints: dict[str, list[dict[str, Any]]] = {}
    for language, rows in (card.get("hints_by_language") or {}).items():
        hint_rows: list[dict[str, Any]] = []
        for row in rows or []:
            raw_illustrates = row.get("illustrates") or row.get("covers") or []
            hint_rows.append(
                {
                    "title": row.get("title"),
                    "illustrates": [canonical_technical_id(item) for item in raw_illustrates],
                    "code": row.get("code"),
                }
            )
        hints[str(language)] = hint_rows
    normalized["hints_by_language"] = hints
    return normalized


def _example_rows_for_technical(
    card: dict[str, Any],
    canonical: str,
    *,
    language: str | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Filter registry hints to rows that illustrate a technical concept."""
    from application.curriculum.content.v4_code_format import format_reference_code

    normalized = normalize_display_card(card)
    formatted: dict[str, list[dict[str, str]]] = {}
    for lang, rows in (normalized.get("hints_by_language") or {}).items():
        lang_key = str(lang).lower()
        if language and lang_key != str(language).lower():
            continue
        examples: list[dict[str, str]] = []
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            illustrates = {
                canonical_technical_id(str(item))
                for item in (row.get("illustrates") or row.get("covers") or [])
            }
            if illustrates and canonical not in illustrates:
                continue
            code = str(row.get("code") or "").strip()
            if code:
                code = format_reference_code(code, lang_key) or code
            title = str(row.get("title") or "Пример").strip() or "Пример"
            if code:
                examples.append({"title": title, "code": code})
        if examples:
            formatted[lang_key] = examples
    return formatted


def examples_for_technical_concept(
    concept_id: str,
    *,
    language: str | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Student popover examples for one technical concept and optional language."""
    canonical = canonical_technical_id(str(concept_id or "").strip())
    if not canonical:
        return {}

    display_id = load_technical_to_tc_map().get(canonical)
    if not display_id:
        return {}

    from application.curriculum.display.tc_display_registry_service import get_merged_display_tc_raw

    card = get_merged_display_tc_raw(display_id)
    if not card:
        return {}

    filtered = _example_rows_for_technical(card, canonical, language=language)
    if filtered:
        return filtered

    all_examples = hints_to_examples_by_language(card)
    if language:
        lang_key = str(language).lower()
        rows = all_examples.get(lang_key)
        return {lang_key: rows} if rows else {}
    return all_examples


def hints_to_examples_by_language(card: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """Student popover examples from tc_display_registry hints_by_language."""
    from application.curriculum.content.v4_code_format import format_reference_code

    normalized = normalize_display_card(card)
    formatted: dict[str, list[dict[str, str]]] = {}
    for language, rows in (normalized.get("hints_by_language") or {}).items():
        lang_key = str(language).lower()
        examples: list[dict[str, str]] = []
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            code = str(row.get("code") or "").strip()
            if code:
                code = format_reference_code(code, lang_key) or code
            title = str(row.get("title") or "Пример").strip() or "Пример"
            if code:
                examples.append({"title": title, "code": code})
        if examples:
            formatted[lang_key] = examples
    return formatted


def build_display_tc_ui_card(
    display_id: str,
    *,
    technical_concept_ids: list[str] | None = None,
) -> dict[str, Any] | None:
    """Full student-facing card for a display TC (name, description, examples per language)."""
    from application.curriculum.display.tc_display_registry_service import get_merged_display_tc_raw

    card = get_merged_display_tc_raw(display_id)
    if not card:
        return None
    tech_ids = technical_concept_ids
    if not tech_ids:
        tech_ids = sorted(
            {canonical_technical_id(item) for item in card.get("technical_concept_ids") or []}
        )
    return {
        "id": display_id,
        "name_ru": str(card.get("name_ru") or display_id),
        "description_ru": str(card.get("description_ru") or ""),
        "technical_concept_ids": list(tech_ids),
        "examples_by_language": hints_to_examples_by_language(card),
    }


def lookup_technical_concept_reference(concept_id: str) -> dict[str, Any] | None:
    """Legacy technical or display TC id → reference payload for pedagogy cards."""
    key = str(concept_id or "").strip()
    if not key:
        return None

    display_id: str | None = None
    if key.startswith("tc_"):
        if key in list_display_tc_cards():
            display_id = key
    else:
        display_id = load_technical_to_tc_map().get(canonical_technical_id(key))

    if not display_id:
        return None

    from application.curriculum.display.tc_display_registry_service import get_merged_display_tc_raw

    card = get_merged_display_tc_raw(display_id)
    if not card:
        return None

    return {
        "id": key,
        "display_id": display_id,
        "name_ru": str(card.get("name_ru") or key),
        "description_ru": str(card.get("description_ru") or ""),
        "examples_by_language": hints_to_examples_by_language(card),
    }


def tc_concept_label_ru(concept_id: str, fallback: str = "") -> str:
    """Russian label for a technical or display TC id."""
    from application.curriculum.validation.technical_concept_detector import technical_concept_label

    key = str(concept_id or "").strip()
    if not key:
        return str(fallback or "").strip() or concept_id
    if key.startswith("tc_"):
        card = list_display_tc_cards().get(key) or {}
        if card.get("name_ru"):
            return str(card["name_ru"])
    label = technical_concept_label(key)
    if label and label != key:
        return label
    ref = lookup_technical_concept_reference(key)
    if ref and ref.get("name_ru"):
        return str(ref["name_ru"])
    return str(fallback or key).strip() or key
