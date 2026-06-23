"""Per-language expected concepts and MPLT transfer meta for algorithm-syntax tasks."""

from __future__ import annotations

from typing import Any

AUTHORING_LANGS: tuple[str, ...] = ("pascal", "python", "cpp", "csharp", "java")

ProactiveZone = str | None


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _empty_proactive() -> dict[str, Any]:
    return {"zone": None, "text": None, "concept_ids": []}


def _merge_algorithm_debug_meta(result: dict[str, Any], base: dict[str, Any]) -> None:
    """Attach AlgorithmDebug catalog for reactive submit feedback (not proactive banner)."""
    debug_id = base.get("debug_id")
    debug_meta = base.get("debug_meta")
    if not debug_id or not isinstance(debug_meta, dict):
        return
    result["debug_meta"] = dict(debug_meta)
    pedagogy = str(debug_meta.get("pedagogy_note_ru") or "").strip()
    if pedagogy:
        result["algorithm_pedagogy_note_ru"] = pedagogy


def proactive_zone_for_transfer_type(transfer_type: str | None) -> ProactiveZone:
    tt = str(transfer_type or "").strip().upper()
    if tt == "FCC":
        return "lexeme"
    if tt == "ATCC":
        return "idiom"
    if tt == "AFCC":
        return "model"
    return None


def resolve_pattern_key(
    slot_id: str | None,
    *,
    slot_pattern_id: str | None = None,
    exercise_pattern_id: str | None = None,
) -> str | None:
    from application.curriculum.content.algo_syntax_task_extra import resolve_slot_pattern_key

    pat = str(exercise_pattern_id or slot_pattern_id or "").strip() or None
    return resolve_slot_pattern_key(slot_id, slot_pattern_id=pat)


def expected_concept_ids_by_language(
    slot_id: str,
    *,
    slot_pattern_id: str | None = None,
) -> dict[str, list[str]]:
    """Technical concept ids per authoring language from ALGO_SYNTAX_META."""
    from application.curriculum.content.algo_syntax_task_extra import algo_expected_concepts

    out: dict[str, list[str]] = {}
    for lang in AUTHORING_LANGS:
        ids = algo_expected_concepts(slot_id, lang, slot_pattern_id=slot_pattern_id)
        if ids:
            out[lang] = ids
    return out


def attach_expected_concepts_to_extra(
    extra: dict[str, Any],
    *,
    slot_id: str,
    slot_pattern_id: str | None,
) -> dict[str, Any]:
    """Fill expected_concept_ids + expected_concepts (per lang) on catalog extra."""
    by_lang = expected_concept_ids_by_language(slot_id, slot_pattern_id=slot_pattern_id)
    if not by_lang:
        return extra

    extra = dict(extra)
    extra["slot_pattern_id"] = slot_pattern_id or extra.get("slot_pattern_id")
    extra["expected_concepts"] = by_lang
    primary = by_lang.get("pascal") or by_lang.get("python") or next(iter(by_lang.values()))
    extra["expected_concept_ids"] = list(primary)
    return extra


def build_technical_concept_cards(
    concept_ids: list[str],
    *,
    learning_language: str | None = None,
    source_language: str | None = None,
    pitfall_id: str | None = None,
) -> list[dict[str, Any]]:
    from application.curriculum.validation.expected_concept_checker import (
        build_technical_expected_concept_cards,
    )

    return build_technical_expected_concept_cards(
        concept_ids,
        learning_language=learning_language,
        source_language=source_language,
        pitfall_id=pitfall_id,
    )


