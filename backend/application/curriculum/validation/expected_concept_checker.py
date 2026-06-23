"""Validate student code against expected concepts via canonical AST detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from application.curriculum.validation.canonical_technical_ids import (
    canonical_technical_id,
    canonicalize_technical_ids,
)
from application.curriculum.validation.technical_concept_detector import (
    detect_technical_concepts,
    rollup_to_display_tc,
    technical_concept_label,
)
from application.curriculum.validation.technical_concept_registry import (
    list_display_tc_cards,
    load_technical_to_tc_map,
)


def _is_display_tc_id(raw: str) -> bool:
    return str(raw or "").strip().startswith("tc_")


# Student UI rolls assignment into the arithmetic TC card (registry keeps tc_assignment for admin).
_DISPLAY_TC_ALIASES: dict[str, str] = {"tc_assignment": "tc_arithmetic"}


def _normalize_language(language: str) -> str:
    lang = str(language or "pascal").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def normalize_expected_technical_ids(raw_ids: list[str]) -> list[str]:
    """Legacy / canonical ids → deduped canonical technical ids."""
    return canonicalize_technical_ids(
        [item for item in raw_ids if str(item).strip() and not _is_display_tc_id(item)]
    )


def normalize_expected_display_tc_ids(raw_ids: list[str]) -> list[str]:
    """Legacy / canonical / display ids → deduped display TC card ids."""
    mapping = load_technical_to_tc_map()
    out: set[str] = set()
    for raw in raw_ids:
        key = str(raw or "").strip()
        if not key:
            continue
        if _is_display_tc_id(key):
            out.add(_DISPLAY_TC_ALIASES.get(key, key))
            continue
        tc_id = mapping.get(canonical_technical_id(key))
        if tc_id:
            out.add(_DISPLAY_TC_ALIASES.get(tc_id, tc_id))
    return sorted(out)


def expected_check_mode(raw_ids: list[str]) -> str:
    """``display`` when any expected id is a display TC card."""
    if any(_is_display_tc_id(item) for item in raw_ids):
        return "display"
    return "technical"


def label_for_concept_id(concept_id: str, *, mode: str = "technical") -> str:
    if mode == "display" or _is_display_tc_id(concept_id):
        card = list_display_tc_cards().get(concept_id) or {}
        name = card.get("name_ru")
        if name:
            return str(name)
    return technical_concept_label(concept_id)


@dataclass(frozen=True)
class ConceptCheckResult:
    enabled: bool
    language: str
    mode: str
    expected: list[str]
    found: list[str]
    missing: list[str]
    detected_technical_ids: list[str]
    detected_display_tc_ids: list[str]
    signal_ids: list[str]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "language": self.language,
            "mode": self.mode,
            "expected": list(self.expected),
            "found": list(self.found),
            "missing": list(self.missing),
            "detected_technical_ids": list(self.detected_technical_ids),
            "detected_display_tc_ids": list(self.detected_display_tc_ids),
            "signal_ids": list(self.signal_ids),
            "passed": self.passed,
        }

    def missing_labels(self) -> list[str]:
        return [label_for_concept_id(item, mode=self.mode) for item in self.missing]


def _example_snippet_for_missing_concept(
    concept_id: str,
    *,
    language: str,
    mode: str,
) -> str | None:
    """Short code sample for a missing expected concept (display TC or technical id)."""
    lang = _normalize_language(language)
    raw_id = str(concept_id or "").strip()
    if not raw_id:
        return None

    from application.curriculum.validation.technical_concept_registry import (
        examples_for_technical_concept,
        hints_to_examples_by_language,
    )

    rows: list[dict[str, str]] = []
    if _is_display_tc_id(raw_id) or mode == "display":
        from application.curriculum.display.tc_display_registry_service import get_merged_display_tc_raw

        card = get_merged_display_tc_raw(raw_id) or {}
        by_lang = hints_to_examples_by_language(card)
        rows = list(by_lang.get(lang) or [])
        if not rows and by_lang:
            rows = list(next(iter(by_lang.values())))
    else:
        by_lang = examples_for_technical_concept(raw_id, language=lang)
        rows = list(by_lang.get(lang) or [])
        if not rows and by_lang:
            rows = list(next(iter(by_lang.values())))

    if not rows:
        return None
    row = rows[0]
    title = str(row.get("title") or "пример").strip()
    code = str(row.get("code") or "").strip()
    if not code:
        return None
    return f"Ожидается приём вроде «{title}»:\n{code}"


def format_construction_warning_messages(
    concept_check: dict[str, Any] | ConceptCheckResult | None,
    *,
    tests_passed: bool = False,
    language: str | None = None,
) -> list[dict[str, str]]:
    """One summary when tests passed; per-label lines otherwise (no duplicate both)."""
    if concept_check is None:
        return []
    if isinstance(concept_check, ConceptCheckResult):
        check = concept_check
    else:
        if not concept_check.get("enabled") or concept_check.get("passed"):
            return []
        check = ConceptCheckResult(
            enabled=True,
            language=str(concept_check.get("language") or language or ""),
            mode=str(concept_check.get("mode") or "technical"),
            expected=list(concept_check.get("expected") or []),
            found=list(concept_check.get("found") or []),
            missing=list(concept_check.get("missing") or []),
            detected_technical_ids=list(concept_check.get("detected_technical_ids") or []),
            detected_display_tc_ids=list(concept_check.get("detected_display_tc_ids") or []),
            signal_ids=list(concept_check.get("signal_ids") or []),
            passed=False,
        )
    if not check.enabled or check.passed:
        return []
    labels = [label for label in check.missing_labels() if label]
    if not labels:
        return []
    lang = _normalize_language(language or check.language or "pascal")
    missing_ids = list(check.missing)
    if tests_passed:
        summary_lines = [
            "Тесты пройдены, но в решении не найдены ожидаемые конструкции:",
            *[f"- {label}" for label in labels],
        ]
        for mid in missing_ids[:2]:
            snippet = _example_snippet_for_missing_concept(mid, language=lang, mode=check.mode)
            if snippet:
                summary_lines.append(snippet)
        return [{"text": "\n".join(summary_lines), "type": "CONSTRUCTION_WARNING"}]
    messages: list[dict[str, str]] = []
    for label, mid in zip(labels, missing_ids):
        text = f"В коде не найдена ожидаемая конструкция: {label}"
        snippet = _example_snippet_for_missing_concept(mid, language=lang, mode=check.mode)
        if snippet:
            text = f"{text}\n\n{snippet}"
        messages.append({"text": text, "type": "CONSTRUCTION_WARNING"})
    # Extra missing labels without paired ids (should not happen, but keep parity).
    for label in labels[len(missing_ids) :]:
        messages.append(
            {
                "text": f"В коде не найдена ожидаемая конструкция: {label}",
                "type": "CONSTRUCTION_WARNING",
            }
        )
    return messages


def check_expected_concepts(
    code: str,
    language: str,
    expected_concept_ids: list[str],
    *,
    enabled: bool = True,
) -> ConceptCheckResult:
    """Compare expected concepts (legacy, canonical, or display TC) with AST detection."""
    lang = _normalize_language(language)
    raw = [str(item).strip() for item in expected_concept_ids if str(item).strip()]
    empty = ConceptCheckResult(
        enabled=False,
        language=lang,
        mode="technical",
        expected=[],
        found=[],
        missing=[],
        detected_technical_ids=[],
        detected_display_tc_ids=[],
        signal_ids=[],
        passed=True,
    )
    if not enabled or not raw:
        return empty

    mode = expected_check_mode(raw)
    detection = detect_technical_concepts(code, lang)
    detected_all = _detected_technical_ids(detection)
    detected_technical = set(detection.technical_ids)
    detected_display = set(rollup_to_display_tc(detected_all))
    signals = set(detection.signal_ids)

    if mode == "display":
        expected_set = set(normalize_expected_display_tc_ids(raw))
        found = expected_set & detected_display
        missing = expected_set - detected_display
    else:
        expected_set = set(normalize_expected_technical_ids(raw))
        found = expected_set & detected_all
        missing = expected_set - detected_all

    return ConceptCheckResult(
        enabled=True,
        language=lang,
        mode=mode,
        expected=sorted(expected_set),
        found=sorted(found),
        missing=sorted(missing),
        detected_technical_ids=sorted(detected_technical),
        detected_display_tc_ids=sorted(detected_display),
        signal_ids=sorted(signals),
        passed=not missing,
    )


def _merge_examples(
    target: dict[str, list[dict[str, str]]],
    source: dict[str, list[dict[str, str]]],
) -> None:
    seen_codes: set[tuple[str, str]] = set()
    for lang, rows in target.items():
        for row in rows:
            seen_codes.add((lang, str(row.get("code") or "")))

    for lang, rows in source.items():
        bucket = target.setdefault(lang, [])
        for row in rows:
            key = (lang, str(row.get("code") or ""))
            if key in seen_codes or not row.get("code"):
                continue
            bucket.append(row)
            seen_codes.add(key)


def _concept_in_pitfall_scope(concept_id: str, pitfall_spec: dict[str, Any] | None) -> bool:
    if not pitfall_spec:
        return False
    canonical = canonical_technical_id(concept_id)
    scope = {canonical_technical_id(str(item)) for item in (pitfall_spec.get("concept_ids") or [])}
    scope |= {str(item) for item in (pitfall_spec.get("concept_ids") or [])}
    return canonical in scope or str(concept_id) in scope


def _transfer_hint_for_concept(
    concept_id: str,
    *,
    source_language: str,
    target_language: str,
    pitfall_id: str | None = None,
) -> str | None:
    from application.curriculum.display.pitfall_catalog import (
        build_pitfall_payload_for_languages,
        get_pitfall,
    )

    if not pitfall_id:
        return None

    spec = get_pitfall(pitfall_id)
    if not spec or not _concept_in_pitfall_scope(concept_id, spec):
        return None

    pair = build_pitfall_payload_for_languages(
        pitfall_id,
        source_language=source_language,
        target_language=target_language,
    )
    return str(
        pair.get("reference_warning_ru")
        or pair.get("hint_ru")
        or pair.get("contrast_note_ru")
        or ""
    ).strip() or None


def build_technical_expected_concept_cards(
    expected_concept_ids: list[str],
    *,
    learning_language: str | None = None,
    source_language: str | None = None,
    pitfall_id: str | None = None,
) -> list[dict[str, Any]]:
    """One UI chip per display TC bundle (deduped), with examples and pair hints."""
    from application.curriculum.validation.technical_concept_registry import (
        examples_for_technical_concept,
        load_technical_to_tc_map,
        lookup_technical_concept_reference,
        tc_concept_label_ru,
    )

    from application.curriculum.display.pitfall_catalog import get_pitfall

    mapping = load_technical_to_tc_map()
    grouped: dict[str, list[str]] = {}
    for raw in expected_concept_ids:
        raw_id = str(raw or "").strip()
        cid = canonical_technical_id(raw_id)
        if not cid or _is_display_tc_id(cid):
            continue
        display_id = mapping.get(cid) or cid
        bucket = grouped.setdefault(display_id, [])
        if raw_id not in bucket:
            bucket.append(raw_id)

    source = str(source_language or "").strip().lower() or None
    target = str(learning_language or "").strip().lower() or None
    pitfall_spec = get_pitfall(pitfall_id) if pitfall_id else None

    payload: list[dict[str, Any]] = []
    for display_id, raw_ids in grouped.items():
        primary_raw = raw_ids[0]
        primary_canonical = canonical_technical_id(primary_raw)
        ref = lookup_technical_concept_reference(primary_canonical) or {}

        examples: dict[str, list[dict[str, str]]] = {}
        for rid in raw_ids:
            _merge_examples(
                examples,
                examples_for_technical_concept(rid, language=target),
            )

        in_proactive_scope = bool(
            pitfall_spec
            and any(_concept_in_pitfall_scope(rid, pitfall_spec) for rid in raw_ids)
        )

        transfer_hint: str | None = None
        if in_proactive_scope and source and target and source != target:
            for rid in raw_ids:
                hint = _transfer_hint_for_concept(
                    rid,
                    source_language=source,
                    target_language=target,
                    pitfall_id=pitfall_id,
                )
                if hint:
                    transfer_hint = hint
                    break

        card: dict[str, Any] = {
            "id": primary_raw,
            "display_id": display_id,
            "technical_concept_ids": list(raw_ids),
            "name_ru": tc_concept_label_ru(primary_raw),
            "description_ru": str(ref.get("description_ru") or ref.get("name_ru") or ""),
            "examples_by_language": examples,
            "in_proactive_scope": in_proactive_scope,
        }
        if transfer_hint:
            card["transfer_hint_ru"] = transfer_hint
        payload.append(card)
    return payload


def build_display_expected_concept_cards(expected_concept_ids: list[str]) -> list[dict[str, Any]]:
    """Roll expected ids up to display TC cards for student UI (deduped, registry order)."""
    from application.curriculum.validation.technical_concept_registry import build_display_tc_ui_card

    # tc_assignment folded into tc_arithmetic for student chips (assignment still detectable via AST).

    mapping = load_technical_to_tc_map()
    cards = list_display_tc_cards()

    def _rollup_display_id(key: str) -> str | None:
        if _is_display_tc_id(key):
            aliased = _DISPLAY_TC_ALIASES.get(key, key)
            return aliased if aliased in cards else None
        display_id = mapping.get(canonical_technical_id(key))
        if not display_id:
            return None
        aliased = _DISPLAY_TC_ALIASES.get(display_id, display_id)
        return aliased if aliased in cards else None

    by_display: dict[str, set[str]] = {}

    for raw in expected_concept_ids:
        key = str(raw or "").strip()
        if not key:
            continue
        display_id = _rollup_display_id(key)
        if not display_id:
            continue
        if _is_display_tc_id(key):
            by_display.setdefault(display_id, set())
            continue
        by_display.setdefault(display_id, set()).add(canonical_technical_id(key))

    payload: list[dict[str, Any]] = []
    for display_id in cards:
        if display_id not in by_display:
            continue
        ui_card = build_display_tc_ui_card(
            display_id,
            technical_concept_ids=sorted(by_display[display_id]),
        )
        if ui_card:
            payload.append(ui_card)
    return payload


def build_display_expected_concept_cards_for_pair(
    expected_concept_ids: list[str],
    *,
    source_language: str | None = None,
    target_language: str | None = None,
    pitfall_id: str | None = None,
    pitfall_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Display TC cards with MPLT chip hints for the active language pair."""
    cards = build_display_expected_concept_cards(expected_concept_ids)
    source = str(source_language or "").strip().lower()
    target = str(target_language or "").strip().lower()
    active_ids: list[str] = []
    if pitfall_id:
        active_ids.append(str(pitfall_id).strip())
    for pid in pitfall_ids or []:
        key = str(pid or "").strip()
        if key and key not in active_ids:
            active_ids.append(key)
    if not source or not target or source == target or not active_ids:
        return cards

    enriched: list[dict[str, Any]] = []
    for card in cards:
        item = dict(card)
        tech_ids = list(item.get("technical_concept_ids") or [])
        if not tech_ids:
            tech_ids = [str(item.get("id") or "")]
        in_scope = False
        transfer_hint: str | None = None
        for pid in active_ids:
            for tech_id in tech_ids:
                hint = _transfer_hint_for_concept(
                    tech_id,
                    source_language=source,
                    target_language=target,
                    pitfall_id=pid,
                )
                if hint:
                    transfer_hint = hint
                    in_scope = True
                    break
            if in_scope:
                break
        item["in_proactive_scope"] = in_scope
        if transfer_hint:
            item["transfer_hint_ru"] = transfer_hint
        enriched.append(item)
    return enriched


