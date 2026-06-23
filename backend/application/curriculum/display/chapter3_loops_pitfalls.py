"""MPLT pitfall bindings — chapter 3 loops (8 tasks × 5 languages).

Proactive banners on slots 1–7; slot 8 (capstone) has no proactive banners.
Pitfalls already proactive in chapters 1–2 are reactive-only here.
"""

from __future__ import annotations

from typing import Any

CH3_SLOT_PATTERN_ORDER: tuple[str, ...] = (
    "task_017",
    "task_018",
    "task_019",
    "task_020",
    "task_021",
    "task_022",
    "task_023",
    "task_024",
)

CHAPTER3_PATTERN_KEYS: frozenset[str] = frozenset(
    {
        "task_017",
        "task_018",
        "task_019",
        "task_020",
        "task_021",
        "task_022",
        "task_023",
        "task_024",
    }
)

_ASSIGNMENT_SOURCES: frozenset[str] = frozenset({"python", "cpp", "csharp", "java"})

# Re-export ch1 filter; extend with ch2-only proactive pitfalls.
from application.curriculum.display.chapter2_branches_pitfalls import (  # noqa: E402
    CHAPTER1_PROACTIVE_PITFALLS,
)

CHAPTER2_PROACTIVE_PITFALLS: frozenset[str] = frozenset(
    {
        "elif_chain",
        "chain_comparison",
        "leap_year_mod",
        "mod_negative",
        "pascal_case_labels",
        "switch_fallthrough",
        "and_or_keywords",
    }
)

PRIOR_PROACTIVE_PITFALLS: frozenset[str] = CHAPTER1_PROACTIVE_PITFALLS | CHAPTER2_PROACTIVE_PITFALLS


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


def _task_017_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("while_sentinel", source=source, target=target)


def _task_018_pitfalls(source: str, target: str) -> list[str]:
    ids = ["search_first_guard"]
    if target == "pascal":
        ids.append("index_1based")
    return _prep_banners(*ids, source=source, target=target)


def _task_019_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("yes_no_output", "mod_sqrt_loop", source=source, target=target)


def _task_020_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "filter_non_negative",
        "while_sentinel",
        "for_range_off_by_one",
        source=source,
        target=target,
    )


def _task_021_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "loop_upper_bound_n",
        "output_space_separated",
        source=source,
        target=target,
    )


def _task_022_pitfalls(source: str, target: str) -> list[str]:
    ids = ["search_last_overwrite"]
    if target == "pascal":
        ids.append("index_1based")
    return _prep_banners(*ids, source=source, target=target)


def _task_023_pitfalls(source: str, target: str) -> list[str]:
    ids = ["frequency_bucket"]
    if target == "pascal":
        ids.append("list_vs_static_array")
    return _prep_banners(*ids, source=source, target=target)


def _task_capstone_pitfalls(_source: str, _target: str) -> list[str]:
    return []


_TASK_RESOLVERS = {
    "task_017": _task_017_pitfalls,
    "task_018": _task_018_pitfalls,
    "task_019": _task_019_pitfalls,
    "task_020": _task_020_pitfalls,
    "task_021": _task_021_pitfalls,
    "task_022": _task_022_pitfalls,
    "task_023": _task_023_pitfalls,
    "task_024": _task_capstone_pitfalls,
}


def is_chapter3_pattern(pattern_key: str | None) -> bool:
    return str(pattern_key or "").strip() in CHAPTER3_PATTERN_KEYS


def resolve_chapter3_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """All pitfall ids for reactive «Перенос» on chapter-3 slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER3_PATTERN_KEYS:
        return []

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if not source or not target or source == target:
        return []

    resolver = _TASK_RESOLVERS.get(key)
    if resolver is None:
        return []

    return _filter_pair(resolver(source, target), source=source, target=target)


def resolve_chapter3_proactive_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """Proactive banners once per chapter slot; skip pitfalls from ch.1–2 and earlier ch.3 slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER3_PATTERN_KEYS or key == "task_024":
        return []

    try:
        slot_idx = CH3_SLOT_PATTERN_ORDER.index(key)
    except ValueError:
        return resolve_chapter3_pitfall_ids(
            key,
            source_language=source_language,
            target_language=target_language,
        )

    all_ids = resolve_chapter3_pitfall_ids(
        key,
        source_language=source_language,
        target_language=target_language,
    )
    shown: set[str] = set()
    for earlier in CH3_SLOT_PATTERN_ORDER[:slot_idx]:
        for pid in resolve_chapter3_pitfall_ids(
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


def primary_chapter3_pitfall_id(
    pattern_key: str | None,
    *,
    source_language: str = "python",
    target_language: str = "pascal",
) -> str | None:
    ids = resolve_chapter3_pitfall_ids(
        pattern_key,
        source_language=source_language,
        target_language=target_language,
    )
    return ids[0] if ids else None


def chapter3_binding_overrides() -> dict[str, dict[str, Any]]:
    """Default dominant pitfalls / debug ids for chapter-3 patterns."""
    return {
        "task_017": {
            "dominant_pitfall_id": "while_sentinel",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_018": {
            "dominant_pitfall_id": "search_first_guard",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_019": {
            "dominant_pitfall_id": "yes_no_output",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_020": {
            "dominant_pitfall_id": "filter_non_negative",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_021": {
            "dominant_pitfall_id": "loop_upper_bound_n",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_022": {
            "dominant_pitfall_id": "search_last_overwrite",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_023": {
            "dominant_pitfall_id": "frequency_bucket",
            "debug_id": None,
            "transfer_category": "AFCC",
        },
        "task_024": {
            "dominant_pitfall_id": None,
            "debug_id": None,
            "transfer_category": "TCC",
        },
    }
