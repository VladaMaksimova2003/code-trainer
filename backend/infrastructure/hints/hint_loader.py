"""Load structure hints from resources/hints/structures.yml."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_HINTS_PATH = Path(__file__).resolve().parents[2] / "resources" / "hints" / "structures.yml"
_cache: dict[str, dict[str, dict[str, Any]]] | None = None


def hints_file_path() -> Path:
    return _HINTS_PATH


def load_structure_hints(*, force: bool = False) -> dict[str, dict[str, dict[str, Any]]]:
    global _cache
    if _cache is not None and not force:
        return _cache

    if not _HINTS_PATH.is_file():
        raise FileNotFoundError(f"Hints file not found: {_HINTS_PATH}")

    raw = yaml.safe_load(_HINTS_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("structures.yml must be a mapping at root")

    parsed: dict[str, dict[str, dict[str, Any]]] = {}
    for structure_type, subtypes in raw.items():
        if not isinstance(subtypes, dict):
            continue
        parsed[str(structure_type)] = {
            str(subtype): dict(entry)
            for subtype, entry in subtypes.items()
            if isinstance(entry, dict)
        }

    _cache = parsed
    return parsed


def reload_structure_hints() -> dict[str, dict[str, dict[str, Any]]]:
    return load_structure_hints(force=True)
