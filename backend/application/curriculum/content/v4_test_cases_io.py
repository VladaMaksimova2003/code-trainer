"""Normalize docx-style test inputs for line-based stdin (display + execution)."""

from __future__ import annotations

import re
from typing import Any

# Explicit stdin layouts for patterns where goal/reference heuristics disagree.
STDIN_LAYOUT_BY_PATTERN: dict[str, str] = {
    "task_002": "count_target_line",
    "task_018": "count_target_line",
    "task_022": "count_target_line",
    "task_026": "count_k_line",
    "task_027": "count_pos_line",
    "task_028": "count_pos_value_lines",
    "task_029": "count_pos_value_lines",
    "task_129": "single_line",
}

_COUNT_TARGET_LINE_PATTERNS = frozenset({"task_002", "task_018", "task_022"})


def _tokenize_compact(raw: str) -> list[str]:
    return [part for part in str(raw or "").split() if part]


def _as_count(token: str, fallback: int) -> int:
    try:
        return int(token)
    except ValueError:
        return fallback


def infer_stdin_layout(
    pattern_id: str = "",
    *,
    reference_code: str = "",
    pascal_code: str = "",
    goal: str = "",
) -> str:
    """Infer how stdin tokens should be grouped into lines for students."""
    pid = str(pattern_id or "").strip()
    explicit = STDIN_LAYOUT_BY_PATTERN.get(pid)
    if explicit:
        return explicit

    pascal = str(pascal_code or "")
    python = str(reference_code or "")
    code = pascal if pascal.strip() else python
    g = str(goal or "").lower()

    if re.search(r"readln\s*\(\s*n\s*,\s*target", code, re.I) or (
        "первой строке" in g and "искомый код" in g
    ):
        return "count_target_line"
    if re.search(r"readln\s*\(\s*n\s*,\s*k\s*\)", code, re.I) or re.search(
        r"\bn,\s*k\b", g
    ):
        return "count_k_line"
    if "затем искомое значение" in g and pid not in _COUNT_TARGET_LINE_PATTERNS:
        return "count_values_query"
    if "стоп-значения 0" in g or "пока не встретите 0" in g or "до появления стоп" in g:
        return "lines_all"
    if re.search(r"дано целое\s+n", g) or pid == "task_129":
        return "single_line"

    readln_match = re.search(r"readln\s*\(\s*([^)]+)\s*\)", code, re.I)
    if readln_match:
        args = [part.strip() for part in readln_match.group(1).split(",") if part.strip()]
        if len(args) == 1 and args[0].lower() == "n":
            if re.search(r"for\s+i\s*:=\s*1\s+to\s+n", code, re.I):
                return "count_then_lines"
        if 2 <= len(args) <= 6 and all(re.fullmatch(r"[a-z_]\w*", a, re.I) for a in args):
            return f"first_line_{len(args)}"

    split_match = re.search(
        r"^([a-z_][\w]*(?:\s*,\s*[a-z_][\w]*)+)\s*=\s*map\([^)]+\)\s*,\s*input\(\)\.split\(\)",
        python,
        re.M | re.I,
    )
    if split_match:
        count = len([x.strip() for x in split_match.group(1).split(",") if x.strip()])
        if count >= 2:
            return f"first_line_{count}"

    if re.search(r"n\s*=\s*int\(input\(\)\)", python) and re.search(
        r"\[int\(input\(\)\)\s+for\s+_+\s+in\s+range\(n\)\]", python
    ):
        return "count_then_lines"
    if re.search(r"n\s*=\s*int\(input\(\)\)", python) and "range(n)" in python:
        return "count_then_lines"
    if re.search(r"while\s+.*!=\s*0", python):
        return "lines_all"
    if python.count("int(input())") == 1 and "for " not in python and "while " not in python:
        return "single_line"
    if re.search(r"количество", g) or re.search(r"вводится количество", g):
        return "count_then_lines"
    if re.search(r"три целых числа", g) or re.search(r"три стороны", g):
        return "first_line_3"
    if re.search(r"день.*месяц.*год", g):
        return "first_line_3"
    return ""


