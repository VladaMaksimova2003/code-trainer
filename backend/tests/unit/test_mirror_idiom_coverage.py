"""Mirror idiom matrix, pitfall pair hints, and proactive FCC coverage."""

from __future__ import annotations

from application.curriculum.display.atcc_idiom_engine import idiom_hint_for_concept
from application.curriculum.display.mirror_idiom_matrix import (
    KNOWN_LANGS,
    _MATRIX,
    count_matrix_pairs,
    matrix_idiom_brief,
)
from application.curriculum.display.pitfall_catalog import build_pitfall_payload_for_languages
from application.curriculum.display.pitfall_pair_hints import proactive_pitfall_hint

EXPECTED_PAIRS_PER_CONCEPT = len(KNOWN_LANGS) * (len(KNOWN_LANGS) - 1)


def test_matrix_full_grid_for_core_concepts():
    assert count_matrix_pairs() == len(_MATRIX) * EXPECTED_PAIRS_PER_CONCEPT
    for concept, pairs in _MATRIX.items():
        assert len(pairs) == EXPECTED_PAIRS_PER_CONCEPT, concept
        for src in KNOWN_LANGS:
            for tgt in KNOWN_LANGS:
                if src == tgt:
                    continue
                assert (src, tgt) in pairs, f"{concept}: {src}->{tgt}"


def test_reverse_pairs_in_matrix_and_idiom_engine():
    assert matrix_idiom_brief("pascal", "cpp", "program_entry")
    assert matrix_idiom_brief("cpp", "java", "program_entry")
    hint = idiom_hint_for_concept("cpp", "java", "program_entry")
    assert hint
    assert "Java" in hint


def test_fcc_proactive_cpp_to_pascal_integer_division():
    payload = build_pitfall_payload_for_languages(
        "integer_division",
        source_language="cpp",
        target_language="pascal",
    )
    assert payload.get("pitfall_id") == "integer_division"
    assert "div" in payload["reference_warning_ru"].lower()


def test_fcc_proactive_java_to_python_integer_division():
    payload = build_pitfall_payload_for_languages(
        "integer_division",
        source_language="java",
        target_language="python",
    )
    assert payload.get("pitfall_id") == "integer_division"
    assert "//" in payload["reference_warning_ru"]


def test_pitfall_pair_hint_cpp_to_csharp_chain_comparison():
    hint = proactive_pitfall_hint(
        "chain_comparison",
        source_language="python",
        target_language="csharp",
    )
    assert hint
    assert "C#" in hint or "цепоч" in hint.lower()


def test_pas_to_cpp_index_hint_via_pair_overrides():
    hint = proactive_pitfall_hint(
        "index_1based",
        source_language="pascal",
        target_language="cpp",
    )
    assert hint
    assert "0" in hint