def _detected_technical_ids(detection) -> frozenset[str]:
    """AST node hits plus coarse signal nodes (e.g. binary_expression → arithmetic)."""
    return frozenset(detection.technical_ids) | frozenset(detection.signal_ids)


def concept_present_in_code(
    code: str,
    concept_id: str,
    *,
    language: str = "pascal",
) -> bool:
    lang = _normalize_language(language)
    cid = str(concept_id or "").strip()
    if not cid:
        return False
    detection = detect_technical_concepts(code, lang)
    detected = _detected_technical_ids(detection)
    if _is_display_tc_id(cid):
        check_id = _DISPLAY_TC_ALIASES.get(cid, cid)
        return check_id in rollup_to_display_tc(detected)
    canonical = canonical_technical_id(cid)
    return canonical in detected


def prune_expected_concepts_for_code(
    expected_concept_ids: list[str],
    code: str,
    language: str,
) -> list[str]:
    """Drop concepts that are not present in reference/solution code."""
    text = str(code or "")
    if not text.strip():
        return [str(item).strip() for item in expected_concept_ids if str(item).strip()]

    lang = _normalize_language(language)
    pruned: list[str] = []
    seen: set[str] = set()
    for concept_id in expected_concept_ids:
        cid = str(concept_id).strip()
        if not cid or cid in seen:
            continue
        if concept_present_in_code(text, cid, language=lang):
            pruned.append(cid)
            seen.add(cid)
    return pruned


