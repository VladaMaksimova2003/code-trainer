"""Map v128 catalog ``features`` tokens to technical concept ids (29 TC cards)."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


def features_for_pattern(pattern: str | None) -> str:
    """Return semicolon-separated feature tokens for a task_NNN pattern key."""
    key = str(pattern or "").strip()
    if not key:
        return ""
    try:
        from algo_v128_catalog import _TASK_INDEX
    except ImportError:
        return ""
    for item in _TASK_INDEX:
        if str(item.get("pattern_id") or "").strip() == key:
            return str(item.get("features") or "").strip()
    return ""


def technical_ids_from_catalog_features(features: str) -> list[str]:
    """Map catalog feature tokens → deduped technical ids (registry order)."""
    from application.curriculum.validation.canonical_technical_ids import canonical_technical_id
    from application.curriculum.validation.technical_concept_registry import (
        list_display_tc_cards,
        load_technical_to_tc_map,
    )

    mapping = load_technical_to_tc_map()
    cards = list_display_tc_cards()
    technical_ids: list[str] = []
    seen_tc: set[str] = set()
    for raw in str(features or "").split(";"):
        token = str(raw or "").strip()
        if not token:
            continue
        technical_id = canonical_technical_id(token)
        if not technical_id:
            continue
        tc_id = mapping.get(technical_id)
        if not tc_id or tc_id not in cards or tc_id in seen_tc:
            continue
        seen_tc.add(tc_id)
        technical_ids.append(technical_id)
    return technical_ids
