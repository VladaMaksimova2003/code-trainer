"""Expected concept cards for MPLT pairs include hints and registry examples."""

from __future__ import annotations

from application.curriculum.validation.expected_concept_checker import (
    build_display_expected_concept_cards_for_pair,
)


def test_integer_division_pair_marks_arithmetic_and_keeps_examples():
    cards = build_display_expected_concept_cards_for_pair(
        ["program_entry", "stdin_read", "stdout_write", "counted_loop", "arithmetic_ops"],
        source_language="python",
        target_language="pascal",
        pitfall_ids=["integer_division"],
    )
    arithmetic = next((c for c in cards if c.get("id") == "tc_arithmetic"), None)
    assert arithmetic is not None
    assert arithmetic.get("in_proactive_scope") is True
    assert arithmetic.get("transfer_hint_ru")
    examples = arithmetic.get("examples_by_language") or {}
    assert examples.get("python")
    assert examples.get("pascal")
    py_codes = " ".join(str(row.get("code") or "") for row in examples["python"])
    pas_codes = " ".join(str(row.get("code") or "") for row in examples["pascal"])
    assert "//" in py_codes
    assert "div" in pas_codes
