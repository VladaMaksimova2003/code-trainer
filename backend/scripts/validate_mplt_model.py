#!/usr/bin/env python3
"""Validate approved MPLT methodology model (Stage 1 — data layer only)."""

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
from application.curriculum.display.algorithm_debug_catalog import (  # noqa: E402
    ALGORITHM_DEBUG,
    validate_algorithm_debug_id,
)
from application.curriculum.display.mplt_pattern_bindings import (  # noqa: E402
    MPLT_PATTERN_BINDINGS,
    binding_stats,
    get_mplt_pattern_binding,
    list_patterns_with_debug_id,
    list_patterns_with_dominant_pitfall,
)
from application.curriculum.display.pitfall_catalog import (  # noqa: E402
    PITFALLS,
    get_pitfall,
    validate_pitfall_id,
)

_EXPECTED_PITFALL_COUNT = 22
_EXPECTED_DEBUG_COUNT = 5
_EXPECTED_PATTERN_COUNT = 192

_RECLASSIFIED = {
    "for_range_off_by_one": "ATCC",
    "float_division_pascal": "AFCC",
    "mod_negative": "AFCC",
}

_ALGORITHM_DEBUG_IDS = frozenset(
    {
        "filter_positive",
        "threshold_count",
        "branch_logic",
        "multi_branch_discount",
        "map_key_missing",
    }
)


def _errors() -> list[str]:
    errors: list[str] = []

    if len(MPLT_PATTERN_BINDINGS) != _EXPECTED_PATTERN_COUNT:
        errors.append(
            f"binding table size {len(MPLT_PATTERN_BINDINGS)} != {_EXPECTED_PATTERN_COUNT}"
        )

    catalog_patterns = set(ALGO_SYNTAX_META.keys())
    binding_patterns = set(MPLT_PATTERN_BINDINGS.keys())
    missing = sorted(catalog_patterns - binding_patterns)
    extra = sorted(binding_patterns - catalog_patterns)
    if missing:
        errors.append(f"bindings missing patterns: {missing[:5]}{'...' if len(missing) > 5 else ''}")
    if extra:
        errors.append(f"bindings unknown patterns: {extra[:5]}{'...' if len(extra) > 5 else ''}")

    if len(PITFALLS) != _EXPECTED_PITFALL_COUNT:
        errors.append(f"PITFALLS count {len(PITFALLS)} != {_EXPECTED_PITFALL_COUNT}")

    if len(ALGORITHM_DEBUG) != _EXPECTED_DEBUG_COUNT:
        errors.append(f"ALGORITHM_DEBUG count {len(ALGORITHM_DEBUG)} != {_EXPECTED_DEBUG_COUNT}")

    overlap = set(PITFALLS.keys()) & set(ALGORITHM_DEBUG.keys())
    if overlap:
        errors.append(f"ids present in both catalogs: {sorted(overlap)}")

    for debug_id in _ALGORITHM_DEBUG_IDS:
        if debug_id in PITFALLS:
            errors.append(f"algorithm debug {debug_id!r} still in PITFALLS")
        if not validate_algorithm_debug_id(debug_id):
            errors.append(f"missing algorithm debug entry {debug_id!r}")

    for pitfall_id, expected_tt in _RECLASSIFIED.items():
        spec = get_pitfall(pitfall_id)
        if not spec:
            errors.append(f"reclassified pitfall missing: {pitfall_id}")
            continue
        actual = str(spec.get("transfer_type") or "").upper()
        if actual != expected_tt:
            errors.append(f"{pitfall_id}: transfer_type {actual} != {expected_tt}")

    for pattern_id, row in MPLT_PATTERN_BINDINGS.items():
        dominant = row.get("dominant_pitfall_id")
        debug = row.get("debug_id")
        category = str(row.get("transfer_category") or "").upper()

        if dominant and debug:
            errors.append(f"{pattern_id}: dominant_pitfall_id and debug_id both set (mutex v1)")

        if dominant:
            if not validate_pitfall_id(str(dominant)):
                errors.append(f"{pattern_id}: unknown dominant_pitfall_id {dominant!r}")
            else:
                pitfall_tt = str(get_pitfall(str(dominant)).get("transfer_type") or "").upper()
                if category != pitfall_tt:
                    errors.append(
                        f"{pattern_id}: transfer_category {category} != pitfall {pitfall_tt}"
                    )
        elif debug:
            if not validate_algorithm_debug_id(str(debug)):
                errors.append(f"{pattern_id}: unknown debug_id {debug!r}")
            if category != "TCC":
                errors.append(f"{pattern_id}: debug_id set but transfer_category {category} != TCC")
        elif category != "TCC":
            errors.append(f"{pattern_id}: no binding but transfer_category {category} != TCC")

    for row in V192_EXPANSION_INDEX:
        pat = str(row.get("pattern_id") or "")
        plan_pid = str(row.get("pitfall_id") or "").strip()
        if not plan_pid:
            continue
        binding = get_mplt_pattern_binding(pat)
        if not binding:
            errors.append(f"v192 {pat}: no binding row")
            continue
        if str(binding.get("dominant_pitfall_id") or "") != plan_pid:
            errors.append(
                f"v192 {pat}: binding dominant {binding.get('dominant_pitfall_id')!r} "
                f"!= plan {plan_pid!r}"
            )

    return errors


def main() -> int:
    errors = _errors()
    stats = binding_stats()

    print("MPLT model validation (Stage 1)")
    print(f"  patterns: {stats['total']}")
    print(f"  TCC: {stats['TCC']}")
    print(f"  ATCC: {stats['ATCC']}")
    print(f"  FCC: {stats['FCC']}")
    print(f"  AFCC: {stats['AFCC']}")
    print(f"  with dominant_pitfall_id: {stats['with_dominant_pitfall']}")
    print(f"  with debug_id: {stats['with_debug_id']}")
    print(f"  PITFALLS: {len(PITFALLS)}")
    print(f"  ALGORITHM_DEBUG: {len(ALGORITHM_DEBUG)}")

    dominant_patterns = list_patterns_with_dominant_pitfall()
    debug_patterns = list_patterns_with_debug_id()
    print(f"  dominant patterns ({len(dominant_patterns)}): {', '.join(dominant_patterns)}")
    print(f"  debug patterns ({len(debug_patterns)}): {', '.join(debug_patterns)}")

    if errors:
        print("ERRORS:")
        for line in errors:
            print(f"  - {line}")
        return 1

    print("OK: MPLT Stage 1 model is consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
