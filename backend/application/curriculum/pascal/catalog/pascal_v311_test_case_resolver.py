"""Resolve executable test cases for Pascal v3.1.1 catalog tasks."""

from __future__ import annotations

import re
from typing import Any

# (slot_id, chapter, title, format, action, pattern, goal, features, difficulty, legacy?)
TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

MIN_TEST_CASES = 3

_PASCAL_PROGRAM = (
    "program Demo;\n"
    "var\n"
    "  x, y: integer;\n"
    "begin\n"
    "  x := 1;\n"
    "  y := x + 1;\n"
    "  writeln(y);\n"
    "end.\n"
)

_PASCAL_SNIPPET = "x := 1;\ny := x + 1;"

_SLOT_REFERENCE: dict[str, str] = {
    "psk_01": "program Demo;\nbegin\n  writeln('Hello, World!');\nend.",
    "psk_02": "program Demo;\nvar x: integer;\nbegin\n  x := 1;\n  writeln(x);\nend.",
    "psk_04": "program Demo;\nbegin\nend.",
    "psk_06": (
        "program Demo;\n"
        "begin\n"
        "  Writeln('start');\n"
        "  Writeln('finish');\n"
        "end."
    ),
    "psk_09": "{ Однострочный }\n(* Многострочный *)",
}
from application.curriculum.pascal.catalog.pascal_v311_capstone_catalog import (  # noqa: E402
    capstone_reference_pascal,
    capstone_starter_pascal,
)

_SLOT_REFERENCE.update(capstone_reference_pascal())
_CAPSTONE_STARTER = capstone_starter_pascal()

# Marker printed by wrapped snippet/fragment programs.
_SNIPPET_PROBE = "ok"

# Formats that do not run through the code+tests pipeline.
_NON_EXECUTABLE_FORMATS = frozenset(
    {
        "выбор_фрагмента",
        "блок-схема_по_коду",
        "поиск_ошибки",
    }
)


def wrap_pascal_snippet(snippet: str) -> str:
    body = str(snippet or "").strip()
    if not body:
        return ""
    if re.search(r"\bprogram\b", body, re.I):
        return body
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    joined = "\n  ".join(lines)
    if not joined.endswith(";"):
        joined = f"{joined};"
    return (
        "program Demo;\n"
        "begin\n"
        f"  {joined}\n"
        f"  writeln('{_SNIPPET_PROBE}');\n"
        "end.\n"
    )


def wrap_pascal_program_body(code: str) -> str:
    """Wrap block-assembly fragments (var/const + begin/end) with program header."""
    body = str(code or "").strip()
    if not body:
        return ""
    if re.search(r"\bprogram\b", body, re.I):
        return body
    if re.search(r"\bbegin\b", body, re.I):
        suffix = "" if body.rstrip().endswith(".") else "\n."
        return f"program Demo;\n{body}{suffix}"
    return wrap_pascal_snippet(body)


def _reference_solution(slot_id: str, _features: str) -> str:
    return _SLOT_REFERENCE.get(slot_id, _PASCAL_SNIPPET)


def _debug_solution(slot_id: str) -> str:
    if slot_id in _SLOT_REFERENCE:
        return _SLOT_REFERENCE[slot_id]
    return (
        "program Demo;\n"
        "var x: integer;\n"
        "begin\n"
        "  x := 1;\n"
        "  writeln(x);\n"
        "end.\n"
    )


def _slot_assembly() -> dict[str, tuple[str, str, list[str], list[int], list[dict[str, str]]]]:
    from application.curriculum.pascal.catalog.pascal_v311_content import _SLOT_ASSEMBLY

    return _SLOT_ASSEMBLY


def _slot_test_case_catalog() -> dict[str, list[dict[str, str]]]:
    try:
        from application.curriculum.pascal.catalog.pascal_v311_task_test_cases import (
            TASK_TEST_CASES_BY_SLOT,
        )

        if TASK_TEST_CASES_BY_SLOT:
            return TASK_TEST_CASES_BY_SLOT
    except ImportError:
        pass

    from application.curriculum.pascal.catalog.pascal_v311_content import _SLOT_TEST_CASES

    return _SLOT_TEST_CASES


def _normalize_test_case(case: dict[str, str]) -> dict[str, str]:
    return {
        "inputs": str(case.get("inputs", "")),
        "output": str(case.get("output", "")),
    }


