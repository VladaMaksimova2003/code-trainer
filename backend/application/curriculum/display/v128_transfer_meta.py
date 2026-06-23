"""Transfer-type and pitfall/debug binding for algorithm-syntax slots (Stage 2)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from application.curriculum.display.algorithm_debug_catalog import build_algorithm_debug_payload
from application.curriculum.display.mplt_pattern_bindings import (
    MPLT_PATTERN_BINDINGS,
    get_mplt_pattern_binding,
    list_patterns_with_debug_id,
    list_patterns_with_dominant_pitfall,
)
from application.curriculum.display.pitfall_catalog import TransferType, build_pitfall_payload

_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: E402
except ImportError:
    ALGO_SYNTAX_META: dict[str, dict[str, Any]] = {}

# Optional extra pedagogy line per pattern (shown when dominant pitfall has proactive banner)
_PEDAGOGY_NOTE_BY_PATTERN: dict[str, str] = {
    "task_008": (
        "Итоговая без подсказок-переноса: соберите решение из приёмов задач 1–7."
    ),
    "task_024": (
        "Итоговая без проактивных баннеров: min/max/sum/avg и целочисленное деление из задач 17–23."
    ),
}

# Backward compat for diagnostic scripts (dominant pitfalls only, not AlgorithmDebug).
_EXPLICIT_PITFALL_BY_PATTERN: dict[str, str] = {
    pat: str(row["dominant_pitfall_id"])
    for pat, row in MPLT_PATTERN_BINDINGS.items()
    if row.get("dominant_pitfall_id")
}


def pattern_action(pattern_key: str | None) -> str | None:
    if not pattern_key:
        return None
    raw = ALGO_SYNTAX_META.get(str(pattern_key).strip()) or {}
    action = str(raw.get("action") or "").strip().lower()
    return action or None


def default_transfer_type_for_action(action: str | None) -> TransferType:
    """Deprecated: action no longer implies MPLT category (Stage 2)."""
    _ = action
    return "TCC"


def resolve_v128_transfer_meta(pattern_key: str | None) -> dict[str, Any]:
    """Return transfer_type, pitfall_id/debug_id and pitfall texts from binding table."""
    key = str(pattern_key or "").strip()
    if not key:
        return {"transfer_type": "TCC"}

    binding = get_mplt_pattern_binding(key)
    if not binding:
        return {"transfer_type": "TCC", "slot_pattern_id": key}

    dominant = binding.get("dominant_pitfall_id")
    debug_id = binding.get("debug_id")
    transfer_type: TransferType = binding.get("transfer_category") or "TCC"  # type: ignore[assignment]

    result: dict[str, Any] = {
        "transfer_type": transfer_type,
        "slot_pattern_id": key,
        "pitfall_id": dominant,
    }
    if debug_id:
        result["debug_id"] = debug_id
        debug_payload = build_algorithm_debug_payload(str(debug_id))
        if debug_payload:
            result["debug_meta"] = debug_payload

    if dominant:
        pitfall = build_pitfall_payload(str(dominant))
        for field, value in pitfall.items():
            if value is not None and field not in result:
                result[field] = value
        result["pitfall_id"] = dominant
        result["transfer_type"] = pitfall.get("transfer_type") or transfer_type

    note = _PEDAGOGY_NOTE_BY_PATTERN.get(key)
    if note and dominant and str(result.get("transfer_type") or "").upper() != "TCC":
        result["pedagogy_note_ru"] = note

    return result


def list_debug_patterns_with_pitfalls() -> list[str]:
    """Patterns with AlgorithmDebug binding (legacy name)."""
    return list_patterns_with_debug_id()


def list_v128_patterns_with_pitfall() -> list[str]:
    """Pattern keys with a dominant MPLT pitfall (binding table)."""
    return list_patterns_with_dominant_pitfall()
