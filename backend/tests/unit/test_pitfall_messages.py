"""Concrete MPLT message catalog — no vague transfer phrasing."""

from __future__ import annotations


def test_proactive_is_pair_only_without_verbatim_code():
    from application.curriculum.display.pitfall_messages import proactive_pitfall_message

    text = proactive_pitfall_message(
        "for_range_off_by_one",
        source_language="csharp",
        target_language="pascal",
    )
    assert text
    assert "Python" not in text
    assert "range(n)" not in text
    assert "for (int i = 0" not in text
    assert "for i :=" not in text
    assert "C#" in text or "c#" in text.lower() or "При переносе" in text
    assert "Pascal" in text


def test_reference_pitfalls_have_concrete_pair_messages():
    from application.curriculum.display.pitfall_messages import (
        _BANNED_FRAGMENTS,
        proactive_pitfall_message,
        reactive_pitfall_message,
    )

    reference = [
        "integer_division",
        "for_range_off_by_one",
        "input_line_model",
        "scope_block",
    ]
    for pid in reference:
        proactive = proactive_pitfall_message(pid, source_language="python", target_language="pascal")
        feedback = reactive_pitfall_message(pid, source_language="python", target_language="pascal")
        assert proactive, pid
        assert feedback, pid
        assert "Похоже" in feedback or "найден" in feedback.lower() or "Python:" in feedback
        for text in (proactive, feedback):
            lowered = text.lower()
            for banned in _BANNED_FRAGMENTS:
                assert banned not in lowered, f"{pid}: {banned!r} in {text[:80]}"


def test_fcc_integer_division_reactive_mentions_div():
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
    assert "div" in hits[0]["feedback_ru"].lower()
    assert "total / n" in hits[0]["feedback_ru"]


def test_afcc_input_line_reactive_shows_readln_fix():
    from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls

    hits = detect_transfer_pitfalls(
        pitfall_id="input_line_model",
        transfer_type="AFCC",
        source_language="python",
        target_language="pascal",
        code="readln(a); readln(b);",
        test_results=[{"status": "FAILED"}],
    )
    assert hits
    assert "readln(a, b, c" in hits[0]["feedback_ru"]


def test_atcc_range_reactive_has_both_loops():
    from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls

    hits = detect_transfer_pitfalls(
        pitfall_id="for_range_off_by_one",
        transfer_type="ATCC",
        source_language="python",
        target_language="pascal",
        code="for i := 0 to n do begin end;",
        test_results=[],
        buggy_code="for i := 0 to n do begin end;",
    )
    assert hits
    assert "range(n)" in hits[0]["feedback_ru"]
    assert "for i := 1 to n do" in hits[0]["feedback_ru"]