def format_stdin_layout(layout: str, parts: list[str]) -> str:
    """Format flat tokens into multiline stdin using a layout kind."""
    if not parts:
        return ""
    if layout == "single_line":
        return parts[0] + "\n"
    if layout == "lines_all":
        return "\n".join(parts) + "\n"
    if layout.startswith("first_line_"):
        k = int(layout.split("_")[-1])
        if len(parts) <= k:
            return " ".join(parts) + "\n"
        head = " ".join(parts[:k])
        rest = parts[k:]
        if not rest:
            return head + "\n"
        return head + "\n" + "\n".join(rest) + "\n"
    if layout == "count_target_line":
        if len(parts) < 2:
            return "\n".join(parts) + "\n"
        n = _as_count(parts[0], max(len(parts) - 2, 0))
        head = f"{parts[0]} {parts[1]}"
        body = parts[2 : 2 + n]
        return head + "\n" + "\n".join(body) + "\n"
    if layout == "count_k_line":
        if len(parts) < 2:
            return "\n".join(parts) + "\n"
        n = _as_count(parts[0], max(len(parts) - 2, 0))
        head = f"{parts[0]} {parts[1]}"
        body = parts[2 : 2 + n]
        return head + "\n" + "\n".join(body) + "\n"
    if layout == "count_then_lines":
        n = _as_count(parts[0], max(len(parts) - 1, 0))
        body = parts[1 : 1 + n]
        return str(parts[0]) + "\n" + "\n".join(body) + "\n"
    if layout == "count_values_query":
        n = _as_count(parts[0], max(len(parts) - 2, 0))
        body = parts[1 : 1 + n]
        tail = parts[1 + n :]
        lines = [str(parts[0]), *body]
        if tail:
            lines.append(tail[0])
        return "\n".join(lines) + "\n"
    if layout == "count_pos_line":
        if len(parts) < 2:
            return "\n".join(parts) + "\n"
        n = _as_count(parts[0], max(len(parts) - 2, 0))
        pos = parts[1 + n] if len(parts) > 1 + n else parts[-1]
        body = parts[1 : 1 + n]
        return str(parts[0]) + "\n" + "\n".join(body) + f"\n{pos}\n"
    if layout == "count_pos_value_lines":
        if len(parts) < 3:
            return "\n".join(parts) + "\n"
        n = _as_count(parts[0], max(len(parts) - 3, 0))
        body = parts[1 : 1 + n]
        tail = parts[1 + n :]
        lines = [str(parts[0]), *body, *tail]
        return "\n".join(lines) + "\n"
    return "\n".join(parts) + "\n"


def _apply_leading_count_heuristic(tokens: list[str], reference_code: str) -> list[str]:
    """When docx lists N numbers but code reads ``n`` then ``n`` values (``range(n)``)."""
    if len(tokens) < 2:
        return tokens
    text = str(reference_code or "")
    if not re.search(r"\binput\s*\(", text, re.I):
        return tokens
    if not re.search(r"range\s*\(\s*n\s*\)", text, re.I):
        return tokens
    try:
        first = int(tokens[0])
    except ValueError:
        return tokens
    if first != len(tokens):
        return tokens
    n = len(tokens) - 1
    return [str(n)] + tokens[1:]


def stdin_tokens_to_lines(raw: str, reference_code: str = "") -> str:
    """Convert compact docx inputs to one token per line for ``input()`` / ``readln``."""
    text = str(raw or "")
    if not text.strip():
        return text
    if "\n" in text:
        return text if text.endswith("\n") else text + "\n"
    tokens = _tokenize_compact(text)
    if not tokens:
        return text
    tokens = _apply_leading_count_heuristic(tokens, reference_code)
    return "\n".join(tokens) + "\n"


def normalize_test_case_inputs(
    raw: str,
    reference_code: str = "",
    language: str = "",
    *,
    pattern_id: str = "",
    pascal_code: str = "",
    goal: str = "",
) -> str:
    """Normalize a single test-case input string for execution/storage/display."""
    _ = language
    text = str(raw or "")
    if not text.strip():
        return text
    layout = infer_stdin_layout(
        pattern_id,
        reference_code=reference_code,
        pascal_code=pascal_code,
        goal=goal,
    )
    if layout:
        formatted = format_stdin_layout(layout, _tokenize_compact(text))
        return formatted if formatted.endswith("\n") else formatted + "\n"
    return stdin_tokens_to_lines(text, reference_code)


def normalize_pattern_test_cases(
    cases: list[dict[str, Any]],
    *,
    pattern_id: str = "",
    reference_code: str = "",
    pascal_code: str = "",
    goal: str = "",
) -> list[dict[str, Any]]:
    """Normalize inputs for every case in a pattern suite."""
    normalized: list[dict[str, Any]] = []
    for case in cases or []:
        if not isinstance(case, dict):
            continue
        row = dict(case)
        row["inputs"] = normalize_test_case_inputs(
            str(row.get("inputs", row.get("input", ""))),
            reference_code,
            "",
            pattern_id=pattern_id,
            pascal_code=pascal_code,
            goal=goal,
        )
        normalized.append(row)
    return normalized


def normalize_test_cases_list(
    cases: list[dict],
    *,
    reference_code: str = "",
    language: str = "",
    pattern_id: str = "",
    pascal_code: str = "",
    goal: str = "",
) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for case in cases or []:
        if not isinstance(case, dict):
            continue
        inputs = str(case.get("inputs", case.get("input", "")))
        output = str(case.get("output", case.get("expected_output", "")))
        normalized.append(
            {
                "inputs": normalize_test_case_inputs(
                    inputs,
                    reference_code,
                    language,
                    pattern_id=pattern_id,
                    pascal_code=pascal_code,
                    goal=goal,
                ),
                "output": output,
            }
        )
    return normalized


def count_static_stdin_reads(code: str, language: str) -> int:
    """Best-effort count of stdin reads for Pascal/Python line-based tasks."""
    text = str(code or "")
    lang = str(language or "python").strip().lower()
    if lang == "pascal":
        return len(re.findall(r"\breadln\b", text, re.I))
    if lang == "python":
        return len(re.findall(r"\binput\s*\(", text, re.I))
    if lang in {"csharp", "cs", "c#"}:
        return len(re.findall(r"\bReadLine\s*\(", text, re.I))
    if lang == "java":
        return len(re.findall(r"\bnext(?:Int|Line|Double)\s*\(", text, re.I))
    if lang == "cpp":
        return len(re.findall(r">>", text))
    return 0
