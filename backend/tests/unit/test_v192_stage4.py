"""Stage 4: reactive MPLT transfer feedback in submission pipeline."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from application.execution.pipeline_runner import WorkerPipelineRunner, _is_non_blocking_warning


def test_transfer_pitfall_warning_is_non_blocking():
    assert _is_non_blocking_warning({"type": "TRANSFER_PITFALL", "text": "x"})
    assert _is_non_blocking_warning({"type": "CONSTRUCTION_WARNING", "text": "x"})
    assert _is_non_blocking_warning({"type": "ALGORITHM", "text": "x"})
    assert not _is_non_blocking_warning({"type": "CONSTRUCTION", "text": "x"})


def test_append_transfer_pitfall_on_failed_tests():
    runner = WorkerPipelineRunner()
    db = MagicMock()
    failed_tests = [{"case": 1, "status": "FAILED", "expected": "2", "actual": "3"}]

    with patch(
        "application.curriculum.display.mplt_submit_profile.resolve_mplt_submit_profile",
    ) as profile_mock, patch(
        "application.curriculum.display.transfer_pitfall_detector.detect_transfer_pitfalls",
        return_value=[
            {
                "text": "Возможный перенос (FCC): div",
                "type": "TRANSFER_PITFALL",
                "pitfall_id": "integer_division",
                "transfer_type": "FCC",
                "feedback_ru": "div",
            }
        ],
    ) as detect_mock:
        from application.curriculum.display.mplt_submit_profile import MpltSubmitProfile
        from application.curriculum.display.pitfall_catalog import get_pitfall

        profile_mock.return_value = MpltSubmitProfile(
            pattern_key="task_006",
            dominant_pitfall_id="integer_division",
            debug_id=None,
            transfer_category="FCC",
            pitfall=get_pitfall("integer_division"),
            source_language="python",
            target_language="pascal",
            buggy_code="writeln(total / n);",
        )
        merged = runner._append_post_submit_feedback(
            db,
            task_id=999,
            code="writeln(total / n);",
            language="pascal",
            pattern_errors=[],
            test_results=failed_tests,
        )

    detect_mock.assert_called_once()
    assert len(merged) == 1
    assert merged[0]["type"] == "TRANSFER_PITFALL"
    assert merged[0]["pitfall_id"] == "integer_division"


def test_transfer_pitfall_detector_uses_feedback_ru():
    from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls

    hits = detect_transfer_pitfalls(
        pitfall_id="integer_division",
        transfer_type="FCC",
        source_language="python",
        target_language="pascal",
        code="writeln(total / n);",
        test_results=[{"status": "FAILED"}],
    )
    assert hits
    assert hits[0]["type"] == "TRANSFER_PITFALL"
    assert hits[0].get("feedback_ru")
    assert "FCC" in hits[0]["text"]


def test_append_afcc_on_failed_contrast_test():
    runner = WorkerPipelineRunner()
    db = MagicMock()
    failed_tests = [
        {"case": 1, "status": "PASSED"},
        {"case": 2, "status": "FAILED", "expected": "4 2 1", "actual": "4 3 1"},
    ]

    with patch(
        "application.curriculum.display.mplt_submit_profile.resolve_mplt_submit_profile",
    ) as profile_mock, patch(
        "application.curriculum.display.transfer_pitfall_detector.detect_transfer_pitfalls",
        return_value=[
            {
                "text": "Возможный перенос (AFCC, contrast): round",
                "type": "TRANSFER_PITFALL",
                "pitfall_id": "round_semantics",
                "transfer_type": "AFCC",
                "detection": "contrast",
            }
        ],
    ):
        from application.curriculum.display.mplt_submit_profile import MpltSubmitProfile
        from application.curriculum.display.pitfall_catalog import get_pitfall

        profile_mock.return_value = MpltSubmitProfile(
            pattern_key="task_008",
            dominant_pitfall_id="round_semantics",
            debug_id=None,
            transfer_category="AFCC",
            pitfall=get_pitfall("round_semantics"),
            source_language="python",
            target_language="pascal",
            buggy_code="",
        )
        merged = runner._append_post_submit_feedback(
            db,
            task_id=8,
            code="program T; begin writeln(4, 3, 1); end.",
            language="pascal",
            pattern_errors=[],
            test_results=failed_tests,
        )

    assert len(merged) == 1
    assert merged[0]["type"] == "TRANSFER_PITFALL"
    assert merged[0]["pitfall_id"] == "round_semantics"
    assert merged[0]["detection"] == "contrast"
