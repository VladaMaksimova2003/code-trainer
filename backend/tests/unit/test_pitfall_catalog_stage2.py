"""Tests for pitfall catalog and transfer pitfall detector (stage 2)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_pitfall_catalog_has_methodology_entries():
    from application.curriculum.display.pitfall_catalog import (
        PITFALLS,
        list_pitfall_ids,
        pitfall_ids_for_transfer_type,
        validate_pitfall_id,
    )

    assert len(PITFALLS) >= 20
    assert validate_pitfall_id("integer_division")
    assert validate_pitfall_id("chain_comparison")
    assert validate_pitfall_id("list_vs_static_array")
    assert "round_semantics" in list_pitfall_ids()
    assert "integer_division" in pitfall_ids_for_transfer_type("FCC")
    assert "round_semantics" in pitfall_ids_for_transfer_type("AFCC")
    assert "for_range_off_by_one" in pitfall_ids_for_transfer_type("ATCC")
    assert "float_division_pascal" in pitfall_ids_for_transfer_type("AFCC")
    assert "mod_negative" in pitfall_ids_for_transfer_type("AFCC")
    assert not validate_pitfall_id("filter_positive")


def test_v192_plan_pitfall_ids_exist_in_catalog():
    from algo_v192_plan import V192_EXPANSION_INDEX
    from application.curriculum.display.pitfall_catalog import validate_pitfall_id

    missing = [
        row["pitfall_id"]
        for row in V192_EXPANSION_INDEX
        if row.get("pitfall_id") and not validate_pitfall_id(str(row["pitfall_id"]))
    ]
    assert not missing, f"Unknown pitfall_id in v192 plan: {missing}"


def test_build_pitfall_payload_includes_reference_warning():
    from application.curriculum.display.pitfall_catalog import build_pitfall_payload

    payload = build_pitfall_payload("round_semantics")
    assert payload["transfer_type"] == "AFCC"
    assert payload.get("reference_warning_ru")
    assert payload.get("feedback_ru")


def test_fcc_detector_index_1based():
    from application.curriculum.display.pitfall_catalog import get_pitfall
    from application.curriculum.display.transfer_pitfall_detector import detect_fcc_pitfall

    spec = get_pitfall("index_1based")
    assert spec
    hits = detect_fcc_pitfall(
        spec,
        target_language="pascal",
        code="program T; var a: array[1..10] of integer; begin writeln(a[0]); end.",
        buggy_code="",
    )
    assert hits
    assert hits[0]["pitfall_id"] == "index_1based"
    assert hits[0]["type"] == "TRANSFER_PITFALL"
    assert hits[0]["detection"] == "ast"


def test_fcc_detector_integer_division_pattern():
    from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls

    hits = detect_transfer_pitfalls(
        pitfall_id="integer_division",
        transfer_type="FCC",
        source_language="python",
        target_language="pascal",
        code="writeln(total / n);",
        test_results=[],
    )
    assert hits
    assert "div" in hits[0]["text"].lower() or "FCC" in hits[0]["text"]


def test_afcc_detector_on_failed_contrast_test():
    from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls

    hits = detect_transfer_pitfalls(
        pitfall_id="round_semantics",
        transfer_type="AFCC",
        source_language="python",
        target_language="pascal",
        code="writeln(Round(x));",
        test_results=[{"status": "FAILED"}, {"status": "FAILED"}],
        atcc_warnings=[],
    )
    assert hits
    assert hits[0]["transfer_type"] == "AFCC"
    assert hits[0]["detection"] == "contrast"


def test_mplt_binding_task_012_algorithm_debug():
    from application.curriculum.display.algorithm_debug_catalog import build_algorithm_debug_payload
    from application.curriculum.display.mplt_pattern_bindings import get_mplt_pattern_binding

    row = get_mplt_pattern_binding("task_012")
    assert row
    assert row.get("dominant_pitfall_id") is None
    assert row.get("debug_id") == "branch_logic"
    assert row.get("transfer_category") == "TCC"
    debug = build_algorithm_debug_payload("branch_logic")
    assert debug.get("feedback_ru")


def test_resolve_v128_transfer_meta_task_020_atcc_binding():
    from application.curriculum.display.mplt_pattern_bindings import get_mplt_pattern_binding
    from application.curriculum.display.pitfall_catalog import get_pitfall
    from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta

    meta = resolve_v128_transfer_meta("task_020")
    assert meta.get("pitfall_id") == "for_range_off_by_one"
    binding = get_mplt_pattern_binding("task_020")
    assert binding.get("dominant_pitfall_id") == "for_range_off_by_one"
    assert binding.get("transfer_category") == "ATCC"
    assert get_pitfall("for_range_off_by_one").get("transfer_type") == "ATCC"


def test_list_v128_patterns_with_pitfall_from_bindings():
    from application.curriculum.display.v128_transfer_meta import list_v128_patterns_with_pitfall

    patterns = list_v128_patterns_with_pitfall()
    assert "task_012" not in patterns
    assert "task_020" in patterns
    assert len(patterns) >= 18


def test_sanitize_attaches_transfer_for_task_008_afcc():
    from application.curriculum.display.showcase_display import sanitize_public_task_payload

    payload = sanitize_public_task_payload(
        {
            "id": 8,
            "title": "Round semantics",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": "pas_008",
                    "slot_pattern_id": "task_008",
                    "target_language": "pascal",
                },
            },
        }
    )
    transfer = payload.get("transfer") or {}
    assert transfer.get("pitfall_id") == "round_semantics"
    assert transfer.get("transfer_type") == "AFCC"
    assert transfer.get("pedagogy_note_ru") or transfer.get("reference_warning_ru")
