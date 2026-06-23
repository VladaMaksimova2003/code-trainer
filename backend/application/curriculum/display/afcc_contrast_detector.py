"""AFCC detection via contrast test failures (thesis §3.2.8 — no AST)."""

from __future__ import annotations

import re
from typing import Any

from application.curriculum.display.pitfall_catalog import PitfallSpec, get_pitfall

WARNING_TYPE = "TRANSFER_PITFALL"


def resolve_test_result_at_index(
    test_results: list[dict[str, Any]],
    index: int,
) -> dict[str, Any] | None:
    """Resolve a test result by 0-based suite index or 1-based case number."""
    if 0 <= index < len(test_results):
        return test_results[index]
    one_based = index + 1
    for item in test_results:
        if int(item.get("case") or 0) == one_based:
            return item
    return None


def contrast_indices_failed(
    spec: PitfallSpec,
    test_results: list[dict[str, Any]],
) -> list[int]:
    indices = [int(i) for i in (spec.get("contrast_test_indices") or [0])]
    failed: list[int] = []
    for idx in indices:
        item = resolve_test_result_at_index(test_results, idx)
        if item is None:
            continue
        if str(item.get("status") or "").upper() != "PASSED":
            failed.append(idx)
    return failed


def any_test_failed(test_results: list[dict[str, Any]]) -> bool:
    return any(str(item.get("status") or "").upper() != "PASSED" for item in test_results)


def build_afcc_warning(
    spec: PitfallSpec,
    *,
    detection: str = "contrast",
    contrast_case_index: int | None = None,
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
        body = str(
            spec.get("contrast_note_ru") or spec.get("hint_ru") or "AFCC"
        ).strip()
    transfer_type = str(spec.get("transfer_type") or "AFCC").strip()
    payload: dict[str, str] = {
        "text": body,
        "type": WARNING_TYPE,
        "pitfall_id": pitfall_id,
        "transfer_type": transfer_type,
        "feedback_ru": body,
        "detection": detection,
    }
    if contrast_case_index is not None:
        payload["contrast_case_index"] = str(contrast_case_index)
    return payload


def detect_afcc_contrast(
    spec: PitfallSpec,
    *,
    test_results: list[dict[str, Any]],
    atcc_already_fired: bool,
    source_language: str = "python",
    target_language: str = "pascal",
) -> list[dict[str, str]]:
    if atcc_already_fired:
        return []
    if not test_results or not any_test_failed(test_results):
        return []

    failed_indices = contrast_indices_failed(spec, test_results)
    if not failed_indices:
        return []
    return [
        build_afcc_warning(
            spec,
            detection="contrast",
            contrast_case_index=failed_indices[0],
            source_language=source_language,
            target_language=target_language,
        )
    ]


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def detect_afcc_pitfall(
    spec: PitfallSpec,
    *,
    target_language: str,
    code: str,
    test_results: list[dict[str, Any]],
    atcc_already_fired: bool,
    source_language: str = "python",
) -> list[dict[str, str]]:
    detector = spec.get("detector", "contrast_test")
    lang = _normalize_lang(target_language)
    src = _normalize_lang(source_language)

    if detector == "contrast_test":
        return detect_afcc_contrast(
            spec,
            test_results=test_results,
            atcc_already_fired=atcc_already_fired,
            source_language=src,
            target_language=lang,
        )

    if atcc_already_fired or not test_results or not any_test_failed(test_results):
        return []

    if detector == "code_pattern":
        from application.curriculum.display.fcc_ast_detector import (
            code_outside_string_literals,
            detect_mplt_pattern_ast,
            pitfall_has_ast_rule,
            _safe_parse,
        )

        pitfall_id = str(spec.get("id") or "")
        ast_covered = pitfall_has_ast_rule(pitfall_id, lang)
        parse_ok = _safe_parse(code, lang) is not None
        ast_hit = detect_mplt_pattern_ast(pitfall_id, lang, code)
        if ast_hit is True:
            return [build_afcc_warning(
                spec, detection="ast",
                source_language=src, target_language=lang,
            )]
        if ast_hit is False and parse_ok and ast_covered:
            return []
        search_text = code_outside_string_literals(code, lang) if parse_ok else code
        pat = (spec.get("code_patterns") or {}).get(lang)
        if pat and re.search(pat, search_text, re.I | re.M):
            return [build_afcc_warning(
                spec, detection="lex",
                source_language=src, target_language=lang,
            )]

    if detector == "matches_buggy":
        snippet = (spec.get("buggy_snippets") or {}).get(lang, "")
        if snippet and snippet in code:
            return [build_afcc_warning(
                spec, detection="lex",
                source_language=src, target_language=lang,
            )]

    return []


def validate_afcc_contrast_bindings(
    meta: dict[str, dict[str, Any]],
    *,
    pattern_pitfall_map: dict[str, str],
) -> list[str]:
    """Ensure AFCC contrast indices fit bound task test suites."""
    errors: list[str] = []
    for pattern, pitfall_id in sorted(pattern_pitfall_map.items()):
        spec = get_pitfall(pitfall_id)
        if not spec or str(spec.get("transfer_type") or "").upper() != "AFCC":
            continue
        if str(spec.get("detector") or "") != "contrast_test":
            continue
        row = meta.get(pattern) or {}
        tests = list(row.get("test_cases") or [])
        indices = [int(i) for i in (spec.get("contrast_test_indices") or [0])]
        for idx in indices:
            if idx < 0 or idx >= len(tests):
                errors.append(
                    f"{pattern}/{pitfall_id}: contrast_test_indices[{idx}] "
                    f"out of range (tests={len(tests)})"
                )
                continue
            case = tests[idx]
            if not case.get("mplt_contrast") and str(case.get("tag") or "") != "contrast":
                errors.append(
                    f"{pattern}/{pitfall_id}: test_cases[{idx}] missing mplt_contrast/tag=contrast"
                )
    return errors
