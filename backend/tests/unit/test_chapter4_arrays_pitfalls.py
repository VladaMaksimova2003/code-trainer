"""Chapter 4 arrays: per-task × per-language-pair pitfall bindings."""

from __future__ import annotations

import pytest

from application.curriculum.content.algo_syntax_showcase_meta import (
    transfer_meta_for_language_pair,
)
from application.curriculum.display.chapter4_arrays_hints import (
    CHAPTER4_HINTS,
    chapter4_hints_for_pattern,
)
from application.curriculum.display.chapter4_arrays_pitfalls import (
    CH4_SLOT_PATTERN_ORDER,
    PRIOR_PROACTIVE_PITFALLS,
    resolve_chapter4_pitfall_ids,
    resolve_chapter4_proactive_pitfall_ids,
)
from application.curriculum.display.pitfall_messages import proactive_pitfall_message


@pytest.mark.parametrize(
    ("pattern", "source", "target", "expected_subset"),
    [
        ("task_025", "python", "pascal", ["array_reverse_order"]),
        ("task_026", "python", "pascal", ["cyclic_shift_mod_k"]),
        ("task_027", "python", "pascal", ["array_delete_shift"]),
        ("task_028", "python", "pascal", ["array_insert_shift"]),
        ("task_029", "python", "pascal", ["dual_array_concat"]),
        ("task_030", "python", "pascal", ["duplicate_pair_loop"]),
        ("task_031", "python", "pascal", ["merge_sorted_two_ptr"]),
        ("task_032", "python", "pascal", ["sorted_insert_pos"]),
    ],
)
def test_chapter4_reactive_pitfalls(
    pattern: str,
    source: str,
    target: str,
    expected_subset: list[str],
) -> None:
    ids = resolve_chapter4_pitfall_ids(
        pattern,
        source_language=source,
        target_language=target,
    )
    for pid in expected_subset:
        assert pid in ids


def test_chapter4_proactive_skips_prior_chapters() -> None:
    first = resolve_chapter4_proactive_pitfall_ids(
        "task_025",
        source_language="python",
        target_language="pascal",
    )
    assert "array_reverse_order" in first
    for pid in first:
        assert pid not in PRIOR_PROACTIVE_PITFALLS


def test_chapter4_proactive_dedup_within_chapter() -> None:
    """array_reverse_order on 025 — not proactive again on later slots."""
    proactive_029 = resolve_chapter4_proactive_pitfall_ids(
        "task_029",
        source_language="python",
        target_language="pascal",
    )
    assert "array_reverse_order" not in proactive_029
    assert "dual_array_concat" in proactive_029


def test_chapter4_capstone_no_proactive() -> None:
    assert (
        resolve_chapter4_proactive_pitfall_ids(
            "task_032",
            source_language="python",
            target_language="pascal",
        )
        == []
    )


def test_chapter4_transfer_meta_has_proactive_items() -> None:
    meta = transfer_meta_for_language_pair(
        "task_026",
        source_language="python",
        target_language="pascal",
    )
    items = meta.get("proactive_items") or []
    assert items
    assert items[0].get("pitfall_id") == "cyclic_shift_mod_k"


def test_chapter4_slot_order_covers_all_patterns() -> None:
    assert len(CH4_SLOT_PATTERN_ORDER) == 8
    assert CH4_SLOT_PATTERN_ORDER[-1] == "task_032"


def test_chapter4_proactive_banners_no_verbatim_code() -> None:
    ch4_pitfalls = [
        "array_reverse_order",
        "cyclic_shift_mod_k",
        "array_delete_shift",
        "array_insert_shift",
        "dual_array_concat",
        "duplicate_pair_loop",
        "merge_sorted_two_ptr",
        "sorted_insert_pos",
    ]
    code_markers = (":=", " mod ", "a[0]", "insert(", "del a", "yes/no")
    for pattern in CH4_SLOT_PATTERN_ORDER[:-1]:
        ids = resolve_chapter4_proactive_pitfall_ids(
            pattern,
            source_language="python",
            target_language="pascal",
        )
        for pid in ids:
            if pid not in ch4_pitfalls:
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


def test_chapter4_all_tasks_have_hints() -> None:
    for pattern in CH4_SLOT_PATTERN_ORDER:
        hints = chapter4_hints_for_pattern(pattern)
        assert len(hints) >= 3, pattern
        assert pattern in CHAPTER4_HINTS
