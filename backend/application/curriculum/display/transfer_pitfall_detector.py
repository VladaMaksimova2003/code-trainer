"""Detect FCC/AFCC transfer pitfalls in student submissions."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

from application.curriculum.display.pitfall_catalog import PitfallSpec, get_pitfall

WARNING_TYPE = "TRANSFER_PITFALL"


def _normalize_code(text: str) -> str:
    return " ".join(str(text or "").split())


def _similar(a: str, b: str, *, threshold: float = 0.85) -> bool:
    if not a.strip() or not b.strip():
        return False
    return SequenceMatcher(None, _normalize_code(a), _normalize_code(b)).ratio() >= threshold


def _warning_message(
    spec: PitfallSpec,
    label: str,
    *,
    detection: str = "lex",
    source_language: str = "python",
    target_language: str = "pascal",
) -> dict[str, str]:
    from application.curriculum.display.pitfall_messages import reactive_pitfall_message

    pitfall_id = str(spec.get("id") or "")
    body = reactive_pitfall_message(
        pitfall_id,
        source_language=source_language,
        target_language=target_language,
    )
    if not body:
        body = str(spec.get("feedback_ru") or "").strip()
    if not body:
        fallback = str(
            spec.get("contrast_note_ru") or spec.get("hint_ru") or label
        ).strip()
        body = fallback
    transfer_type = str(spec.get("transfer_type") or label).strip()
    return {
        "text": body or str(spec.get("hint_ru") or "").strip(),
        "type": WARNING_TYPE,
        "pitfall_id": pitfall_id,
        "transfer_type": transfer_type,
        "feedback_ru": body,
        "detection": detection,
    }


def detect_fcc_pitfall(
    spec: PitfallSpec,
    *,
    target_language: str,
    code: str,
    buggy_code: str = "",
    source_language: str = "python",
) -> list[dict[str, str]]:
    from application.curriculum.display.fcc_ast_detector import (
        code_outside_string_literals,
        detect_fcc_matches_buggy_ast,
        detect_fcc_pattern_ast,
        pitfall_has_ast_rule,
        _safe_parse,
    )

    lang = target_language.lower()
    if lang in {"cs", "c#"}:
        lang = "csharp"
    pitfall_id = str(spec.get("id") or "")
    detector = spec.get("detector", "matches_buggy")
    ast_covered = pitfall_has_ast_rule(pitfall_id, lang)
    parse_ok = _safe_parse(code, lang) is not None

    if detector == "code_pattern":
        ast_hit = detect_fcc_pattern_ast(pitfall_id, lang, code)
        if ast_hit is True:
            return [_warning_message(
                spec, "FCC", detection="ast",
                source_language=source_language, target_language=target_language,
            )]
        if ast_hit is False and parse_ok and ast_covered:
            return []
        search_text = code_outside_string_literals(code, lang) if parse_ok else code
        pat = (spec.get("code_patterns") or {}).get(lang)
        if pat and re.search(pat, search_text, re.I | re.M):
            return [_warning_message(
                spec, "FCC", detection="lex",
                source_language=source_language, target_language=target_language,
            )]
        return []

    if detector == "matches_buggy":
        if parse_ok:
            ast_match = detect_fcc_matches_buggy_ast(
                spec,
                target_language=lang,
                code=code,
                buggy_code=buggy_code,
            )
            if ast_match is True:
                return [_warning_message(
                    spec, "FCC", detection="ast",
                    source_language=source_language, target_language=target_language,
                )]
            if ast_match is False:
                return []

        snippet = (spec.get("buggy_snippets") or {}).get(lang, "")
        if snippet and snippet in code:
            return [_warning_message(
                spec, "FCC", detection="lex",
                source_language=source_language, target_language=target_language,
            )]

        if buggy_code.strip() and _similar(code, buggy_code):
            return [_warning_message(
                spec, "FCC", detection="lex",
                source_language=source_language, target_language=target_language,
            )]

    return []


def detect_atcc_pitfall(
    spec: PitfallSpec,
    *,
    target_language: str,
    code: str,
    buggy_code: str = "",
    source_language: str = "python",
) -> list[dict[str, str]]:
    from application.curriculum.display.fcc_ast_detector import (
        code_outside_string_literals,
        detect_fcc_matches_buggy_ast,
        detect_mplt_pattern_ast,
        pitfall_has_ast_rule,
        _safe_parse,
    )

    lang = target_language.lower()
    if lang in {"cs", "c#"}:
        lang = "csharp"
    pitfall_id = str(spec.get("id") or "")
    detector = spec.get("detector", "matches_buggy")
    ast_covered = pitfall_has_ast_rule(pitfall_id, lang)
    parse_ok = _safe_parse(code, lang) is not None

    if detector == "matches_buggy":
        if parse_ok:
            ast_match = detect_fcc_matches_buggy_ast(
                spec,
                target_language=lang,
                code=code,
                buggy_code=buggy_code,
            )
            if ast_match is True:
                return [_warning_message(
                    spec, "ATCC", detection="ast",
                    source_language=source_language, target_language=target_language,
                )]
            if ast_match is False:
                return []

        snippet = (spec.get("buggy_snippets") or {}).get(lang, "")
        if snippet and snippet in code:
            return [_warning_message(
                spec, "ATCC", detection="lex",
                source_language=source_language, target_language=target_language,
            )]

        if buggy_code.strip() and _similar(code, buggy_code):
            return [_warning_message(
                spec, "ATCC", detection="lex",
                source_language=source_language, target_language=target_language,
            )]

    if detector == "code_pattern":
        ast_hit = detect_mplt_pattern_ast(pitfall_id, lang, code)
        if ast_hit is True:
            return [_warning_message(
                spec, "ATCC", detection="ast",
                source_language=source_language, target_language=target_language,
            )]
        if ast_hit is False and parse_ok and ast_covered:
            return []
        search_text = code_outside_string_literals(code, lang) if parse_ok else code
        pat = (spec.get("code_patterns") or {}).get(lang)
        if pat and re.search(pat, search_text, re.I | re.M):
            return [_warning_message(
                spec, "ATCC", detection="lex",
                source_language=source_language, target_language=target_language,
            )]

    return []


def detect_afcc_pitfall(
    spec: PitfallSpec,
    *,
    target_language: str,
    code: str,
    test_results: list[dict[str, Any]],
    atcc_already_fired: bool,
    source_language: str = "python",
) -> list[dict[str, str]]:
    from application.curriculum.display.afcc_contrast_detector import (
        detect_afcc_pitfall as _detect_afcc_pitfall,
    )

    return _detect_afcc_pitfall(
        spec,
        target_language=target_language,
        code=code,
        test_results=test_results,
        atcc_already_fired=atcc_already_fired,
        source_language=source_language,
    )


def detect_transfer_pitfalls(
    *,
    pitfall_id: str,
    transfer_type: str,
    source_language: str,
    target_language: str,
    code: str,
    test_results: list[dict[str, Any]] | None = None,
    buggy_code: str = "",
    atcc_warnings: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    spec = get_pitfall(pitfall_id)
    if not spec:
        return []

    tt = str(transfer_type or spec.get("transfer_type") or "").upper()
    atcc_fired = bool(atcc_warnings)
    results = list(test_results or [])
    src = str(source_language or "python")

    if tt == "ATCC":
        return detect_atcc_pitfall(
            spec,
            target_language=target_language,
            code=code,
            buggy_code=buggy_code,
            source_language=src,
        )
    if tt == "FCC":
        return detect_fcc_pitfall(
            spec,
            target_language=target_language,
            code=code,
            buggy_code=buggy_code,
            source_language=src,
        )
    if tt == "AFCC":
        return detect_afcc_pitfall(
            spec,
            target_language=target_language,
            code=code,
            test_results=results,
            atcc_already_fired=atcc_fired,
            source_language=src,
        )
    return []
