"""Load manual AST node.type tables for subtype detection."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_MAP_PATH = Path(__file__).resolve().parents[3] / "resources" / "analysis" / "subtype_node_types.yml"
_cache: dict[str, dict[str, dict[str, frozenset[str]]]] | None = None


def _normalize_entry(raw: Any) -> dict[str, frozenset[str]]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, frozenset[str]] = {}
    for structure, subtypes in raw.items():
        if not isinstance(subtypes, dict):
            continue
        out[str(structure)] = {
            str(subtype): frozenset(str(t) for t in types if t)
            for subtype, types in subtypes.items()
            if isinstance(types, list)
        }
    return out


def load_subtype_node_maps(*, force: bool = False) -> dict[str, dict[str, dict[str, frozenset[str]]]]:
    global _cache
    if _cache is not None and not force:
        return _cache

    raw = yaml.safe_load(_MAP_PATH.read_text(encoding="utf-8")) or {}
    default = _normalize_entry(raw.get("default"))
    per_lang: dict[str, dict[str, dict[str, frozenset[str]]]] = {"default": default}

    for key, value in raw.items():
        if key == "default" or not isinstance(value, dict):
            continue
        per_lang[str(key).lower()] = _merge_maps(default, _normalize_entry(value))

    _cache = per_lang
    return _cache


def _merge_maps(
    base: dict[str, dict[str, frozenset[str]]],
    override: dict[str, dict[str, frozenset[str]]],
) -> dict[str, dict[str, frozenset[str]]]:
    merged = {s: dict(sub) for s, sub in base.items()}
    for structure, subtypes in override.items():
        bucket = merged.setdefault(structure, {})
        bucket.update(subtypes)
    return merged


def maps_for_language(language_id: str) -> dict[str, dict[str, frozenset[str]]]:
    all_maps = load_subtype_node_maps()
    lang = str(language_id).lower()
    if lang in all_maps:
        return all_maps[lang]
    return all_maps.get("default", {})
