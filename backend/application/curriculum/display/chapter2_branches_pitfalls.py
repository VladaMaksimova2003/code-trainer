"""MPLT pitfall bindings — chapter 2 branches (8 tasks × 5 languages).

Proactive banners on slots 1–7; slot 8 (capstone) has no proactive banners.
AlgorithmDebug (branch_logic, multi_branch_discount) stays reactive-only in «Ошибки».
"""

from __future__ import annotations

from typing import Any

# Pedagogical order (may differ from task_num 9–16 in catalog).
CH2_SLOT_PATTERN_ORDER: tuple[str, ...] = (
    "task_009",
    "task_010",
    "task_013",
    "task_011",
    "task_012",
    "task_014",
    "task_015",
    "task_016",
)

CHAPTER2_PATTERN_KEYS: frozenset[str] = frozenset(
    {
        "task_009",
        "task_010",
        "task_011",
        "task_012",
        "task_013",
        "task_014",
        "task_015",
        "task_016",
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


# Pitfalls already shown proactively in chapter 1 — do not repeat in chapter 2 banners.
CHAPTER1_PROACTIVE_PITFALLS: frozenset[str] = frozenset(
    {
        "for_range_off_by_one",
        "integer_division",
        "index_1based",
        "input_line_model",
        "output_space_separated",
        "assignment_vs_compare",
    }
)


def _task_max_three_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("assignment_vs_compare", source=source, target=target)


def _task_temperature_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners("elif_chain", source=source, target=target)


def _task_grades_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "chain_comparison",
        "elif_chain",
        source=source,
        target=target,
    )


def _task_triangle_pitfalls(source: str, target: str) -> list[str]:
    ids = ["elif_chain"]
    if source == "python" and target in {"cpp", "csharp", "java"}:
        ids.append("and_or_keywords")
    return _prep_banners(*ids, source=source, target=target)


def _task_date_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "input_line_model",
        "leap_year_mod",
        "mod_negative",
        source=source,
        target=target,
    )


def _task_season_pitfalls(source: str, target: str) -> list[str]:
    ids = ["pascal_case_labels"]
    if target in {"cpp", "csharp"}:
        ids.append("switch_fallthrough")
    if source == "python" and target == "python":
        ids = []
    return _prep_banners(*ids, source=source, target=target)


def _task_discount_pitfalls(source: str, target: str) -> list[str]:
    return _prep_banners(
        "elif_chain",
        "chain_comparison",
        source=source,
        target=target,
    )


def _task_capstone_pitfalls(_source: str, _target: str) -> list[str]:
    return []


_TASK_RESOLVERS = {
    "task_009": _task_max_three_pitfalls,
    "task_010": _task_temperature_pitfalls,
    "task_011": _task_triangle_pitfalls,
    "task_012": _task_date_pitfalls,
    "task_013": _task_grades_pitfalls,
    "task_014": _task_season_pitfalls,
    "task_015": _task_discount_pitfalls,
    "task_016": _task_capstone_pitfalls,
}


def is_chapter2_pattern(pattern_key: str | None) -> bool:
    return str(pattern_key or "").strip() in CHAPTER2_PATTERN_KEYS


def resolve_chapter2_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """All pitfall ids for reactive «Перенос» on chapter-2 slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER2_PATTERN_KEYS:
        return []

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if not source or not target or source == target:
        return []

    resolver = _TASK_RESOLVERS.get(key)
    if resolver is None:
        return []

    return _filter_pair(resolver(source, target), source=source, target=target)


def resolve_chapter2_proactive_pitfall_ids(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> list[str]:
    """Proactive banners once per chapter slot; skip pitfalls taught on earlier slots."""
    key = str(pattern_key or "").strip()
    if key not in CHAPTER2_PATTERN_KEYS or key == "task_016":
        return []

    try:
        slot_idx = CH2_SLOT_PATTERN_ORDER.index(key)
    except ValueError:
        return resolve_chapter2_pitfall_ids(
            key,
            source_language=source_language,
            target_language=target_language,
        )

    all_ids = resolve_chapter2_pitfall_ids(
        key,
        source_language=source_language,
        target_language=target_language,
    )
    shown: set[str] = set()
    for earlier in CH2_SLOT_PATTERN_ORDER[:slot_idx]:
        for pid in resolve_chapter2_pitfall_ids(
            earlier,
            source_language=source_language,
            target_language=target_language,
        ):
            shown.add(pid)
    return [pid for pid in all_ids if pid not in shown and pid not in CHAPTER1_PROACTIVE_PITFALLS]


def primary_chapter2_pitfall_id(
    pattern_key: str | None,
    *,
    source_language: str = "python",
    target_language: str = "pascal",
) -> str | None:
    ids = resolve_chapter2_pitfall_ids(
        pattern_key,
        source_language=source_language,
        target_language=target_language,
    )
    return ids[0] if ids else None


def chapter2_binding_overrides() -> dict[str, dict[str, Any]]:
    """Default dominant pitfalls / debug ids for chapter-2 patterns."""
    return {
        "task_009": {
            "dominant_pitfall_id": "assignment_vs_compare",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_010": {
            "dominant_pitfall_id": "elif_chain",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_011": {
            "dominant_pitfall_id": "elif_chain",
            "debug_id": "branch_logic",
            "transfer_category": "TCC",
        },
        "task_012": {
            "dominant_pitfall_id": "leap_year_mod",
            "debug_id": "branch_logic",
            "transfer_category": "AFCC",
        },
        "task_013": {
            "dominant_pitfall_id": "chain_comparison",
            "debug_id": None,
            "transfer_category": "FCC",
        },
        "task_014": {
            "dominant_pitfall_id": "pascal_case_labels",
            "debug_id": None,
            "transfer_category": "ATCC",
        },
        "task_015": {
            "dominant_pitfall_id": "elif_chain",
            "debug_id": "multi_branch_discount",
            "transfer_category": "TCC",
        },
        "task_016": {
            "dominant_pitfall_id": None,
            "debug_id": None,
            "transfer_category": "TCC",
        },
    }