def enrich_student_expected_concepts(
    payload: dict[str, Any],
    *,
    pattern_key: str,
    slot_id: str,
    target_language: str,
    slot_pattern_id: str | None = None,
) -> dict[str, Any]:
    """Attach per-language technical expected concepts for student task payload."""
    by_lang = expected_concept_ids_by_language(
        slot_id,
        slot_pattern_id=slot_pattern_id or pattern_key,
    )
    if not by_lang:
        return payload

    target = _normalize_lang(target_language)
    target_ids = by_lang.get(target) or by_lang.get("pascal") or []

    showcase_fields: dict[str, Any] = {}
    raw_examples = payload.get("code_examples")
    if isinstance(raw_examples, dict):
        raw_showcase = raw_examples.get("curriculum_showcase")
        if isinstance(raw_showcase, dict):
            showcase_fields = raw_showcase

    source_lang = resolve_source_language(
        payload,
        showcase_fields,
        target_language=target,
    )
    from application.curriculum.display.mplt_pattern_bindings import get_mplt_pattern_binding

    binding = get_mplt_pattern_binding(pattern_key) or {}
    dominant_pitfall_id = binding.get("dominant_pitfall_id")

    cards = build_technical_concept_cards(
        target_ids,
        learning_language=target,
        source_language=source_lang,
        pitfall_id=str(dominant_pitfall_id) if dominant_pitfall_id else None,
    )
    cards_by_lang = {
        lang: build_technical_concept_cards(
            ids,
            learning_language=_normalize_lang(lang),
            source_language=source_lang,
            pitfall_id=str(dominant_pitfall_id) if dominant_pitfall_id else None,
        )
        for lang, ids in by_lang.items()
    }

    result = dict(payload)
    result["expected_concept_ids"] = list(target_ids)
    result["expected_concepts"] = cards

    curriculum = dict(result.get("curriculum") or {})
    curriculum["expected_concept_ids"] = list(target_ids)
    curriculum["expected_concepts"] = cards
    curriculum["expected_concept_ids_by_language"] = {k: list(v) for k, v in by_lang.items()}
    curriculum["expected_concepts_by_language"] = cards_by_lang
    curriculum["slot_pattern_id"] = pattern_key
    curriculum["expected_concepts_mode"] = "technical"
    result["curriculum"] = curriculum
    return result


def resolve_source_language(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any],
    *,
    target_language: str,
) -> str:
    """Infer «Я знаю» language for MPLT pair filtering."""
    from application.curriculum.display.pascal_hint_engine import KNOWN_SOURCE_LANGUAGES

    target = _normalize_lang(target_language)
    for key in ("requested_source_language", "source_language"):
        raw = _normalize_lang(str(payload.get(key) or showcase_fields.get(key) or ""))
        if raw in KNOWN_SOURCE_LANGUAGES:
            return raw

    if target in {"python", "cpp", "csharp", "java"}:
        mirror_source = "pascal"
    elif target == "pascal":
        mirror_source = "python"
    else:
        mirror_source = "python"

    variants = showcase_fields.get("known_language_variants") or payload.get("known_language_variants")
    if isinstance(variants, dict):
        available = {
            _normalize_lang(lang)
            for lang, entry in variants.items()
            if isinstance(entry, dict) and str(entry.get("source_code") or "").strip()
        }
        if mirror_source in available and mirror_source != target:
            return mirror_source
        for lang in KNOWN_SOURCE_LANGUAGES:
            if lang != target and lang in available:
                return lang

    examples = payload.get("code_examples") or {}
    if isinstance(examples, dict):
        if mirror_source != target and str(examples.get(mirror_source) or "").strip():
            return mirror_source
        for lang in KNOWN_SOURCE_LANGUAGES:
            if lang == target:
                continue
            if str(examples.get(lang) or "").strip():
                return lang

    return mirror_source


