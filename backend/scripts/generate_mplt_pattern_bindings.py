#!/usr/bin/env python3
"""Generate backend/application/curriculum/display/mplt_pattern_bindings.py."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: E402
from algo_v192_plan import V192_EXPANSION_INDEX  # noqa: E402
# Dominant MPLT transfer pitfalls (explicit methodology bindings).
_DOMINANT: dict[str, str] = {
    "task_002": "index_1based",
    "task_003": "input_line_model",
    "task_006": "integer_division",
    "task_008": "round_semantics",
    "task_020": "for_range_off_by_one",
    "task_027": "list_vs_static_array",
    "task_028": "index_1based",
    "task_036": "string_index",
    "task_187": "exception_model",
}

# Algorithm debug (orthogonal to transfer category; pattern transfer_category stays TCC).
_DEBUG: dict[str, str] = {
    "task_004": "filter_positive",
    "task_007": "threshold_count",
    "task_012": "branch_logic",
    "task_015": "multi_branch_discount",
    "task_076": "map_key_missing",
    "task_142": "map_key_missing",
}

for row in V192_EXPANSION_INDEX:
    pid = str(row.get("pitfall_id") or "").strip()
    pat = str(row["pattern_id"])
    if pid:
        _DOMINANT[pat] = pid


def _category(dominant: str | None, debug: str | None) -> str:
    if dominant:
        from application.curriculum.display.pitfall_catalog import get_pitfall

        spec = get_pitfall(dominant)
        if spec:
            return str(spec.get("transfer_type") or "TCC")
        return "TCC"
    return "TCC"


def build_bindings() -> dict[str, dict[str, str | None]]:
    out: dict[str, dict[str, str | None]] = {}
    for key in sorted(ALGO_SYNTAX_META.keys()):
        dominant = _DOMINANT.get(key)
        debug = _DEBUG.get(key)
        if dominant and debug:
            raise ValueError(f"mutex violation {key}: pitfall={dominant} debug={debug}")
        out[key] = {
            "dominant_pitfall_id": dominant,
            "debug_id": debug,
            "transfer_category": _category(dominant, debug),
        }
    return out


def render_python(bindings: dict[str, dict[str, str | None]]) -> str:
    lines = [
        '"""MPLT pattern bindings — authoritative Stage 1 (methodology approved).',
        "",
        "Each pattern has exactly one of:",
        "  - transfer_category TCC (no dominant_pitfall_id, no debug_id);",
        "  - dominant_pitfall_id → ATCC | FCC | AFCC;",
        "  - debug_id → AlgorithmDebug (transfer_category remains TCC).",
        "",
        "Runtime resolver wiring: Stage 2.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any, TypedDict",
        "",
        "",
        "class MpltPatternBinding(TypedDict):",
        '    dominant_pitfall_id: str | None',
        '    debug_id: str | None',
        '    transfer_category: str',
        "",
        "",
        "MPLT_PATTERN_BINDINGS: dict[str, MpltPatternBinding] = {",
    ]
    for pat, row in bindings.items():
        d = row["dominant_pitfall_id"]
        g = row["debug_id"]
        c = row["transfer_category"]
        d_repr = repr(d)
        g_repr = repr(g)
        lines.append(
            f'    "{pat}": {{"dominant_pitfall_id": {d_repr}, '
            f'"debug_id": {g_repr}, "transfer_category": "{c}"}},'
        )
    lines.extend(
        [
            "}",
            "",
            "",
            "def get_mplt_pattern_binding(pattern_id: str | None) -> MpltPatternBinding | None:",
            '    key = str(pattern_id or "").strip()',
            "    if not key:",
            "        return None",
            "    return MPLT_PATTERN_BINDINGS.get(key)",
            "",
            "",
            "def list_patterns_by_transfer_category(category: str) -> list[str]:",
            '    cat = str(category or "").strip().upper()',
            "    return sorted(",
            "        pat",
            "        for pat, row in MPLT_PATTERN_BINDINGS.items()",
            '        if str(row.get("transfer_category") or "").upper() == cat',
            "    )",
            "",
            "",
            "def list_patterns_with_dominant_pitfall() -> list[str]:",
            "    return sorted(",
            "        pat",
            "        for pat, row in MPLT_PATTERN_BINDINGS.items()",
            "        if row.get('dominant_pitfall_id')",
            "    )",
            "",
            "",
            "def list_patterns_with_debug_id() -> list[str]:",
            "    return sorted(",
            "        pat",
            "        for pat, row in MPLT_PATTERN_BINDINGS.items()",
            "        if row.get('debug_id')",
            "    )",
            "",
            "",
            "def binding_stats() -> dict[str, Any]:",
            "    stats = {",
            '        "total": len(MPLT_PATTERN_BINDINGS),',
            '        "TCC": len(list_patterns_by_transfer_category("TCC")),',
            '        "ATCC": len(list_patterns_by_transfer_category("ATCC")),',
            '        "FCC": len(list_patterns_by_transfer_category("FCC")),',
            '        "AFCC": len(list_patterns_by_transfer_category("AFCC")),',
            '        "with_dominant_pitfall": len(list_patterns_with_dominant_pitfall()),',
            '        "with_debug_id": len(list_patterns_with_debug_id()),',
            "    }",
            "    return stats",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    bindings = build_bindings()
    target = BACKEND / "application" / "curriculum" / "display" / "mplt_pattern_bindings.py"
    target.write_text(render_python(bindings), encoding="utf-8")
    print(f"wrote {target} patterns={len(bindings)}")
