"""MPLT pitfall bindings — chapter 1 algo_basics (8 tasks × 5 languages).

Banners teach on slots 1–7; slot 8 (capstone) has no proactive banners.
"""

from __future__ import annotations

from typing import Any

CH1_SLOT_PATTERN_ORDER: tuple[str, ...] = (
    "task_002",
    "task_005",
    "task_006",
    "task_001",
    "task_004",
    "task_007",
    "task_129",
    "task_008",
)

CHAPTER1_PATTERN_KEYS: frozenset[str] = frozenset(
    {
        "task_001",
        "task_002",
        "task_004",
        "task_005",
        "task_006",
        "task_007",
        "task_008",
        "task_129",
    }
)

_COURSE_LANGS: tuple[str, ...] = ("python", "pascal", "cpp", "csharp", "java")
_ASSIGNMENT_SOURCES: frozenset[str] = frozenset({"python", "cpp", "csharp", "java"})


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


def _task_002_pitfalls(source: str, target: str) -> list[str]:
    """Linear search — input line, 1-based index, comparison."""
    ids = ["input_line_model"]
    if target == "pascal":
        ids.append("index_1based")
    return _prep_banners(*ids, source=source, target=target)


def _task_loop_pitfalls(source: str, target: str) -> list[str]:
    """Counted loop + spaced output prep for capstone."""
    return _prep_banners(
        "for_range_off_by_one",
        "input_line_model",
        source=source,
        target=target,
    )


def _task_max_pitfalls(source: str, target: str) -> list[str]:
    """Max in array — loop + input."""
    return _prep_banners(
        "for_range_off_by_one",
        "input_line_model",
        source=source,
        target=target,
    )


def _task_div_pitfalls(source: str, target: str) -> list[str]:
    """Integer average — division + loop recap."""
    return _prep_banners(
        "integer_division",
        "for_range_off_by_one",
        source=source,
        target=target,
    )


def _task_filter_debug_pitfalls(source: str, target: str) -> list[str]:
    """Debug: count positives — loop, input, assignment."""
    return _prep_banners(
        "for_range_off_by_one",
        "input_line_model",
        source=source,
        target=target,
    )


def _task_threshold_debug_pitfalls(source: str, target: str) -> list[str]:
    """Debug: threshold count — loop + capstone output format."""
    return _prep_banners(
        "for_range_off_by_one",
        "output_space_separated",
        "input_line_model",
        source=source,
        target=target,
    )


def _task_digit_sum_pitfalls(source: str, target: str) -> list[str]:
    """Sum of digits — div/mod recap + loop."""
    return _prep_banners(
        "integer_division",
        "for_range_off_by_one",
        source=source,
        target=target,
    )


def _task_capstone_pitfalls(_source: str, _target: str) -> list[str]:
    """Final assessment — no proactive banners (skills taught on slots 1–7)."""
    return []


_TASK_RESOLVERS = {
    "task_001": _task_max_pitfalls,
    "task_002": _task_002_pitfalls,
    "task_004": _task_filter_debug_pitfalls,
    "task_005": _task_loop_pitfalls,
    "task_006": _task_div_pitfalls,
    "task_007": _task_threshold_debug_pitfalls,
    "task_008": _task_capstone_pitfalls,
    "task_129": _task_digit_sum_pitfalls,
}


def is_chapter1_pattern(pattern_key: str | None) -> bool:
    return str(pattern_key or "").strip() in CHAPTER1_PATTERN_KEYS


def resolve_chapter1_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """Ordered pitfall ids for algo_basics chapter-1 slot pattern."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER1_PATTERN_KEYS:
        return []

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if not source or not target or source == target:
        return []

    resolver = _TASK_RESOLVERS.get(key)
    if resolver is None:
        return []

    return _filter_pair(resolver(source, target), source=source, target=target)


def resolve_chapter1_proactive_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """Banners shown once per chapter slot; pitfalls repeat only in reactive «Перенос» warnings."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER1_PATTERN_KEYS or key == "task_008":
        return []

    try:
        slot_idx = CH1_SLOT_PATTERN_ORDER.index(key)
    except ValueError:
        return resolve_chapter1_pitfall_ids(
            key,
            source_language=source_language,
            target_language=target_language,
        )

    all_ids = resolve_chapter1_pitfall_ids(
        key,
        source_language=source_language,
        target_language=target_language,
    )
    shown: set[str] = set()
    for earlier in CH1_SLOT_PATTERN_ORDER[:slot_idx]:
        for pid in resolve_chapter1_pitfall_ids(
            earlier,
            source_language=source_language,
            target_language=target_language,
        ):
            shown.add(pid)
    return [pid for pid in all_ids if pid not in shown]


def primary_chapter1_pitfall_id(
    pattern_key: str | None,
    *,
    source_language: str = "python",
    target_language: str = "pascal",
) -> str | None:
    ids = resolve_chapter1_pitfall_ids(
        pattern_key,
        source_language=source_language,
        target_language=target_language,
    )
    return ids[0] if ids else None


def chapter1_binding_overrides() -> dict[str, dict[str, Any]]:
    """Default dominant pitfalls for chapter-1 patterns (scripts / legacy readers)."""
    return {
        "task_001": {
            "dominant_pitfall_id": "for_range_off_by_one",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_002": {
            "dominant_pitfall_id": "input_line_model",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_004": {
            "dominant_pitfall_id": "for_range_off_by_one",
            "debug_id": "filter_positive",
            "transfer_category": "TCC",
        },
        "task_005": {
            "dominant_pitfall_id": "for_range_off_by_one",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_006": {
            "dominant_pitfall_id": "integer_division",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_007": {
            "dominant_pitfall_id": "for_range_off_by_one",
            "debug_id": "threshold_count",
            "transfer_category": "TCC",
        },
        "task_008": {
            "dominant_pitfall_id": None,
            "debug_id": None,
            "transfer_category": "TCC",
        },
    }
