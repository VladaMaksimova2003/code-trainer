"""Unit tests for AFCC contrast detector (stage 5 regression)."""

from application.curriculum.display.afcc_contrast_detector import (
    contrast_indices_failed,
    detect_afcc_contrast,
    detect_afcc_pitfall,
    resolve_test_result_at_index,
)
from application.curriculum.display.pitfall_catalog import get_pitfall


def test_resolve_test_result_by_index_and_case_number():
    results = [
        {"case": 1, "status": "PASSED"},
        {"case": 2, "status": "FAILED"},
    ]
    assert resolve_test_result_at_index(results, 1)["status"] == "FAILED"
    assert resolve_test_result_at_index(results, 99) is None


def test_afcc_fires_only_when_contrast_index_failed():
    spec = get_pitfall("round_semantics")
    assert spec
    results = [
        {"case": 1, "status": "PASSED"},
        {"case": 2, "status": "FAILED"},
        {"case": 3, "status": "PASSED"},
    ]
    hits = detect_afcc_contrast(spec, test_results=results, atcc_already_fired=False)
    assert hits
    assert hits[0]["detection"] == "contrast"
    assert hits[0]["contrast_case_index"] == "1"


def test_afcc_not_fired_when_only_non_contrast_tests_fail():
    spec = get_pitfall("round_semantics")
    assert spec
    results = [
        {"case": 1, "status": "FAILED"},
        {"case": 2, "status": "PASSED"},
        {"case": 3, "status": "FAILED"},
    ]
    assert not detect_afcc_contrast(spec, test_results=results, atcc_already_fired=False)


def test_afcc_suppressed_when_atcc_already_fired():
    spec = get_pitfall("round_semantics")
    assert spec
    results = [{"status": "FAILED"}, {"status": "FAILED"}]
    assert not detect_afcc_contrast(
        spec,
        test_results=results,
        atcc_already_fired=True,
    )


def test_input_line_model_contrast_index_zero():
    spec = get_pitfall("input_line_model")
    assert spec
    assert spec.get("contrast_test_indices") == [0]
    failed = contrast_indices_failed(spec, [{"status": "FAILED"}, {"status": "PASSED"}])
    assert failed == [0]


def test_detect_afcc_integration_round_semantics():
    spec = get_pitfall("round_semantics")
    assert spec
    hits = detect_afcc_pitfall(
        spec,
        target_language="pascal",
        code="writeln(3);",
        test_results=[{"status": "PASSED"}, {"status": "FAILED"}],
        atcc_already_fired=False,
    )
    assert hits
    assert "AFCC" in hits[0]["text"]
    assert hits[0]["transfer_type"] == "AFCC"


def test_task_008_contrast_case_in_catalog():
    import sys
    from pathlib import Path

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from algo_v128_catalog import ALGO_SYNTAX_META

    case = ALGO_SYNTAX_META["task_008"]["test_cases"][1]
    assert case.get("mplt_contrast") is True
    assert case["inputs"] == "2\n1\n4\n"
    assert case["output"] == "4 2 1"
