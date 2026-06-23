"""AlgorithmDebug feedback — orthogonal to MPLT transfer pitfalls (Stage 4)."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

from application.curriculum.display.algorithm_debug_catalog import (
    AlgorithmDebugSpec,
    get_algorithm_debug,
)

WARNING_TYPE = "ALGORITHM"


def _normalize_code(text: str) -> str:
    return " ".join(str(text or "").split())


def _similar(a: str, b: str, *, threshold: float = 0.85) -> bool:
    if not a.strip() or not b.strip():
        return False
    return SequenceMatcher(None, _normalize_code(a), _normalize_code(b)).ratio() >= threshold


def _any_test_failed(test_results: list[dict[str, Any]]) -> bool:
    return any(str(item.get("status") or "").upper() != "PASSED" for item in test_results)


def _algorithm_message(spec: AlgorithmDebugSpec, *, detection: str = "matches_buggy", code: str = "") -> dict[str, str]:
    debug_id = str(spec.get("id") or "")
    body = str(spec.get("feedback_ru") or spec.get("hint_ru") or "Ошибка алгоритма").strip()
    body = _concrete_algorithm_body(debug_id, body, code)
    return {
        "text": body,
        "type": WARNING_TYPE,
        "debug_id": debug_id,
        "feedback_ru": body,
        "detection": detection,
    }


def _concrete_algorithm_body(debug_id: str, body: str, code: str) -> str:
    text = str(code or "")
    if debug_id == "filter_positive":
        snippets: list[str] = []
        if re.search(r"count\s*:=\s*1\b", text, re.I):
            snippets.append("Pascal: count := 1 → нужно count := 0")
        if re.search(r"count\s*=\s*1\b", text, re.I):
            snippets.append("count = 1 → нужно count = 0")
        if re.search(r"if\s+[\w.]+\s*>=\s*0\b", text, re.I):
            snippets.append("if amount >= 0 → нужно if amount > 0")
        if snippets:
            return f"{body} Примеры в коде: {'; '.join(snippets)}."
        if "count := 0" not in body and "amount > 0" not in body:
            return (
                f"{body} Счётчик стартует с 0 (count := 0 / count = 0), "
                "считаются только amount > 0."
            )
    return body


_DEBUG_HEURISTICS: dict[str, re.Pattern[str]] = {
    "filter_positive": re.compile(
        r"(?:if\s+[\w.]+\s*>\s*0\b|count\s*[:=]\s*1\b)",
        re.I,
    ),
    "threshold_count": re.compile(
        r"if\s+[\w.]+\s*>=\s*50\b[\s\S]*?(?:else|end|writeln)",
        re.I,
    ),
    "branch_logic": re.compile(r"\belse\b", re.I),
    "multi_branch_discount": re.compile(r"\bif\b.*\bif\b", re.I | re.S),
    "map_key_missing": re.compile(r"\[[^\]]+\](?!\s*(?:in\b|:=\s*))", re.I),
}


def detect_algorithm_debug(
    *,
    debug_id: str,
    target_language: str,
    code: str,
    test_results: list[dict[str, Any]] | None = None,
    buggy_code: str = "",
) -> list[dict[str, str]]:
    """Return ALGORITHM feedback when failed tests match the reference buggy solution."""
    del target_language  # reserved for future language-specific rules
    results = list(test_results or [])
    if not results or not _any_test_failed(results):
        return []

    spec = get_algorithm_debug(debug_id)
    if not spec:
        return []

    text = str(code or "")
    buggy = str(buggy_code or "").strip()

    if buggy and _similar(text, buggy):
        return [_algorithm_message(spec, detection="matches_buggy", code=text)]

    heuristic = _DEBUG_HEURISTICS.get(str(debug_id).strip())
    if heuristic and heuristic.search(text):
        return [_algorithm_message(spec, detection="lex", code=text)]

    return []
