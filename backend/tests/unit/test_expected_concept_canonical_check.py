"""Canonical expected-concept checking via AST detector."""

from application.curriculum.validation.expected_concept_checker import (
    analyze_expected_concepts,
    check_expected_concepts,
    concept_present_in_code,
    detect_expected_concepts_in_code,
    normalize_expected_display_tc_ids,
    normalize_expected_technical_ids,
)

PYTHON_LOOP_CODE = """
x = 0
for i in range(5):
    x += i
print(x)
""".strip()


def test_finds_assignment_loop_console_output():
    result = check_expected_concepts(
        PYTHON_LOOP_CODE,
        "python",
        ["assignment", "loop", "console_output"],
    )
    assert result.passed is True
    assert set(result.found) == {"assignment", "loop", "console_output"}
    assert result.missing == []
    assert "console_output" in result.detected_technical_ids
    assert "loop" in result.detected_technical_ids
    assert "arithmetic" not in result.detected_technical_ids or "arithmetic" in result.signal_ids


def test_if_condition_does_not_satisfy_assignment_expected():
    result = check_expected_concepts(
        "if x > 0:\n    print(x)\n",
        "python",
        ["assignment"],
    )
    assert result.passed is False
    assert result.missing == ["assignment"]
    assert "assignment" not in result.detected_technical_ids


def test_legacy_expected_ids_normalize_to_canonical():
    normalized = normalize_expected_technical_ids(["py_assign", "ast_assignment"])
    assert normalized == ["assignment"]


def test_display_expected_ids_compare_against_detected_display_tc():
    result = check_expected_concepts(
        PYTHON_LOOP_CODE,
        "python",
        ["tc_arithmetic", "tc_loops", "tc_console_io"],
    )
    assert result.mode == "display"
    assert result.passed is True
    assert set(result.found) == {"tc_arithmetic", "tc_console_io", "tc_loops"}
    assert normalize_expected_display_tc_ids(["tc_assignment", "tc_loops"]) == [
        "tc_arithmetic",
        "tc_loops",
    ]


def test_arithmetic_ops_legacy_id_matches_signal_nodes():
    result = check_expected_concepts(
        "x = 1 + 2\nprint(x)\n",
        "python",
        ["arithmetic_ops"],
    )
    assert result.passed is True
    assert result.found == ["arithmetic"]


def test_tc_arithmetic_display_id_matches_signal_nodes():
    result = check_expected_concepts(
        "for (int i = 0; i < n; i++) { }\n",
        "cpp",
        ["tc_arithmetic"],
    )
    assert result.mode == "display"
    assert result.passed is True
    assert result.found == ["tc_arithmetic"]


def test_missing_expected_concept_is_reported():
    result = check_expected_concepts(
        "print('hi')\n",
        "python",
        ["assignment", "loop"],
    )
    assert result.passed is False
    assert "assignment" in result.missing
    assert "loop" in result.missing
    assert result.found == []


def test_concept_check_payload_shape():
    payload = check_expected_concepts(
        PYTHON_LOOP_CODE,
        "python",
        ["assignment", "loop"],
    ).to_dict()
    assert payload["enabled"] is True
    assert payload["language"] == "python"
    assert "detected_technical_ids" in payload
    assert "detected_display_tc_ids" in payload
    assert "signal_ids" in payload
    assert isinstance(payload["signal_ids"], list)


def test_display_expected_cards_dedupe_legacy_assignment_variants():
    from application.curriculum.validation.expected_concept_checker import (
        build_display_expected_concept_cards,
    )

    cards = build_display_expected_concept_cards(
        ["assignment", "py_assign", "ast_assignment", "counted_loop"]
    )
    labels = [card["name_ru"] for card in cards]
    ids = [card["id"] for card in cards]
    assert "Арифметика и операции" in labels
    assert "Присваивание" not in labels
    assert "tc_arithmetic" in ids
    assert "tc_assignment" not in ids
    assert "tc_loops" in ids


def test_analyze_matches_import_detection_for_display_cards():
    code = "for i in range(3):\n    print(i)\n"
    cards = ["tc_loops", "tc_console_io"]
    items = analyze_expected_concepts(code, language="python", concept_ids=cards)
    detected = detect_expected_concepts_in_code(code, language="python")
    for item in items:
        assert item.detected == (item.id in detected)


def test_analyze_uses_same_path_as_prune_for_legacy_ids():
    code = "x = 1 + 2\nprint(x)\n"
    assert concept_present_in_code(code, "arithmetic_ops", language="python")
    items = analyze_expected_concepts(code, language="python", concept_ids=["arithmetic_ops"])
    assert items[0].detected is True


def test_display_expected_cards_include_examples_by_language():
    from application.curriculum.validation.expected_concept_checker import (
        build_display_expected_concept_cards,
    )

    cards = build_display_expected_concept_cards(["counted_loop", "console_output"])
    loops = next(card for card in cards if card["id"] == "tc_loops")
    assert loops["examples_by_language"]["cpp"]
    assert loops["examples_by_language"]["pascal"]
    assert loops["examples_by_language"]["python"]
    assert loops["examples_by_language"]["cpp"][0]["code"]
