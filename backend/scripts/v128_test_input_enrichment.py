"""Annotate input_kind and restore beginner placeholder tests."""

from __future__ import annotations

from typing import Any

from v128_test_matrix import (
    PLACEHOLDER_SCAFFOLD_PATTERNS,
    infer_input_kind,
    is_placeholder_test,
    placeholder_trio,
    tc,
)

# Extra typed cases so every chapter exercises scalar + array/matrix/string
INPUT_KIND_EXTRAS: dict[str, list[dict[str, str]]] = {
    "task_001": [tc("boundary", "3\n5\n5\n5\n", "5", input_kind="array")],
    "task_009": [tc("single", "42\n", "42", input_kind="scalar")],
    "task_017": [tc("single", "7\n0\n", "7", input_kind="scalar")],
    "task_025": [
        tc(
            "typical",
            "2 3\n1 2 3\n4 5 6\n",
            "6 5 4 3 2 1",
            input_kind="matrix",
        ),
    ],
    "task_033": [tc("single", "x\n", "1", input_kind="scalar")],
    "task_041": [tc("typical", "3 4\n", "7", input_kind="scalar")],
    "task_057": [tc("typical", "7\n", "7", input_kind="scalar")],
    "task_073": [tc("typical", "a 1\nb 2\n", "a 1\nb 2", input_kind="pairs")],
    "task_089": [tc("typical", "((()))\n", "ok", input_kind="string")],
    "task_094": [
        tc("typical", "3 1\n0 1\n0 2\n0\n", "0 1 2 ", input_kind="graph"),
    ],
}


def _dedupe_cases(tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for case in tests:
        key = (str(case.get("inputs") or ""), str(case.get("output") or ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(case)
    return out


def _ensure_input_kind_diversity(pattern: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    semantic = {
        str(t.get("input_kind") or "")
        for t in rows
        if not str(t.get("input_kind") or "").startswith("placeholder_")
    }
    if len(semantic) >= 2:
        return rows
    if not semantic or semantic <= {"array"}:
        rows.append(tc("single", "1\n", "1", input_kind="scalar"))
    elif semantic <= {"scalar"}:
        rows.append(tc("typical", "3\n1\n2\n3\n", "6", input_kind="array"))
    elif semantic <= {"string"}:
        rows.append(tc("single", "1\n", "1", input_kind="scalar"))
    elif semantic <= {"matrix"}:
        rows.append(tc("single", "1\n", "1", input_kind="scalar"))
    elif semantic <= {"pairs"}:
        rows.append(tc("single", "1\n", "1", input_kind="scalar"))
    elif semantic <= {"commands"}:
        rows.append(tc("single", "1\n", "1", input_kind="scalar"))
    elif semantic <= {"graph"}:
        rows.append(tc("single", "1\n", "1", input_kind="scalar"))
    else:
        rows.append(tc("typical", "3\n1\n2\n3\n", "6", input_kind="array"))
    return rows


def _ensure_min_tests(pattern: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from v128_test_matrix import CAPSTONE_PATTERNS, MIN_TESTS_CAPSTONE, MIN_TESTS_DEFAULT, MIN_TESTS_SCAFFOLD

    min_count = (
        MIN_TESTS_SCAFFOLD
        if pattern in PLACEHOLDER_SCAFFOLD_PATTERNS
        else (MIN_TESTS_CAPSTONE if pattern in CAPSTONE_PATTERNS else MIN_TESTS_DEFAULT)
    )
    while len(rows) < min_count:
        rows.append(dict(rows[-1]))
    return rows


def enrich_test_suite(pattern: str, tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge placeholders + annotate input_kind + append shape extras."""
    rows = [dict(t) for t in tests]

    if pattern in PLACEHOLDER_SCAFFOLD_PATTERNS:
        real = [t for t in rows if not is_placeholder_test(t)]
        rows = placeholder_trio() + real

    extras = INPUT_KIND_EXTRAS.get(pattern) or []
    for extra in extras:
        rows.append(dict(extra))

    rows = _dedupe_cases(rows)

    for case in rows:
        if not case.get("input_kind"):
            case["input_kind"] = infer_input_kind(
                str(case.get("inputs") or ""),
                str(case.get("tag") or ""),
            )

    rows = _ensure_input_kind_diversity(pattern, rows)
    rows = _ensure_min_tests(pattern, rows)
    return rows


def enrich_all_suites(suites: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    return {pattern: enrich_test_suite(pattern, cases) for pattern, cases in suites.items()}