def _ensure_min_test_cases(
    cases: list[dict[str, str]],
    *,
    min_count: int = MIN_TEST_CASES,
) -> list[dict[str, str]]:
    """Return unique test cases without padding duplicates."""
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw in cases:
        if not raw:
            continue
        case = _normalize_test_case(raw)
        key = (case["inputs"], case["output"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(case)
    return unique


def _executable_reference(row: TaskRow, extra: dict[str, Any] | None = None) -> str:
    slot_id, _chapter, _title, task_format, _action, _pattern, _goal, features, _diff, _legacy = row
    extra = extra or {}
    slot_assembly = _slot_assembly()

    if task_format in {"сборка_программы", "сборка_фрагмента"} and slot_id in slot_assembly:
        return slot_assembly[slot_id][0]

    if task_format in {"исправление", "поиск_ошибки"}:
        return _debug_solution(slot_id)

    if task_format == "перевод_программы":
        ref = extra.get("reference_solution_pascal")
        if ref:
            return str(ref)
        slot_ref = _reference_solution(slot_id, features)
        if re.search(r"\bprogram\b", slot_ref, re.I):
            return slot_ref
        return wrap_pascal_snippet(slot_ref)

    ref = str(extra.get("reference_solution_pascal") or _reference_solution(slot_id, features))
    if task_format == "перевод_фрагмента":
        return wrap_pascal_snippet(ref)
    if task_format == "код_по_блок-схеме":
        if re.search(r"\bprogram\b", ref, re.I):
            return ref
        return wrap_pascal_snippet(ref)
    return ref


def _probe_test_case(code: str, *, inputs: str = "") -> list[dict[str, str]]:
    if not code.strip():
        return []
    if _SNIPPET_PROBE in code and f"writeln('{_SNIPPET_PROBE}')" in code:
        return [{"inputs": inputs, "output": _SNIPPET_PROBE}]
    return [{"inputs": inputs, "output": ""}]


def _measured_flowchart_cases(
    slot_id: str,
    features: str,
    measured: dict[str, str],
) -> list[dict[str, str]]:
    if "positive" not in features and "n > 0" not in features:
        return []
    pos = measured.get(f"{slot_id}::0") or "positive"
    neg = measured.get(f"{slot_id}::1") or "non-positive"
    zero = measured.get(f"{slot_id}::2") or neg
    return [
        {"inputs": "3\n", "output": pos},
        {"inputs": "-2\n", "output": neg},
        {"inputs": "0\n", "output": zero},
    ]


def _derive_test_cases_core(
    row: TaskRow,
    *,
    extra: dict[str, Any] | None = None,
    measured: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    slot_id, _chapter, _title, task_format, _action, _pattern, _goal, features, _diff, _legacy = row
    extra = extra or {}
    measured = measured or {}
    slot_assembly = _slot_assembly()
    catalog = _slot_test_case_catalog()

    if slot_id in catalog and catalog[slot_id]:
        return list(catalog[slot_id])

    # For v4 slots (pas_NNN), look up from v4_test_cases.
    try:
        from application.curriculum.content.v4_test_cases import get_test_cases
        v4 = get_test_cases(slot_id)
        if v4:
            return [{"inputs": inp, "output": out} for inp, out in v4]
    except ImportError:
        pass

    if task_format in _NON_EXECUTABLE_FORMATS:
        return [{"inputs": "", "output": _SNIPPET_PROBE}]

    if task_format in {"сборка_программы", "сборка_фрагмента"} and slot_id in slot_assembly:
        asm_cases = slot_assembly[slot_id][4]
        if asm_cases:
            return list(asm_cases)
        code = slot_assembly[slot_id][0]
        wrapped = wrap_pascal_snippet(code) if not re.search(r"\bprogram\b", code, re.I) else code
        probed = _probe_test_case(wrapped)
        if probed:
            return probed
        fallback = measured.get(slot_id) or "ok"
        return [{"inputs": "", "output": fallback}]

    code = _executable_reference(row, extra)

    if task_format == "перевод_фрагмента":
        return _probe_test_case(code) or [{"inputs": "", "output": _SNIPPET_PROBE}]

    if task_format in {"исправление", "поиск_ошибки"}:
        return _probe_test_case(_debug_solution(slot_id)) or [{"inputs": "", "output": "1"}]

    if task_format == "перевод_программы":
        if slot_id == "psk_01":
            return [{"inputs": "", "output": "Hello, World!"}]
        if slot_id == "psk_04":
            return [{"inputs": "", "output": ""}]
        probed = _probe_test_case(code)
        if probed and probed[0].get("output"):
            return probed
        fallback = measured.get(slot_id)
        if fallback is not None:
            return [{"inputs": "", "output": fallback}]
        return [{"inputs": "", "output": "2"}]

    if task_format == "код_по_блок-схеме":
        flowchart_cases = _measured_flowchart_cases(slot_id, features, measured)
        if flowchart_cases:
            return flowchart_cases
        return _probe_test_case(code) or [{"inputs": "", "output": _SNIPPET_PROBE}]

    probed = _probe_test_case(code)
    if probed:
        return probed
    fallback = measured.get(slot_id)
    if fallback is not None:
        return [{"inputs": "", "output": fallback}]
    return [{"inputs": "", "output": _SNIPPET_PROBE}]


def derive_test_cases(
    row: TaskRow,
    *,
    extra: dict[str, Any] | None = None,
    measured: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    """Build unique test cases for a catalog task (no duplicate padding)."""
    return _derive_test_cases_core(row, extra=extra, measured=measured)
