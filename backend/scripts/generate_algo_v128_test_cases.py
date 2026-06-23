#!/usr/bin/env python3
"""Generate authoritative test cases for 128 algo-syntax tasks."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.content.v4_code_format import format_reference_code

OUT = BACKEND / "scripts" / "algo_task_test_cases.py"
COURSE_JSON = BACKEND / "algo_syntax_course.json"
MIN_CASES = 3


def _wrap_pascal(code: str) -> str:
    text = str(code or "").strip()
    if not text:
        return ""
    if re.search(r"\bprogram\b", text, re.I):
        return text
    return f"program Demo;\n{text}\nend."


def _readln_count(code: str) -> int:
    return len(re.findall(r"\breadln\b", code, re.I))


def _uses_space_separated_reads(code: str) -> bool:
    return bool(re.search(r"readln\s*\(\s*\w+\s*,", code, re.I))


def _input_variants(code: str, task_num: int) -> list[str]:
    if _uses_space_separated_reads(code):
        pools = [
            "5 12 8 3 12 5 9",
            "3 7 1 2 3",
            "4 5 5 5 1 2",
            "3 7 2",
            "1 10",
            "4 -5 -1 -8 -2",
        ]
    else:
        count = max(1, _readln_count(code))
        pools = []
        base_sets = [
            ["5", "2", "9", "1", "7", "4"],
            ["1", "10"],
            ["4", "-5", "10", "-2", "1"],
            ["5", "40", "18", "25", "60", "19"],
            ["3", "7", "2"],
            ["4", "100", "90", "120", "80"],
            ["5", "100", "-20", "0", "50", "-1"],
            ["abba"],
            ["abc"],
            ["aaabb"],
            ["hello world"],
            ["18", "25", "40", "19", "22"],
        ]
        for values in base_sets:
            if len(values) >= count:
                pools.append(" ".join(values[:count]))
                pools.append("\n".join(values[:count]) + "\n")
    seen: list[str] = []
    for item in pools:
        if item not in seen:
            seen.append(item)
    if len(seen) < MIN_CASES:
        seen.extend([f"{task_num + idx}" for idx in range(MIN_CASES - len(seen))])
    return seen


def _measure_with_docker(core, code: str, inputs: str) -> str | None:
    try:
        rows = core.run_tests("pascal", code, [{"inputs": inputs, "output": "__measure__"}])
    except Exception:
        return None
    if not rows:
        return None
    row = rows[0]
    if row.status not in {"PASSED", "FAILED"}:
        return None
    actual = str(row.actual or "").strip()
    if actual == "(пустой вывод)":
        return ""
    if actual.lower().startswith("error:") or "Compilation aborted" in actual:
        return None
    return actual


def _simulate_output(code: str, inputs: str) -> str | None:
    """Best-effort stdout prediction for common Pascal IO patterns."""
    text = _wrap_pascal(format_reference_code(code, "pascal"))
    if not text:
        return None
    raw = str(inputs or "")
    tokens = [part for part in re.split(r"\s+", raw.strip()) if part]
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

    if re.search(r"writeln\s*\(\s*['\"]yes['\"]", text, re.I):
        if "abba" in raw.lower():
            s = raw.strip()
            return "yes" if s == s[::-1] and s else "no"
        if tokens and all(part.isdigit() or re.match(r"^-?\d+$", part) for part in tokens):
            nums = [int(part) for part in tokens]
            if len(nums) >= 2:
                return "yes" if len(set(nums)) < len(nums) else "no"

    if re.search(r"writeln\s*\(\s*['\"]no['\"]", text, re.I) and "abba" in raw.lower():
        s = raw.strip()
        return "yes" if s == s[::-1] else "no"

    if re.search(r"writeln\s*\(\s*['\"]freezing['\"]", text, re.I) and tokens:
        t = int(tokens[0])
        if t < 0:
            return "freezing"
        if t <= 25:
            return "normal"
        return "hot"

    if re.search(r"writeln\s*\(\s*['\"]excellent['\"]", text, re.I) and tokens:
        score = int(tokens[0])
        if score >= 90:
            return "excellent"
        if score >= 75:
            return "good"
        if score >= 60:
            return "satisfactory"
        return "fail"

    if re.search(r"readln\s*\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)", text, re.I) and len(tokens) >= 3:
        if not all(re.match(r"^-?\d+$", t) for t in tokens[:3]):
            return None
        a, b, c = int(tokens[0]), int(tokens[1]), int(tokens[2])
        if "< best" in text or "ping < best" in text or "minimum" in text.lower():
            return str(min(a, b, c))
        return str(max(a, b, c))

    if "readln(n" in text.lower() and tokens:
        if not re.match(r"^-?\d+$", tokens[0]):
            return None
        n = int(tokens[0])
        rest = [int(x) for x in tokens[1:]]
        if "writeln(total" in text.replace(" ", "").lower() or "total :=" in text.lower():
            if len(rest) >= n:
                return str(sum(rest[:n]))
        if "best" in text.lower() and "score > best" in text.lower():
            if len(rest) >= n:
                return str(max(rest[:n]))
        if "ping < best" in text.lower() or ("best" in text.lower() and "< best" in text.lower()):
            if len(rest) >= n:
                return str(min(rest[:n]))
        if "count" in text.lower() and "> 0" in text:
            if len(rest) >= n:
                return str(sum(1 for x in rest[:n] if x > 0))
        if "average" in text.lower() or "total div n" in text.lower() or "total / n" in text.lower():
            if len(rest) >= n:
                return str(sum(rest[:n]) // n)
        if "position" in text.lower() or "target" in text.lower():
            target = rest[0] if rest else 0
            arr = rest[1 : 1 + n] if len(rest) > 1 else rest
            for idx, value in enumerate(arr, start=1):
                if value == target:
                    return str(idx)
            return "0"

    if lines and len(lines) == 1 and lines[0].isdigit() and "fact(" in text.lower():
        n = int(lines[0])
        out = 1
        for i in range(2, n + 1):
            out *= i
        return str(out)

    if tokens and all(re.match(r"^-?\d+$", t) for t in tokens):
        nums = [int(t) for t in tokens]
        if len(nums) >= 2 and "writeln" in text.lower():
            if "sum" in text.lower() or "+" in text:
                return str(sum(nums))
            if len(nums) == 3:
                return str(max(nums))
    return None


def _build_cases(task: dict, core) -> list[dict[str, str]]:
    refs = task.get("reference_codes") or {}
    raw = str(refs.get("pascal") or "").strip()
    code = _wrap_pascal(format_reference_code(raw, "pascal"))
    if not code.strip():
        return []

    task_num = int(task.get("task_num") or 0)
    cases: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for inputs in _input_variants(code, task_num):
        output = None
        if core is not None:
            output = _measure_with_docker(core, code, inputs)
        if output is None:
            output = _simulate_output(raw, inputs)
        if output is None:
            continue
        key = (inputs, output)
        if key in seen:
            continue
        seen.add(key)
        cases.append({"inputs": inputs, "output": output})
        if len(cases) >= MIN_CASES + 1:
            break

    if len(cases) < MIN_CASES:
        seed = task.get("test_cases") or []
        for item in seed:
            if not isinstance(item, dict):
                continue
            key = (str(item.get("inputs", "")), str(item.get("output", "")))
            if key in seen:
                continue
            seen.add(key)
            cases.append({"inputs": key[0], "output": key[1]})
            if len(cases) >= MIN_CASES:
                break
    return cases[: max(MIN_CASES, len(cases))]


def _write_module(cases_by_num: dict[int, list[dict[str, str]]]) -> None:
    lines = [
        '"""Authoritative test cases for the 128-task algorithm-syntax course."""',
        "from __future__ import annotations",
        "",
        "TEST_CASES_BY_NUM: dict[int, list[dict[str, str]]] = {",
    ]
    for num in sorted(cases_by_num):
        encoded = json.dumps(cases_by_num[num], ensure_ascii=False, indent=4)
        indented = "\n".join(f"    {line}" for line in encoded.splitlines())
        lines.append(f"    {num}: {indented},")
    lines.extend(
        [
            "}",
            "",
            "",
            "def test_cases_for_task(task_num: int) -> list[dict[str, str]]:",
            "    raw = TEST_CASES_BY_NUM.get(int(task_num)) or []",
            "    return [dict(item) for item in raw if isinstance(item, dict)]",
            "",
        ]
    )
    OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not COURSE_JSON.is_file():
        print(f"Missing {COURSE_JSON}; run build_algorithm_syntax_course_from_docx.py first")
        return 1

    tasks = json.loads(COURSE_JSON.read_text(encoding="utf-8"))
    core = None
    try:
        from infrastructure.execution.execution_core import ExecutionCore
        from infrastructure.execution.execution_guard import mark_worker_context

        mark_worker_context()
        core = ExecutionCore()
        _measure_with_docker(core, "program P; begin writeln(1); end.", "")
    except Exception as exc:
        print(f"Docker execution unavailable, using simulator fallback: {exc}")
        core = None

    cases_by_num: dict[int, list[dict[str, str]]] = {}
    failures: list[str] = []

    for task in sorted(tasks, key=lambda item: int(item.get("task_num") or 0)):
        num = int(task["task_num"])
        cases = _build_cases(task, core)
        if len(cases) < MIN_CASES:
            failures.append(f"task {num}: only {len(cases)} cases")
            seed = task.get("test_cases") or []
            if seed:
                cases = list(seed)[:MIN_CASES]
        cases_by_num[num] = cases

    _write_module(cases_by_num)
    print(f"Wrote {len(cases_by_num)} task case sets -> {OUT}")
    if failures:
        print(f"Warnings ({len(failures)}):")
        for item in failures[:15]:
            print(" ", item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
