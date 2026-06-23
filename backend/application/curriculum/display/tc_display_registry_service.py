"""Admin + runtime merge for pedagogical display TC cards (tc_display_registry.json)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from application.curriculum.validation.technical_concept_registry import (
    hints_to_examples_by_language,
    list_display_tc_cards,
    normalize_display_card,
)

_SOURCE = "tc_display_registry.json"
_OVERRIDES_PATH = (
    Path(__file__).resolve().parents[2] / "resources" / "curriculum" / "tc_display_overrides.json"
)
_ALLOWED_PATCH_FIELDS = frozenset({"name_ru", "description_ru", "examples_by_language", "hints_by_language"})

_cache: dict[str, dict[str, Any]] | None = None


def _load_overrides_raw() -> dict[str, dict[str, Any]]:
    try:
        with _OVERRIDES_PATH.open(encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_overrides_raw(data: dict[str, dict[str, Any]]) -> None:
    _OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _OVERRIDES_PATH.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _invalidate_cache() -> None:
    global _cache
    _cache = None


def load_overrides() -> dict[str, dict[str, Any]]:
    global _cache
    if _cache is None:
        _cache = _load_overrides_raw()
    return _cache


def list_display_tc_ids() -> list[str]:
    return sorted(list_display_tc_cards().keys())


def has_display_override(concept_id: str) -> bool:
    return str(concept_id or "").strip() in load_overrides()


def _examples_to_hints(examples_by_language: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    hints: dict[str, list[dict[str, Any]]] = {}
    for lang, items in examples_by_language.items():
        if not isinstance(items, list):
            continue
        lang_key = str(lang).lower()
        rows: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "title": str(item.get("title") or "").strip(),
                    "code": str(item.get("code") or ""),
                    "illustrates": list(item.get("illustrates") or []),
                }
            )
        hints[lang_key] = rows
    return hints


def get_merged_display_tc_raw(concept_id: str) -> dict[str, Any] | None:
    """Display card from registry merged with admin overrides."""
    cid = str(concept_id or "").strip()
    base = list_display_tc_cards().get(cid)
    if base is None:
        return None

    merged = normalize_display_card(copy.deepcopy(base))
    override = load_overrides().get(cid) or {}

    if override.get("name_ru"):
        merged["name_ru"] = str(override["name_ru"])
    if override.get("description_ru"):
        merged["description_ru"] = str(override["description_ru"])

    hints_override = override.get("hints_by_language")
    if hints_override is None and override.get("examples_by_language"):
        hints_override = _examples_to_hints(override["examples_by_language"])
    if isinstance(hints_override, dict):
        merged_hints = dict(merged.get("hints_by_language") or {})
        for lang, items in hints_override.items():
            if isinstance(items, list):
                merged_hints[str(lang).lower()] = copy.deepcopy(items)
        merged["hints_by_language"] = merged_hints

    return merged


def list_tc_concept_summaries() -> list[dict[str, Any]]:
    """Lightweight rows for admin sidebar — metadata only."""
    overrides = load_overrides()
    items: list[dict[str, Any]] = []
    for concept_id in list_display_tc_ids():
        base = list_display_tc_cards().get(concept_id)
        if base is None:
            continue
        override = overrides.get(concept_id) or {}
        items.append(
            {
                "id": concept_id,
                "name_ru": str(override.get("name_ru") or base.get("name_ru") or concept_id),
                "description_ru": str(
                    override.get("description_ru") or base.get("description_ru") or ""
                ),
                "has_overrides": concept_id in overrides,
                "source": _SOURCE,
            }
        )
    return items


def get_merged_tc_concept(concept_id: str) -> dict[str, Any] | None:
    """Admin detail payload with examples_by_language."""
    raw = get_merged_display_tc_raw(concept_id)
    if raw is None:
        return None
    return {
        "id": concept_id,
        "name_ru": str(raw.get("name_ru") or concept_id),
        "description_ru": str(raw.get("description_ru") or ""),
        "examples_by_language": hints_to_examples_by_language(raw),
        "technical_concept_ids": list(raw.get("technical_concept_ids") or []),
    }


def update_tc_concept(concept_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    cid = str(concept_id or "").strip()
    if cid not in list_display_tc_cards():
        raise KeyError(f"Display TC '{cid}' not found")

    unknown = set(patch.keys()) - _ALLOWED_PATCH_FIELDS
    if unknown:
        raise ValueError(f"Unknown fields: {sorted(unknown)}")

    if not patch:
        merged = get_merged_tc_concept(cid)
        if merged is None:
            raise KeyError(f"Display TC '{cid}' not found")
        return merged

    overrides = copy.deepcopy(load_overrides())
    current = copy.deepcopy(overrides.get(cid, {}))

    if patch.get("name_ru") is not None:
        current["name_ru"] = str(patch["name_ru"])
    if patch.get("description_ru") is not None:
        current["description_ru"] = str(patch["description_ru"])

    examples_patch = patch.get("examples_by_language")
    if isinstance(examples_patch, dict):
        bucket = dict(current.get("examples_by_language") or {})
        for lang, items in examples_patch.items():
            lang_key = str(lang).lower()
            if items is None:
                bucket.pop(lang_key, None)
                continue
            if not isinstance(items, list):
                raise ValueError("'examples_by_language' values must be lists")
            normalized: list[dict[str, str]] = []
            for item in items:
                if not isinstance(item, dict):
                    raise ValueError("Each example must be an object with title and code")
                normalized.append(
                    {
                        "title": str(item.get("title") or "").strip(),
                        "code": str(item.get("code") or ""),
                    }
                )
            bucket[lang_key] = normalized
        current["examples_by_language"] = bucket
        current["hints_by_language"] = _examples_to_hints(bucket)

    hints_patch = patch.get("hints_by_language")
    if isinstance(hints_patch, dict):
        current["hints_by_language"] = copy.deepcopy(hints_patch)

    overrides[cid] = current
    _save_overrides_raw(overrides)
    _invalidate_cache()

    merged = get_merged_tc_concept(cid)
    if merged is None:
        raise KeyError(f"Display TC '{cid}' not found")
    return merged


def to_admin_response(concept_id: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": concept_id,
        "name_ru": str(entry.get("name_ru") or concept_id),
        "description_ru": str(entry.get("description_ru") or ""),
        "examples_by_language": entry.get("examples_by_language") or {},
        "source": _SOURCE,
        "has_overrides": has_display_override(concept_id),
    }
