"""Chapter 2 branches: per-task × per-language-pair pitfall bindings."""

from __future__ import annotations

import pytest

from application.curriculum.content.algo_syntax_showcase_meta import (
    transfer_meta_for_language_pair,
)
from application.curriculum.display.chapter2_branches_pitfalls import (
    CH2_SLOT_PATTERN_ORDER,
    resolve_chapter2_pitfall_ids,
    resolve_chapter2_proactive_pitfall_ids,
)
from application.curriculum.display.pitfall_messages import proactive_pitfall_message


@pytest.mark.parametrize(
    ("pattern", "source", "target", "expected_subset"),
    [
        ("task_009", "python", "pascal", ["assignment_vs_compare"]),
        ("task_010", "python", "pascal", ["elif_chain"]),
        ("task_013", "python", "pascal", ["chain_comparison", "elif_chain"]),
        ("task_012", "python", "pascal", ["input_line_model", "leap_year_mod"]),
        ("task_014", "python", "pascal", ["pascal_case_labels"]),
        ("task_016", "python", "pascal", []),
    ],
)
def test_chapter2_reactive_pitfalls(
    pattern: str,
    source: str,
    target: str,
    expected_subset: list[str],
) -> None:
    ids = resolve_chapter2_pitfall_ids(
        pattern,
        source_language=source,
        target_language=target,
    )
    for pid in expected_subset:
        assert pid in ids


def test_chapter2_proactive_skips_chapter1_pitfalls() -> None:
    """Ch.1 already taught assignment/input_line — ch.2 proactive must not repeat them."""
    first = resolve_chapter2_proactive_pitfall_ids(
        "task_009",
        source_language="python",
        target_language="pascal",
    )
    assert first == []

    date_proactive = resolve_chapter2_proactive_pitfall_ids(
        "task_012",
        source_language="python",
        target_language="pascal",
    )
    assert "input_line_model" not in date_proactive
    assert "leap_year_mod" in date_proactive


def test_chapter2_proactive_dedup_assignment() -> None:
    """elif_chain on slot 2; assignment from ch.1 never repeats proactively."""
    second = resolve_chapter2_proactive_pitfall_ids(
        "task_010",
        source_language="python",
        target_language="pascal",
    )
    assert "assignment_vs_compare" not in second
    assert "elif_chain" in second


def test_chapter2_capstone_no_proactive() -> None:
    assert (
        resolve_chapter2_proactive_pitfall_ids(
            "task_016",
            source_language="python",
            target_language="pascal",
        )
        == []
    )


def test_chapter2_transfer_meta_has_proactive_items() -> None:
    meta = transfer_meta_for_language_pair(
        "task_013",
        source_language="python",
        target_language="pascal",
    )
    items = meta.get("proactive_items") or []
    assert items
    text = str(items[0].get("text") or "")
    assert text or proactive_pitfall_message(
        str(items[0].get("pitfall_id")),
        source_language="python",
        target_language="pascal",
    )


def test_chapter2_slot_order_covers_all_patterns() -> None:
    assert len(CH2_SLOT_PATTERN_ORDER) == 8
    assert CH2_SLOT_PATTERN_ORDER[-1] == "task_016"


def test_chapter2_proactive_banners_no_verbatim_code() -> None:
    """Proactive MPLT banners for ch2 pitfalls must not embed code snippets."""
    ch2_pitfalls = [
        "assignment_vs_compare",
        "elif_chain",
        "chain_comparison",
        "input_line_model",
        "leap_year_mod",
        "pascal_case_labels",
        "switch_fallthrough",
        "mod_negative",
    ]
    code_markers = (":=", " mod ", "case 12", "in (12", "break;", "if 0 <=", "else if")
    for pattern in CH2_SLOT_PATTERN_ORDER[:-1]:
        ids = resolve_chapter2_proactive_pitfall_ids(
            pattern,
            source_language="python",
            target_language="pascal",
        )
        for pid in ids:
            if pid not in ch2_pitfalls:
                continue
            text = proactive_pitfall_message(
                pid,
                source_language="python",
                target_language="pascal",
            )
            assert text, pid
            lowered = text.lower()
            for marker in code_markers:
                assert marker.lower() not in lowered, f"{pid}: {marker!r} in {text[:120]}"


def test_chapter2_enrich_adds_elif_example() -> None:
    from application.curriculum.display.chapter2_branches_concept_examples import (
        enrich_chapter2_concept_cards,
    )
    from application.curriculum.validation.expected_concept_checker import (
        build_display_expected_concept_cards_for_pair,
    )

    cards = build_display_expected_concept_cards_for_pair(
        ["conditional", "multi_branch"],
        source_language="python",
        target_language="pascal",
        pitfall_ids=["elif_chain"],
    )
    enriched = enrich_chapter2_concept_cards(
        cards,
        pattern_key="task_010",
        pitfall_ids=["elif_chain"],
        source_language="python",
        target_language="pascal",
    )
    cond = next(c for c in enriched if c.get("id") == "tc_conditionals")
    py_examples = (cond.get("examples_by_language") or {}).get("python") or []
    pas_examples = (cond.get("examples_by_language") or {}).get("pascal") or []
    assert any("freezing" in str(row.get("code") or "") for row in py_examples)
    assert any("freezing" in str(row.get("code") or "") for row in pas_examples)


def test_chapter2_expected_concepts_unique_sets() -> None:
    from application.curriculum.display.chapter2_branches_expected_concepts import (
        CH2_EXPECTED_CONCEPTS,
    )
    from application.curriculum.validation.expected_concept_checker import (
        build_display_expected_concept_cards,
    )

    sets: dict[str, tuple[str, ...]] = {}
    for pattern, by_lang in CH2_EXPECTED_CONCEPTS.items():
        for lang, ids in by_lang.items():
            display = tuple(c["id"] for c in build_display_expected_concept_cards(ids))
            sets[f"{pattern}:{lang}"] = display

    unique = {v for v in sets.values()}
    assert len(sets) == 40
    # Distinct by dominant TC: switch (014), arith+branch (012/015/016), simple (009), multi-only (010/011/013)
    assert len(unique) >= 7, f"expected at least 7 unique display TC sets, got {len(unique)}"
    assert sets["task_014:pascal"] != sets["task_010:pascal"]
    assert "tc_switch_selection" in sets["task_014:pascal"]
    assert "tc_switch_selection" not in sets["task_010:pascal"]


def test_chapter2_all_tasks_have_hints() -> None:
    from application.curriculum.display.chapter2_branches_hints import (
        CHAPTER2_HINTS,
        chapter2_hints_for_pattern,
    )

    for pattern in CH2_SLOT_PATTERN_ORDER:
        hints = chapter2_hints_for_pattern(pattern)
        assert len(hints) >= 3, pattern
        assert pattern in CHAPTER2_HINTS
