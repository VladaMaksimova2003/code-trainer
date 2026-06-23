#!/usr/bin/env python3
"""Measure Pascal reference outputs and write v3.1.1 test-case catalog files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import all_v311_task_records
from application.curriculum.pascal.catalog.pascal_v311_content import _SLOT_TEST_CASES
from application.curriculum.pascal.catalog.pascal_v311_test_case_resolver import (
    MIN_TEST_CASES,
    _NON_EXECUTABLE_FORMATS,
    _debug_solution,
    _ensure_min_test_cases,
    _executable_reference,
    _slot_assembly,
    wrap_pascal_snippet,
)
from infrastructure.execution.execution_core import ExecutionCore

MEASURED_PATH = (
    BACKEND
    / "application"
    / "curriculum"
    / "pascal"
    / "catalog"
    / "pascal_v311_measured_outputs.py"
)
TASK_CASES_PATH = (
    BACKEND
    / "application"
    / "curriculum"
    / "pascal"
    / "catalog"
    / "pascal_v311_task_test_cases.py"
)

_IO_INPUT_POOL = ["5", "0", "-3", "10", "1", "2", "7", "4"]


def _record_row(rec) -> tuple[str, str, str, str, str, str, str, str, str, str]:
    return (
        rec.slot_id,
        rec.chapter_key,
        rec.title,
        rec.task_format,
        rec.primary_action,
        rec.exercise_pattern_id,
        rec.educational_goal,
        rec.pascal_features,
        rec.difficulty,
        rec.legacy_slot_id,
    )


def _normalize_output(value: str | None) -> str | None:
    if value is None:
        return None
    if value == "(пустой вывод)":
        return ""
    return value


def _looks_like_compiler_output(value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    markers = (
        "Free Pascal Compiler",
        "Copyright (c)",
        "Compilation aborted",
        "Error: /usr/bin/ppcx",
    )
    if any(marker in text for marker in markers):
        return True
    lowered = text.lower()
    return lowered.startswith("error:") or lowered.startswith("fatal:")


def _measure(core: ExecutionCore, code: str, inputs: str = "") -> str | None:
    if not code.strip():
        return None
    results = core.run_tests("pascal", code, [{"inputs": inputs, "output": "__measure__"}])
    if not results:
        return None
    row = results[0]
    if row.status not in {"PASSED", "FAILED"}:
        return None
    actual = _normalize_output(str(row.actual or "").strip())
    if actual is None or _looks_like_compiler_output(actual):
        return None
    return actual


def _readln_count(code: str) -> int:
    return len(re.findall(r"\breadln\b", code, re.I))


def _input_variants(read_count: int) -> list[str]:
    if read_count <= 0:
        return ["", "", ""]
    variants: list[str] = []
    for values in (
        _IO_INPUT_POOL,
        list(reversed(_IO_INPUT_POOL)),
        ["1", "2", "3", "4", "5"],
    ):
        for start in range(max(1, len(values) - read_count + 1)):
            chunk = values[start : start + read_count]
            if len(chunk) < read_count:
                continue
            candidate = "\n".join(chunk) + "\n"
            if candidate not in variants:
                variants.append(candidate)
            if len(variants) >= 8:
                return variants
    while len(variants) < MIN_TEST_CASES:
        variants.append("\n".join(["1"] * read_count) + "\n")
    return variants


def _reference_code(rec, row) -> str:
    slot_assembly = _slot_assembly()
    if rec.task_format in {"сборка_программы", "сборка_фрагмента"} and rec.slot_id in slot_assembly:
        code = slot_assembly[rec.slot_id][0]
        if not re.search(r"\bprogram\b", code, re.I):
            return wrap_pascal_snippet(code)
        return code
    if rec.task_format in {"исправление", "поиск_ошибки"}:
        return _debug_solution(rec.slot_id)
    return _executable_reference(row, {})


def _append_measured_case(
    cases: list[dict[str, str]],
    *,
    inputs: str,
    output: str,
) -> None:
    case = {"inputs": inputs, "output": output}
    for existing in cases:
        if existing["inputs"] == case["inputs"] and existing["output"] == case["output"]:
            return
    cases.append(case)


def _build_cases_for_record(rec, core: ExecutionCore) -> list[dict[str, str]]:
    row = _record_row(rec)
    slot_id = rec.slot_id
    cases: list[dict[str, str]] = []

    if rec.task_format in _NON_EXECUTABLE_FORMATS:
        return _ensure_min_test_cases([{"inputs": "", "output": "ok"}])

    slot_assembly = _slot_assembly()
    if rec.task_format in {"сборка_программы", "сборка_фрагмента"} and slot_id in slot_assembly:
        asm_cases = slot_assembly[slot_id][4]
        if asm_cases:
            return _ensure_min_test_cases(list(asm_cases))

    seed = _SLOT_TEST_CASES.get(slot_id, [])
    code = _reference_code(rec, row)

    if seed:
        for raw in seed:
            seed_output = str(raw.get("output", ""))
            measured_out = _measure(core, code, str(raw.get("inputs", "")))
            if measured_out is not None:
                output = measured_out
            else:
                output = seed_output
            _append_measured_case(
                cases,
                inputs=str(raw.get("inputs", "")),
                output=output,
            )

    if rec.task_format == "код_по_блок-схеме" and (
        "positive" in rec.pascal_features or "n > 0" in rec.pascal_features
    ):
        for inp in ("3\n", "-2\n", "0\n"):
            measured_out = _measure(core, code, inp)
            if measured_out is not None:
                _append_measured_case(cases, inputs=inp, output=measured_out)

    if len(cases) < MIN_TEST_CASES:
        read_count = _readln_count(code)
        for inp in _input_variants(read_count):
            measured_out = _measure(core, code, inp)
            if measured_out is None:
                continue
            _append_measured_case(cases, inputs=inp, output=measured_out)
            if len(cases) >= MIN_TEST_CASES + 2:
                break

    if not cases:
        read_count = _readln_count(code)
        for inp in _input_variants(read_count):
            measured_out = _measure(core, code, inp)
            if measured_out is None:
                continue
            _append_measured_case(cases, inputs=inp, output=measured_out)
            if len(cases) >= MIN_TEST_CASES + 2:
                break

    if not cases:
        measured_out = _measure(core, code, "")
        _append_measured_case(
            cases,
            inputs="",
            output=measured_out or "ok",
        )

    return _ensure_min_test_cases(cases)


def _write_measured_outputs(measured: dict[str, str]) -> None:
    lines = [
        '"""Auto-generated Pascal stdout for v3.1.1 reference solutions."""',
        "from __future__ import annotations",
        "",
        "MEASURED_OUTPUTS: dict[str, str] = {",
    ]
    for key in sorted(measured):
        value = json.dumps(measured[key], ensure_ascii=False)
        lines.append(f'    "{key}": {value},')
    lines.append("}")
    lines.append("")
    MEASURED_PATH.write_text("\n".join(lines), encoding="utf-8")


def _write_task_cases(task_cases: dict[str, list[dict[str, str]]]) -> None:
    lines = [
        '"""Auto-generated Pascal test cases for v3.1.1 catalog tasks."""',
        "from __future__ import annotations",
        "",
        "TASK_TEST_CASES_BY_SLOT: dict[str, list[dict[str, str]]] = {",
    ]
    for slot_id in sorted(task_cases):
        encoded = json.dumps(task_cases[slot_id], ensure_ascii=False, indent=4)
        indented = "\n".join(f"    {line}" for line in encoded.splitlines())
        lines.append(f'    "{slot_id}": {indented},')
    lines.append("}")
    lines.append("")
    TASK_CASES_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    core = ExecutionCore()
    measured: dict[str, str] = {}
    task_cases: dict[str, list[dict[str, str]]] = {}

    for rec in all_v311_task_records():
        row = _record_row(rec)
        cases = _build_cases_for_record(rec, core)
        task_cases[rec.slot_id] = cases

        if rec.task_format in _NON_EXECUTABLE_FORMATS:
            continue

        code = _reference_code(rec, row)
        if rec.task_format == "код_по_блок-схеме" and (
            "positive" in rec.pascal_features or "n > 0" in rec.pascal_features
        ):
            for idx, inp in enumerate(("3\n", "-2\n", "0\n")):
                out = _measure(core, code, inp)
                if out is not None:
                    measured[f"{rec.slot_id}::{idx}"] = out
            continue

        primary = cases[0]
        measured[rec.slot_id] = str(primary.get("output", ""))

    _write_measured_outputs(measured)
    _write_task_cases(task_cases)

    counts = {len(v) for v in task_cases.values()}
    print(f"Wrote {len(task_cases)} slots to {TASK_CASES_PATH}")
    print(f"Wrote {len(measured)} measured outputs to {MEASURED_PATH}")
    print(f"Test-case counts: min={min(counts)} max={max(counts)} unique={sorted(counts)}")
    bad = [slot for slot, cases in task_cases.items() if len(cases) < 1]
    if bad:
        print(f"WARNING: {len(bad)} slots without test cases")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