def _proactive_text_from_pitfall_pair(
    pitfall_id: str,
    *,
    source_language: str,
    target_language: str,
) -> tuple[str, dict[str, Any]]:
    from application.curriculum.display.pitfall_catalog import (
        build_pitfall_payload,
        build_pitfall_payload_for_languages,
        get_pitfall,
        pitfall_applies_to_language_pair,
    )

    spec = get_pitfall(pitfall_id)
    if not spec or not pitfall_applies_to_language_pair(
        spec,
        source_language=source_language,
        target_language=target_language,
    ):
        return "", {}

    pair_payload = build_pitfall_payload_for_languages(
        pitfall_id,
        source_language=source_language,
        target_language=target_language,
    )
    text = str(
        pair_payload.get("reference_warning_ru")
        or pair_payload.get("hint_ru")
        or pair_payload.get("contrast_note_ru")
        or ""
    ).strip()
    if not text:
        generic = build_pitfall_payload(pitfall_id)
        text = str(
            generic.get("reference_warning_ru")
            or generic.get("hint_ru")
            or generic.get("contrast_note_ru")
            or ""
        ).strip()
    return text, pair_payload


def transfer_meta_for_language_pair(
    pattern_key: str,
    *,
    source_language: str,
    target_language: str,
) -> dict[str, Any]:
    """Proactive MPLT transfer block for GET task payload (Stage 2 resolver)."""
    from application.curriculum.display.chapter1_algo_basics_pitfalls import (
        is_chapter1_pattern,
        resolve_chapter1_pitfall_ids,
        resolve_chapter1_proactive_pitfall_ids,
    )
    from application.curriculum.display.chapter2_branches_pitfalls import (
        is_chapter2_pattern,
        resolve_chapter2_pitfall_ids,
        resolve_chapter2_proactive_pitfall_ids,
    )
    from application.curriculum.display.chapter3_loops_pitfalls import (
        is_chapter3_pattern,
        resolve_chapter3_pitfall_ids,
        resolve_chapter3_proactive_pitfall_ids,
    )
    from application.curriculum.display.chapter4_arrays_pitfalls import (
        is_chapter4_pattern,
        resolve_chapter4_pitfall_ids,
        resolve_chapter4_proactive_pitfall_ids,
    )
    from application.curriculum.display.chapter5_strings_pitfalls import (
        is_chapter5_pattern,
        resolve_chapter5_pitfall_ids,
        resolve_chapter5_proactive_pitfall_ids,
    )
    from application.curriculum.display.pitfall_catalog import get_pitfall
    from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    key = str(pattern_key or "").strip()

    base = resolve_v128_transfer_meta(key) if key else {"transfer_type": "TCC"}
    debug_id = base.get("debug_id")

    if source == target:
        result: dict[str, Any] = {
            "transfer_type": str(base.get("transfer_type") or "TCC").upper(),
            "pitfall_id": base.get("pitfall_id"),
            "pitfall_ids": [],
            "debug_id": debug_id,
            "slot_pattern_id": base.get("slot_pattern_id"),
            "proactive": _empty_proactive(),
            "proactive_items": [],
        }
        _merge_algorithm_debug_meta(result, base)
        return result

    pitfall_ids: list[str] = []
    proactive_pitfall_ids: list[str] = []
    if is_chapter1_pattern(key):
        pitfall_ids = resolve_chapter1_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
        proactive_pitfall_ids = resolve_chapter1_proactive_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter2_pattern(key):
        pitfall_ids = resolve_chapter2_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
        proactive_pitfall_ids = resolve_chapter2_proactive_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter3_pattern(key):
        pitfall_ids = resolve_chapter3_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
        proactive_pitfall_ids = resolve_chapter3_proactive_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter4_pattern(key):
        pitfall_ids = resolve_chapter4_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
        proactive_pitfall_ids = resolve_chapter4_proactive_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
    elif is_chapter5_pattern(key):
        pitfall_ids = resolve_chapter5_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
        proactive_pitfall_ids = resolve_chapter5_proactive_pitfall_ids(
            key,
            source_language=source,
            target_language=target,
        )
    elif base.get("pitfall_id"):
        pitfall_ids = [str(base.get("pitfall_id"))]
        proactive_pitfall_ids = list(pitfall_ids)

    proactive_items: list[dict[str, Any]] = []
    merged_concept_ids: list[str] = []
    pair_payload_merged: dict[str, Any] = {}

    for pid in proactive_pitfall_ids:
        spec = get_pitfall(pid)
        if not spec:
            continue
        text, pair_payload = _proactive_text_from_pitfall_pair(
            pid,
            source_language=source_language,
            target_language=target_language,
        )
        if not text:
            continue
        transfer_type = str(spec.get("transfer_type") or "TCC").upper()
        proactive_items.append(
            {
                "pitfall_id": pid,
                "transfer_type": transfer_type,
                "zone": proactive_zone_for_transfer_type(transfer_type),
                "text": text,
                "concept_ids": list(spec.get("concept_ids") or []),
            }
        )
        for concept_id in spec.get("concept_ids") or []:
            cid = str(concept_id).strip()
            if cid and cid not in merged_concept_ids:
                merged_concept_ids.append(cid)
        for field, value in pair_payload.items():
            if value is not None and field not in pair_payload_merged:
                pair_payload_merged[field] = value

    primary = pitfall_ids[0] if pitfall_ids else None
    primary_spec = get_pitfall(str(primary)) if primary else None
    transfer_type = (
        str(primary_spec.get("transfer_type") or base.get("transfer_type") or "TCC").upper()
        if primary_spec
        else str(base.get("transfer_type") or "TCC").upper()
    )
    if not pitfall_ids:
        transfer_type = str(base.get("transfer_type") or "TCC").upper()

    banner_items = proactive_items
    banner_text = (
        "\n\n".join(
            str(item.get("text") or "").strip()
            for item in banner_items
            if str(item.get("text") or "").strip()
        )
        if banner_items
        else ""
    )

    result = {
        "transfer_type": transfer_type if pitfall_ids else str(base.get("transfer_type") or "TCC").upper(),
        "pitfall_id": primary,
        "pitfall_ids": pitfall_ids,
        "debug_id": debug_id,
        "slot_pattern_id": base.get("slot_pattern_id"),
        "proactive": _empty_proactive(),
        "proactive_items": banner_items,
    }

    _merge_algorithm_debug_meta(result, base)

    if banner_items:
        result["proactive"] = {
            "zone": banner_items[0].get("zone"),
            "text": banner_text or banner_items[0].get("text"),
            "concept_ids": [
                cid
                for item in banner_items
                for cid in (item.get("concept_ids") or [])
            ],
        }
        if banner_text:
            result["reference_warning_ru"] = banner_text
        for field, value in pair_payload_merged.items():
            if value is not None and field not in result:
                result[field] = value

    pedagogy = base.get("pedagogy_note_ru")
    if pedagogy:
        result["pedagogy_note_ru"] = pedagogy

    return result


def build_pair_task_hints(
    base_hints: list[str] | None,
    *,
    pitfall_id: str | None,
    source_language: str,
    target_language: str,
) -> list[str]:
    """Generic hints + one pair-specific line (no stale Pascal/Python from DB)."""
    from application.curriculum.display.pitfall_messages import proactive_pitfall_message

    generic = [str(item).strip() for item in (base_hints or []) if str(item).strip()]
    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)

    neutral: list[str] = []
    for hint in generic:
        lowered = hint.lower()
        if any(
            token in lowered
            for token in ("pascal", "python", "c++", "java", "c#", "div n", "// n", "readln", "split()")
        ):
            continue
        neutral.append(hint)

    if source == target or not pitfall_id:
        return (neutral or generic)[:3]

    pair_text = proactive_pitfall_message(
        pitfall_id,
        source_language=source,
        target_language=target,
    )
    if not pair_text:
        return (neutral or generic)[:3]

    # Pair-specific MPLT text lives in transfer.proactive (amber banner), not hint list.
    if neutral:
        return neutral[:3]
    return generic[:3]
