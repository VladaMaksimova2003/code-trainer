"""MPLT pitfall bindings — chapter 4 arrays (8 tasks × 5 languages).

Proactive banners on slots 1–7; slot 8 (capstone task_032) has no proactive banners.
Pitfalls already proactive in chapters 1–3 are reactive-only here.
"""

from __future__ import annotations

from typing import Any

CH4_SLOT_PATTERN_ORDER: tuple[str, ...] = (
    "task_025",
    "task_026",
    "task_027",
    "task_028",
    "task_029",
    "task_030",
    "task_031",
    "task_032",
)

CHAPTER4_PATTERN_KEYS: frozenset[str] = frozenset(
    {
        "task_025",
        "task_026",
        "task_027",
        "task_028",
        "task_029",
        "task_030",
        "task_031",
        "task_032",
    }
)

_ASSIGNMENT_SOURCES: frozenset[str] = frozenset({"python", "cpp", "csharp", "java"})

from application.curriculum.display.chapter3_loops_pitfalls import (  # noqa: E402
    PRIOR_PROACTIVE_PITFALLS as _CH3_PRIOR,
)

CHAPTER3_PROACTIVE_PITFALLS: frozenset[str] = frozenset(
    {
        "while_sentinel",
        "search_first_guard",
        "search_last_overwrite",
        "yes_no_output",
        "mod_sqrt_loop",
        "filter_non_negative",
        "loop_upper_bound_n",
        "frequency_bucket",
        "list_vs_static_array",
    }
)

PRIOR_PROACTIVE_PITFALLS: frozenset[str] = _CH3_PRIOR | CHAPTER3_PROACTIVE_PITFALLS


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


def _task_025_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "array_reverse_order",
        "output_space_separated",
        source=source,
        target=target,
    )


def _task_026_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "cyclic_shift_mod_k",
        "input_line_model",
        source=source,
        target=target,
    )


def _task_027_pitfalls(source: str, target: str) -> list[str]:
    ids = ["array_delete_shift"]
    if target == "pascal":
        ids.extend(["list_vs_static_array", "index_1based"])
    return _prep_banners(*ids, source=source, target=target)


def _task_028_pitfalls(source: str, target: str) -> list[str]:
    ids = ["array_insert_shift", "index_1based"]
    return _prep_banners(*ids, source=source, target=target)


def _task_029_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "dual_array_concat",
        "input_line_model",
        "output_space_separated",
        source=source,
        target=target,
    )


def _task_030_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "duplicate_pair_loop",
        "yes_no_output",
        source=source,
        target=target,
    )


def _task_031_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "merge_sorted_two_ptr",
        "input_line_model",
        "output_space_separated",
        source=source,
        target=target,
    )


def _task_capstone_pitfalls(source: str, target: str) -> list[str]:
    ids = ["sorted_insert_pos"]
    if target == "pascal":
        ids.append("index_1based")
    return _prep_banners(*ids, source=source, target=target)


_TASK_RESOLVERS = {
    "task_025": _task_025_pitfalls,
    "task_026": _task_026_pitfalls,
    "task_027": _task_027_pitfalls,
    "task_028": _task_028_pitfalls,
    "task_029": _task_029_pitfalls,
    "task_030": _task_030_pitfalls,
    "task_031": _task_031_pitfalls,
    "task_032": _task_capstone_pitfalls,
}


def is_chapter4_pattern(pattern_key: str | None) -> bool:
    return str(pattern_key or "").strip() in CHAPTER4_PATTERN_KEYS


def resolve_chapter4_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """All pitfall ids for reactive «Перенос» on chapter-4 slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER4_PATTERN_KEYS:
        return []

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if not source or not target or source == target:
        return []

    resolver = _TASK_RESOLVERS.get(key)
    if resolver is None:
        return []

    return _filter_pair(resolver(source, target), source=source, target=target)


def resolve_chapter4_proactive_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """Proactive banners once per chapter slot; skip pitfalls from ch.1–3 and earlier ch.4 slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER4_PATTERN_KEYS or key == "task_032":
        return []

    try:
        slot_idx = CH4_SLOT_PATTERN_ORDER.index(key)
    except ValueError:
        return resolve_chapter4_pitfall_ids(
            key,
            source_language=source_language,
            target_language=target_language,
        )

    all_ids = resolve_chapter4_pitfall_ids(
        key,
        source_language=source_language,
        target_language=target_language,
    )
    shown: set[str] = set()
    for earlier in CH4_SLOT_PATTERN_ORDER[:slot_idx]:
        for pid in resolve_chapter4_pitfall_ids(
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


def primary_chapter4_pitfall_id(
    pattern_key: str | None,
    *,
    source_language: str = "python",
    target_language: str = "pascal",
) -> str | None:
    ids = resolve_chapter4_pitfall_ids(
        pattern_key,
        source_language=source_language,
        target_language=target_language,
    )
    return ids[0] if ids else None


def chapter4_binding_overrides() -> dict[str, dict[str, Any]]:
    """Default dominant pitfalls / debug ids for chapter-4 patterns."""
    return {
        "task_025": {
            "dominant_pitfall_id": "array_reverse_order",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_026": {
            "dominant_pitfall_id": "cyclic_shift_mod_k",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_027": {
            "dominant_pitfall_id": "array_delete_shift",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_028": {
            "dominant_pitfall_id": "array_insert_shift",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_029": {
            "dominant_pitfall_id": "dual_array_concat",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_030": {
            "dominant_pitfall_id": "duplicate_pair_loop",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_031": {
            "dominant_pitfall_id": "merge_sorted_two_ptr",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_032": {
            "dominant_pitfall_id": None,
            "debug_id": None,
            "transfer_category": "TCC",
        },
    }
