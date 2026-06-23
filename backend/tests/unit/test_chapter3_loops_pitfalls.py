"""Chapter 3 loops: per-task × per-language-pair pitfall bindings."""

from __future__ import annotations

import pytest

from application.curriculum.content.algo_syntax_showcase_meta import (
    transfer_meta_for_language_pair,
)
from application.curriculum.display.chapter3_loops_hints import (
    CHAPTER3_HINTS,
    chapter3_hints_for_pattern,
)
from application.curriculum.display.chapter3_loops_pitfalls import (
    CH3_SLOT_PATTERN_ORDER,
    PRIOR_PROACTIVE_PITFALLS,
    resolve_chapter3_pitfall_ids,
    resolve_chapter3_proactive_pitfall_ids,
)
from application.curriculum.display.pitfall_messages import proactive_pitfall_message


@pytest.mark.parametrize(
    ("pattern", "source", "target", "expected_subset"),
    [
        ("task_017", "python", "pascal", ["while_sentinel"]),
        ("task_018", "python", "pascal", ["search_first_guard"]),
        ("task_019", "python", "pascal", ["yes_no_output"]),
        ("task_020", "python", "pascal", ["filter_non_negative"]),
        ("task_021", "python", "pascal", ["loop_upper_bound_n"]),
        ("task_022", "python", "pascal", ["search_last_overwrite"]),
        ("task_023", "python", "pascal", ["frequency_bucket"]),
        ("task_024", "python", "pascal", []),
    ],
)
def test_chapter3_reactive_pitfalls(
    pattern: str,
    source: str,
    target: str,
    expected_subset: list[str],
) -> None:
    ids = resolve_chapter3_pitfall_ids(
        pattern,
        source_language=source,
        target_language=target,
    )
    for pid in expected_subset:
        assert pid in ids


def test_chapter3_proactive_skips_prior_chapters() -> None:
    first = resolve_chapter3_proactive_pitfall_ids(
        "task_017",
        source_language="python",
        target_language="pascal",
    )
    assert "while_sentinel" in first
    for pid in first:
        assert pid not in PRIOR_PROACTIVE_PITFALLS

    second = resolve_chapter3_proactive_pitfall_ids(
        "task_018",
        source_language="python",
        target_language="pascal",
    )
    assert "index_1based" not in second or "search_first_guard" in second


def test_chapter3_proactive_dedup_within_chapter() -> None:
    """while_sentinel taught on 017 — not proactive again on 020."""
    proactive_020 = resolve_chapter3_proactive_pitfall_ids(
        "task_020",
        source_language="python",
        target_language="pascal",
    )
    assert "while_sentinel" not in proactive_020
    assert "filter_non_negative" in proactive_020


def test_chapter3_capstone_no_proactive() -> None:
    assert (
        resolve_chapter3_proactive_pitfall_ids(
            "task_024",
            source_language="python",
            target_language="pascal",
        )
        == []
    )


def test_chapter3_transfer_meta_has_proactive_items() -> None:
    meta = transfer_meta_for_language_pair(
        "task_019",
        source_language="python",
        target_language="pascal",
    )
    items = meta.get("proactive_items") or []
    assert items
    assert items[0].get("pitfall_id") == "yes_no_output"


def test_chapter3_slot_order_covers_all_patterns() -> None:
    assert len(CH3_SLOT_PATTERN_ORDER) == 8
    assert CH3_SLOT_PATTERN_ORDER[-1] == "task_024"


def test_chapter3_proactive_banners_no_verbatim_code() -> None:
    ch3_pitfalls = [
        "while_sentinel",
        "search_first_guard",
        "search_last_overwrite",
        "yes_no_output",
        "mod_sqrt_loop",
        "filter_non_negative",
        "loop_upper_bound_n",
        "frequency_bucket",
    ]
    code_markers = (":=", " mod ", "while x <>", "range(1,", "freq[x]", "prime/composite")
    for pattern in CH3_SLOT_PATTERN_ORDER[:-1]:
        ids = resolve_chapter3_proactive_pitfall_ids(
            pattern,
            source_language="python",
            target_language="pascal",
        )
        for pid in ids:
            if pid not in ch3_pitfalls:
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


def test_chapter3_all_tasks_have_hints() -> None:
    for pattern in CH3_SLOT_PATTERN_ORDER:
        hints = chapter3_hints_for_pattern(pattern)
        assert len(hints) >= 3, pattern
        assert pattern in CHAPTER3_HINTS
