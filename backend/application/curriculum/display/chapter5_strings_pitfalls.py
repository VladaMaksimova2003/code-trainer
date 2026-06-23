"""MPLT pitfall bindings — chapter 5 strings (8 tasks × 5 languages).

Proactive banners on slots 1–7; slot 8 (capstone task_040) has no proactive banners.
Pitfalls already proactive in chapters 1–4 are reactive-only here.
"""

from __future__ import annotations

from typing import Any

CH5_SLOT_PATTERN_ORDER: tuple[str, ...] = (
    "task_033",
    "task_034",
    "task_035",
    "task_036",
    "task_037",
    "task_038",
    "task_039",
    "task_040",
)

CHAPTER5_PATTERN_KEYS: frozenset[str] = frozenset(
    {
        "task_033",
        "task_034",
        "task_035",
        "task_036",
        "task_037",
        "task_038",
        "task_039",
        "task_040",
    }
)

_ASSIGNMENT_SOURCES: frozenset[str] = frozenset({"python", "cpp", "csharp", "java"})

from application.curriculum.display.chapter4_arrays_pitfalls import (  # noqa: E402
    PRIOR_PROACTIVE_PITFALLS as _CH4_PRIOR,
)

CHAPTER4_PROACTIVE_PITFALLS: frozenset[str] = frozenset(
    {
        "array_reverse_order",
        "cyclic_shift_mod_k",
        "array_delete_shift",
        "array_insert_shift",
        "dual_array_concat",
        "duplicate_pair_loop",
        "merge_sorted_two_ptr",
        "sorted_insert_pos",
    }
)

PRIOR_PROACTIVE_PITFALLS: frozenset[str] = _CH4_PRIOR | CHAPTER4_PROACTIVE_PITFALLS


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _filter_pair(pitfall_ids: list[str], *, source: str, target: str) -> list[str]:
    from application.curriculum.display.pitfall_catalog import (
        get_pitfall,
        pitfall_applies_to_language_pair,
    )

    out: list[str] = []
    seen: set[str] = set()
    for pid in pitfall_ids:
        key = str(pid or "").strip()
        if not key or key in seen:
            continue
        spec = get_pitfall(key)
        if not spec:
            continue
        if not pitfall_applies_to_language_pair(
            spec,
            source_language=source,
            target_language=target,
        ):
            continue
        seen.add(key)
        out.append(key)
    return out


def _maybe_assignment(source: str, target: str) -> list[str]:
    if target == "pascal" and source in _ASSIGNMENT_SOURCES:
        return ["assignment_vs_compare"]
    return []


def _prep_banners(*ids: str, source: str, target: str) -> list[str]:
    ordered = list(ids)
    ordered.extend(_maybe_assignment(source, target))
    return ordered


def _task_033_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("string_length_builtin", source=source, target=target)


def _task_034_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("string_reverse_chars", source=source, target=target)


def _task_035_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "palindrome_symmetry",
        "yes_no_output",
        source=source,
        target=target,
    )


def _task_036_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("substring_first_1based", source=source, target=target)


def _task_037_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("word_split_spaces", source=source, target=target)


def _task_038_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "anagram_letter_freq",
        "yes_no_output",
        source=source,
        target=target,
    )


def _task_039_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("rle_run_encoding", source=source, target=target)


def _task_capstone_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "text_stats_vowels",
        "word_split_spaces",
        "string_length_builtin",
        source=source,
        target=target,
    )


_TASK_RESOLVERS = {
    "task_033": _task_033_pitfalls,
    "task_034": _task_034_pitfalls,
    "task_035": _task_035_pitfalls,
    "task_036": _task_036_pitfalls,
    "task_037": _task_037_pitfalls,
    "task_038": _task_038_pitfalls,
    "task_039": _task_039_pitfalls,
    "task_040": _task_capstone_pitfalls,
}


def is_chapter5_pattern(pattern_key: str | None) -> bool:
    return str(pattern_key or "").strip() in CHAPTER5_PATTERN_KEYS


def resolve_chapter5_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """All pitfall ids for reactive «Перенос» on chapter-5 slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER5_PATTERN_KEYS:
        return []

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if not source or not target or source == target:
        return []

    resolver = _TASK_RESOLVERS.get(key)
    if resolver is None:
        return []

    return _filter_pair(resolver(source, target), source=source, target=target)


def resolve_chapter5_proactive_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """Proactive banners once per chapter slot; skip pitfalls from ch.1–4 and earlier ch.5 slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER5_PATTERN_KEYS or key == "task_040":
        return []

    try:
        slot_idx = CH5_SLOT_PATTERN_ORDER.index(key)
    except ValueError:
        return resolve_chapter5_pitfall_ids(
            key,
            source_language=source_language,
            target_language=target_language,
        )

    all_ids = resolve_chapter5_pitfall_ids(
        key,
        source_language=source_language,
        target_language=target_language,
    )
    shown: set[str] = set()
    for earlier in CH5_SLOT_PATTERN_ORDER[:slot_idx]:
        for pid in resolve_chapter5_pitfall_ids(
            earlier,
            source_language=source_language,
            target_language=target_language,
        ):
            shown.add(pid)
    return [
        pid
        for pid in all_ids
        if pid not in shown and pid not in PRIOR_PROACTIVE_PITFALLS
    ]


def primary_chapter5_pitfall_id(
    pattern_key: str | None,
    *,
    source_language: str = "python",
    target_language: str = "pascal",
) -> str | None:
    ids = resolve_chapter5_pitfall_ids(
        pattern_key,
        source_language=source_language,
        target_language=target_language,
    )
    return ids[0] if ids else None


def chapter5_binding_overrides() -> dict[str, dict[str, Any]]:
    """Default dominant pitfalls / debug ids for chapter-5 patterns."""
    return {
        "task_033": {
            "dominant_pitfall_id": "string_length_builtin",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_034": {
            "dominant_pitfall_id": "string_reverse_chars",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_035": {
            "dominant_pitfall_id": "palindrome_symmetry",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_036": {
            "dominant_pitfall_id": "substring_first_1based",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_037": {
            "dominant_pitfall_id": "word_split_spaces",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_038": {
            "dominant_pitfall_id": "anagram_letter_freq",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_039": {
            "dominant_pitfall_id": "rle_run_encoding",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_040": {
            "dominant_pitfall_id": None,
            "debug_id": None,
            "transfer_category": "TCC",
        },
    }