def missing_expected_concept_messages(
    code: str,
    expected_concept_ids: list[str],
    *,
    language: str = "pascal",
) -> list[str]:
    """Human-readable warnings for missing pedagogical concepts."""
    result = check_expected_concepts(code, language, expected_concept_ids)
    if not result.enabled or result.passed:
        return []
    return [
        f"В коде не найдена ожидаемая конструкция: {label}"
        for label in result.missing_labels()
    ]


def detect_expected_concepts_in_code(
    code: str,
    *,
    language: str = "pascal",
) -> list[str]:
    """Return display TC card ids detected in code (deduped, registry order)."""
    lang = _normalize_language(language)
    if not str(code or "").strip():
        return []
    detection = detect_technical_concepts(code, lang)
    display_ids = rollup_to_display_tc(detection.technical_ids | detection.signal_ids)
    cards = list_display_tc_cards()
    return [tc_id for tc_id in cards if tc_id in display_ids]


def detect_expected_concepts_multilang(
    samples: list[tuple[str, str]],
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for language, code in samples:
        lang = _normalize_language(language)
        if not lang:
            continue
        result[lang] = detect_expected_concepts_in_code(code, language=lang)
    return result


@dataclass(frozen=True)
class ConceptDetectionItem:
    id: str
    label: str
    detected: bool
    reason: str | None = None


def analyze_expected_concepts(
    code: str,
    *,
    language: str = "pascal",
    concept_ids: list[str] | None = None,
) -> list[ConceptDetectionItem]:
    """Per-expected-concept detection status for live scan UI.

    Uses the same ``concept_present_in_code`` path as import-time
    ``prune_expected_concepts_for_code`` / ``detect_expected_concepts_in_code``.
    """
    lang = _normalize_language(language)
    targets = [str(item).strip() for item in (concept_ids or []) if str(item).strip()]
    if not targets:
        return []

    mode = expected_check_mode(targets)
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in targets:
        normalized = (
            normalize_expected_display_tc_ids([raw])
            if mode == "display"
            else normalize_expected_technical_ids([raw])
        )
        for concept_id in normalized:
            if concept_id not in seen:
                ordered.append(concept_id)
                seen.add(concept_id)

    items: list[ConceptDetectionItem] = []
    for concept_id in ordered:
        label = label_for_concept_id(concept_id, mode=mode)
        detected = concept_present_in_code(code, concept_id, language=lang)
        items.append(
            ConceptDetectionItem(
                id=concept_id,
                label=label,
                detected=detected,
                reason=None
                if detected
                else f"В коде не найдена конструкция «{label}»",
            )
        )
    return items


def checker_coverage_for_language(language: str) -> dict[str, list[str]]:
    """AST detector covers canonical ids from technical_to_tc_map (not regex tables)."""
    del language
    from application.curriculum.validation.technical_concept_registry import (
        list_technical_concept_ids,
    )

    covered = sorted(list_technical_concept_ids())
    return {"covered": covered, "missing_checker": []}


def _label_for(concept_id: str, fallback: str) -> str:
    """Backward-compatible alias for tests."""
    label = label_for_concept_id(concept_id, mode="display")
    return label if label != concept_id else fallback
