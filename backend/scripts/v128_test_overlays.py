"""Load and apply diversified v128 test-case overlays."""

from __future__ import annotations

from typing import Any

from v128_test_input_enrichment import enrich_all_suites
from v128_test_matrix import validate_test_suite
from v128_test_suites_corrections import V128_TEST_CORRECTIONS
from v128_test_suites_data import V128_TEST_SUITES


def build_merged_v128_test_suites() -> dict[str, list[dict[str, str]]]:
    merged = {k: [dict(row) for row in v] for k, v in V128_TEST_SUITES.items()}
    for pattern, cases in V128_TEST_CORRECTIONS.items():
        merged[pattern] = [dict(row) for row in cases]
    return enrich_all_suites(merged)


V128_TEST_SUITES_MERGED: dict[str, list[dict[str, str]]] = build_merged_v128_test_suites()


def apply_v128_test_overlays(meta: dict[str, dict[str, Any]]) -> None:
    """Replace catalog test_cases with tagged diversified suites."""
    from application.curriculum.content.v4_test_cases_io import normalize_pattern_test_cases

    for pattern, cases in V128_TEST_SUITES_MERGED.items():
        row = meta.get(pattern)
        if not row:
            continue
        refs = row.get("reference_codes") or {}
        row["test_cases"] = normalize_pattern_test_cases(
            [dict(c) for c in cases],
            pattern_id=pattern,
            reference_code=str(refs.get("python") or ""),
            pascal_code=str(refs.get("pascal") or ""),
            goal=str(row.get("detailed_description") or row.get("short_goal") or ""),
        )


def overlay_validation_errors(meta: dict[str, dict[str, Any]] | None = None) -> dict[str, list[str]]:
    """Validate merged suites against matrix rules."""
    errors: dict[str, list[str]] = {}
    source = meta if meta is not None else {k: {"test_cases": v} for k, v in V128_TEST_SUITES_MERGED.items()}
    for pattern in sorted(V128_TEST_SUITES_MERGED):
        row = source.get(pattern) or {}
        tests = row.get("test_cases") or V128_TEST_SUITES_MERGED.get(pattern) or []
        probs = validate_test_suite(pattern, tests)
        if probs:
            errors[pattern] = probs
    return errors
