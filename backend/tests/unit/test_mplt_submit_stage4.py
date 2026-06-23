"""Stage 4: post-submit transfer vs algorithm feedback (MPLT bindings)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from application.curriculum.content.algo_syntax_task_extra import algo_implementation
from application.curriculum.display.algorithm_debug_detector import detect_algorithm_debug
from application.curriculum.display.mplt_submit_profile import MpltSubmitProfile
from application.curriculum.display.pitfall_catalog import get_pitfall
from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls
from application.execution.pipeline_runner import WorkerPipelineRunner, _is_non_blocking_warning


def _buggy(pattern: str, lang: str = "pascal") -> str:
    impl = algo_implementation("", lang, slot_pattern_id=pattern)
    return str(impl.get("buggy_code") or "").strip()


def _profile(
    pattern: str,
    *,
    dominant: str | None = None,
    debug_id: str | None = None,
    transfer_category: str = "TCC",
    source: str = "python",
    target: str = "pascal",
) -> MpltSubmitProfile:
    pitfall = get_pitfall(dominant) if dominant else None
    return MpltSubmitProfile(
        pattern_key=pattern,
        dominant_pitfall_id=dominant,
        pitfall_ids=(dominant,) if dominant else (),
        debug_id=debug_id,
        transfer_category=transfer_category,
        pitfall=pitfall,
        source_language=source,
        target_language=target,
        buggy_code=_buggy(pattern, target),
    )


FAILED = [{"case": 1, "status": "FAILED", "expected": "1", "actual": "0"}]


def test_algorithm_warning_is_non_blocking():
    assert _is_non_blocking_warning({"type": "ALGORITHM", "text": "x"})


def test_task_004_buggy_solution_returns_algorithm_not_transfer():
    buggy = _buggy("task_004")
    hits = detect_algorithm_debug(
        debug_id="filter_positive",
        target_language="pascal",
        code=buggy,
        test_results=FAILED,
        buggy_code=buggy,
    )
    transfer = detect_transfer_pitfalls(
        pitfall_id="filter_positive",
        transfer_type="FCC",
        source_language="python",
        target_language="pascal",
        code=buggy,
        test_results=FAILED,
        buggy_code=buggy,
    )

    assert hits
    assert hits[0]["type"] == "ALGORITHM"
    assert hits[0]["debug_id"] == "filter_positive"
    assert not transfer


def test_task_007_buggy_solution_returns_algorithm():
    buggy = _buggy("task_007")
    hits = detect_algorithm_debug(
        debug_id="threshold_count",
        target_language="pascal",
        code=buggy,
        test_results=FAILED,
        buggy_code=buggy,
    )
    assert hits
    assert hits[0]["type"] == "ALGORITHM"


def test_task_012_buggy_solution_returns_algorithm():
    buggy = _buggy("task_012")
    hits = detect_algorithm_debug(
        debug_id="branch_logic",
        target_language="pascal",
        code=buggy,
        test_results=FAILED,
        buggy_code=buggy,
    )
    assert hits
    assert hits[0]["type"] == "ALGORITHM"


def test_task_006_integer_division_returns_fcc_transfer():
    code = "var total, n: integer; begin total := 10; n := 3; writeln(total / n); end."
    hits = detect_transfer_pitfalls(
        pitfall_id="integer_division",
        transfer_type="FCC",
        source_language="python",
        target_language="pascal",
        code=code,
        test_results=FAILED,
    )
    assert hits
    assert hits[0]["type"] == "TRANSFER_PITFALL"
    assert hits[0]["transfer_type"] == "FCC"
    assert hits[0]["pitfall_id"] == "integer_division"


def test_task_003_input_model_contrast_fail_returns_afcc_transfer():
    failed = [
        {"case": 1, "status": "FAILED", "expected": "6", "actual": "0"},
        {"case": 2, "status": "PASSED"},
    ]
    hits = detect_transfer_pitfalls(
        pitfall_id="input_line_model",
        transfer_type="AFCC",
        source_language="python",
        target_language="pascal",
        code="program T; var a,b,c: integer; begin readln(a); readln(b); readln(c); writeln(a+b+c); end.",
        test_results=failed,
    )
    assert hits
    assert hits[0]["type"] == "TRANSFER_PITFALL"
    assert hits[0]["transfer_type"] == "AFCC"
    assert hits[0]["pitfall_id"] == "input_line_model"


def test_task_011_no_dominant_pitfall_skips_atcc_carryover():
    code = "program T; begin print('hi'); end."
    profile = _profile("task_011")
    assert profile.dominant_pitfall_id is None

    runner = WorkerPipelineRunner()
    db = MagicMock()
    with patch(
        "application.curriculum.display.mplt_submit_profile.resolve_mplt_submit_profile",
        return_value=profile,
    ):
        merged = runner._append_atcc_carryover_warnings(db, 11, code, "pascal", [])

    assert merged == []


def test_task_023_debug_without_pitfall_no_fcc_from_action_default():
    profile = _profile("task_023")
    assert profile.dominant_pitfall_id is None
    assert profile.debug_id is None

    runner = WorkerPipelineRunner()
    db = MagicMock()
    with patch(
        "application.curriculum.display.mplt_submit_profile.resolve_mplt_submit_profile",
        return_value=profile,
    ):
        merged = runner._append_post_submit_feedback(
            db,
            23,
            "program T; begin writeln(total / n); end.",
            "pascal",
            [],
            FAILED,
        )

    assert not any(item.get("type") == "TRANSFER_PITFALL" for item in merged)


def test_tcc_task_source_syntax_without_dominant_pitfall_no_transfer_warning():
    runner = WorkerPipelineRunner()
    db = MagicMock()
    profile = _profile("task_001")
    code = "program T; begin print('x'); end."

    with patch(
        "application.curriculum.display.mplt_submit_profile.resolve_mplt_submit_profile",
        return_value=profile,
    ):
        carryover = runner._append_atcc_carryover_warnings(db, 1, code, "pascal", [])
        post = runner._append_post_submit_feedback(db, 1, code, "pascal", carryover, FAILED)

    transfer = [item for item in post if item.get("type") == "TRANSFER_PITFALL"]
    assert not transfer


def test_post_submit_profile_wires_algorithm_and_transfer_separately():
    runner = WorkerPipelineRunner()
    db = MagicMock()
    profile = _profile(
        "task_004",
        debug_id="filter_positive",
        transfer_category="TCC",
    )
    buggy = profile.buggy_code

    with patch(
        "application.curriculum.display.mplt_submit_profile.resolve_mplt_submit_profile",
        return_value=profile,
    ):
        merged = runner._append_post_submit_feedback(
            db,
            4,
            buggy,
            "pascal",
            [],
            FAILED,
        )

    assert any(item.get("type") == "ALGORITHM" for item in merged)
    assert not any(item.get("type") == "TRANSFER_PITFALL" for item in merged)


def test_atcc_carryover_scoped_to_dominant_pitfall_concepts():
    runner = WorkerPipelineRunner()
    db = MagicMock()
    profile = _profile(
        "task_020",
        dominant="for_range_off_by_one",
        transfer_category="ATCC",
    )
    code = "program T; begin for i in range(5) do writeln(i); end."

    with patch(
        "application.curriculum.display.mplt_submit_profile.resolve_mplt_submit_profile",
        return_value=profile,
    ):
        merged = runner._append_atcc_carryover_warnings(db, 20, code, "pascal", [])

    assert merged
    assert all(item.get("type") == "TRANSFER_PITFALL" for item in merged)
    assert all(item.get("transfer_type") == "ATCC" for item in merged)
    assert merged[0].get("pitfall_id") == "for_range_off_by_one"
