"""Stage 2: MPLT resolver wired to mplt_pattern_bindings (GET task payload)."""

from __future__ import annotations

from application.curriculum.content.algo_syntax_showcase_meta import (
    enrich_student_expected_concepts,
    transfer_meta_for_language_pair,
)
from application.curriculum.display.showcase_display import sanitize_public_task_payload
from application.curriculum.display.v128_transfer_meta import (
    default_transfer_type_for_action,
    resolve_v128_transfer_meta,
)
from application.curriculum.validation.expected_concept_checker import (
    build_technical_expected_concept_cards,
)


def test_task_001_atcc_for_range_off_by_one():
    meta = transfer_meta_for_language_pair(
        "task_001",
        source_language="python",
        target_language="pascal",
    )
    assert meta["transfer_type"] == "ATCC"
    assert meta["pitfall_id"] == "for_range_off_by_one"
    assert "for_range_off_by_one" in meta["pitfall_ids"]
    assert meta["proactive"]["zone"] == "idiom"
    assert meta["proactive"]["text"]
    assert len(meta.get("proactive_items") or []) >= 1


def test_task_003_atcc_for_range_not_input_line():
    meta = transfer_meta_for_language_pair(
        "task_003",
        source_language="cpp",
        target_language="java",
    )
    assert meta["transfer_type"] == "ATCC"
    assert meta["pitfall_id"] == "for_range_off_by_one"
    assert meta["pitfall_id"] != "input_line_model"
    assert meta["proactive"]["zone"] == "idiom"
    assert meta["proactive"]["text"]
    assert "counted_loop" in meta["proactive"]["concept_ids"]


def test_task_006_fcc_integer_division():
    meta = transfer_meta_for_language_pair(
        "task_006",
        source_language="python",
        target_language="pascal",
    )
    assert meta["transfer_type"] == "FCC"
    assert meta["pitfall_id"] == "integer_division"
    assert meta["proactive"]["zone"] == "lexeme"
    assert meta["proactive"]["text"]
    assert "div" in meta["proactive"]["text"].lower() or "div" in str(meta.get("reference_warning_ru") or "").lower()


def test_task_020_atcc_for_range_off_by_one():
    meta = transfer_meta_for_language_pair(
        "task_020",
        source_language="python",
        target_language="pascal",
    )
    assert meta["transfer_type"] == "ATCC"
    assert meta["pitfall_id"] == "for_range_off_by_one"
    assert meta["proactive"]["zone"] == "idiom"
    assert meta["proactive"]["text"]


def test_task_004_tcc_algorithm_debug_no_transfer_banner():
    meta = transfer_meta_for_language_pair(
        "task_004",
        source_language="python",
        target_language="pascal",
    )
    assert meta["transfer_type"] == "TCC"
    assert meta.get("pitfall_id") is None
    assert meta["debug_id"] == "filter_positive"
    assert meta["proactive"]["text"] is None
    assert not meta.get("reference_warning_ru")
    assert meta.get("debug_meta", {}).get("hint_ru")
    assert not meta.get("algorithm_proactive")


def test_implement_binding_task_005_is_atcc():
    resolved = resolve_v128_transfer_meta("task_005")
    assert resolved["transfer_type"] == "ATCC"
    assert resolved["pitfall_id"] == "for_range_off_by_one"
    assert default_transfer_type_for_action("implement") == "TCC"


def test_task_001_binding_is_atcc_not_fcc():
    resolved = resolve_v128_transfer_meta("task_001")
    assert resolved["transfer_type"] == "ATCC"
    assert resolved["pitfall_id"] == "for_range_off_by_one"
    assert default_transfer_type_for_action("debug") == "TCC"


def test_chapter1_pair_has_proactive_banner():
    meta = transfer_meta_for_language_pair(
        "task_005",
        source_language="pascal",
        target_language="cpp",
    )
    assert meta["transfer_type"] == "ATCC"
    assert meta["pitfall_id"] == "for_range_off_by_one"
    assert meta["proactive"]["text"]


def test_chip_transfer_hint_only_on_pitfall_concepts():
    cards_tcc = build_technical_expected_concept_cards(
        ["program_entry", "arithmetic_ops", "stdin_read"],
        learning_language="pascal",
        source_language="python",
        pitfall_id=None,
    )
    assert all(not c.get("transfer_hint_ru") for c in cards_tcc)
    assert all(c.get("in_proactive_scope") is False for c in cards_tcc)

    cards_fcc = build_technical_expected_concept_cards(
        ["program_entry", "arithmetic_ops", "stdin_read"],
        learning_language="pascal",
        source_language="python",
        pitfall_id="integer_division",
    )
    arith = next(c for c in cards_fcc if c["id"] == "arithmetic_ops")
    program = next(c for c in cards_fcc if c["id"] == "program_entry")
    assert arith.get("in_proactive_scope") is True
    assert arith.get("transfer_hint_ru")
    assert program.get("in_proactive_scope") is False
    assert not program.get("transfer_hint_ru")


def test_sanitize_attaches_transfer_block_for_chapter1_pair():
    payload = sanitize_public_task_payload(
        {
            "id": 1,
            "title": "Max",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_pattern_id": "task_001",
                    "exercise_pattern_id": "task_001",
                    "target_language": "pascal",
                },
            },
        }
    )
    transfer = payload.get("transfer") or {}
    assert transfer.get("transfer_type") == "ATCC"
    assert transfer.get("pitfall_id") == "for_range_off_by_one"
    assert transfer.get("proactive", {}).get("text")


def test_sanitize_algorithm_debug_task_004():
    payload = sanitize_public_task_payload(
        {
            "id": 4,
            "title": "Filter positive",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": "pas_005",
                    "slot_pattern_id": "task_004",
                    "target_language": "pascal",
                },
            },
        }
    )
    transfer = payload.get("transfer") or {}
    assert transfer.get("transfer_type") == "TCC"
    assert transfer.get("debug_id") == "filter_positive"
    assert transfer.get("pitfall_id") is None
    assert not transfer.get("reference_warning_ru")


def test_enrich_expected_concepts_in_proactive_scope_task_005():
    payload = enrich_student_expected_concepts(
        {
            "code_examples": {
                "python": "n = int(input())\nfor _ in range(n):\n    pass",
                "curriculum_showcase": {
                    "known_language_variants": {
                        "python": {"source_code": "n = int(input())\nfor _ in range(n):\n    pass"},
                    },
                },
            },
        },
        pattern_key="task_005",
        slot_id="pas_002",
        target_language="pascal",
        slot_pattern_id="task_005",
    )
    cards = payload["curriculum"]["expected_concepts"]
    loop = next((c for c in cards if c["id"] == "counted_loop"), None)
    assert loop is not None
    assert loop.get("in_proactive_scope") is True
    assert loop.get("transfer_hint_ru")
