"""Chapter 5 strings: per-task × per-language-pair pitfall bindings."""

from __future__ import annotations

import pytest

from application.curriculum.content.algo_syntax_showcase_meta import (
    transfer_meta_for_language_pair,
)
from application.curriculum.display.chapter5_strings_hints import (
    CHAPTER5_HINTS,
    chapter5_hints_for_pattern,
)
from application.curriculum.display.chapter5_strings_pitfalls import (
    CH5_SLOT_PATTERN_ORDER,
    PRIOR_PROACTIVE_PITFALLS,
    resolve_chapter5_pitfall_ids,
    resolve_chapter5_proactive_pitfall_ids,
)
from application.curriculum.display.pitfall_messages import proactive_pitfall_message


@pytest.mark.parametrize(
    ("pattern", "source", "target", "expected_subset"),
    [
        ("task_033", "python", "pascal", ["string_length_builtin"]),
        ("task_034", "python", "pascal", ["string_reverse_chars"]),
        ("task_035", "python", "pascal", ["palindrome_symmetry"]),
        ("task_036", "python", "pascal", ["substring_first_1based"]),
        ("task_037", "python", "pascal", ["word_split_spaces"]),
        ("task_038", "python", "pascal", ["anagram_letter_freq"]),
        ("task_039", "python", "pascal", ["rle_run_encoding"]),
        ("task_040", "python", "pascal", ["text_stats_vowels"]),
    ],
)
def test_chapter5_reactive_pitfalls(
    pattern: str,
    source: str,
    target: str,
    expected_subset: list[str],
) -> None:
    ids = resolve_chapter5_pitfall_ids(
        pattern,
        source_language=source,
        target_language=target,
    )
    for pid in expected_subset:
        assert pid in ids


def test_chapter5_proactive_skips_prior_chapters() -> None:
    first = resolve_chapter5_proactive_pitfall_ids(
        "task_033",
        source_language="python",
        target_language="pascal",
    )
    assert "string_length_builtin" in first
    for pid in first:
        assert pid not in PRIOR_PROACTIVE_PITFALLS


def test_chapter5_proactive_dedup_within_chapter() -> None:
    proactive_037 = resolve_chapter5_proactive_pitfall_ids(
        "task_037",
        source_language="python",
        target_language="pascal",
    )
    assert "string_length_builtin" not in proactive_037
    assert "word_split_spaces" in proactive_037


def test_chapter5_capstone_no_proactive() -> None:
    assert (
        resolve_chapter5_proactive_pitfall_ids(
            "task_040",
            source_language="python",
            target_language="pascal",
        )
        == []
    )


def test_chapter5_transfer_meta_has_proactive_items() -> None:
    meta = transfer_meta_for_language_pair(
        "task_036",
        source_language="python",
        target_language="pascal",
    )
    items = meta.get("proactive_items") or []
    assert items
    assert items[0].get("pitfall_id") == "substring_first_1based"


def test_chapter5_slot_order_covers_all_patterns() -> None:
    assert len(CH5_SLOT_PATTERN_ORDER) == 8
    assert CH5_SLOT_PATTERN_ORDER[-1] == "task_040"


def test_chapter5_proactive_banners_no_verbatim_code() -> None:
    ch5_pitfalls = [
        "string_length_builtin",
        "string_reverse_chars",
        "palindrome_symmetry",
        "substring_first_1based",
        "word_split_spaces",
        "anagram_letter_freq",
        "rle_run_encoding",
        "text_stats_vowels",
    ]
    code_markers = (":=", "len(s)", "find(", "[::-1]", "split(", "a3b2")
    for pattern in CH5_SLOT_PATTERN_ORDER[:-1]:
        ids = resolve_chapter5_proactive_pitfall_ids(
            pattern,
            source_language="python",
            target_language="pascal",
        )
        for pid in ids:
            if pid not in ch5_pitfalls:
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


def test_chapter5_all_tasks_have_hints() -> None:
    for pattern in CH5_SLOT_PATTERN_ORDER:
        hints = chapter5_hints_for_pattern(pattern)
        assert len(hints) >= 3, pattern
        assert pattern in CHAPTER5_HINTS
