"""Input-matrix taxonomy and validation for v128 test cases."""

from __future__ import annotations

from typing import Any, Literal

TestTag = Literal[
    "typical",
    "boundary_min",
    "boundary_max",
    "boundary",
    "zero_empty",
    "negative",
    "not_found",
    "invalid",
    "single",
    "all_equal",
    "duplicate",
    "edge_order",
    "contrast",
]

InputKind = Literal[
    "scalar",
    "array",
    "matrix",
    "string",
    "pairs",
    "commands",
    "graph",
    "file_sim",
    "placeholder_demo",
    "placeholder_empty",
    "placeholder_edge",
]

ALLOWED_TAGS: frozenset[str] = frozenset(
    {
        "typical",
        "boundary_min",
        "boundary_max",
        "boundary",
        "zero_empty",
        "negative",
        "not_found",
        "invalid",
        "single",
        "all_equal",
        "duplicate",
        "edge_order",
        "contrast",
    }
)

ALLOWED_INPUT_KINDS: frozenset[str] = frozenset(
    {
        "scalar",
        "array",
        "matrix",
        "string",
        "pairs",
        "commands",
        "graph",
        "file_sim",
        "placeholder_demo",
        "placeholder_empty",
        "placeholder_edge",
    }
)

# Expansion scaffold slots (files/OOP chapters) keep demo/empty/edge starters
PLACEHOLDER_SCAFFOLD_PATTERNS: frozenset[str] = frozenset(
    {f"task_{n:03d}" for n in list(range(81, 109)) + list(range(113, 129)) + list(range(169, 193))}
)

MIN_TESTS_DEFAULT = 4
MIN_TESTS_SCAFFOLD = 5  # 3 placeholders + >=2 typed
MIN_TESTS_CAPSTONE = 5

CAPSTONE_PATTERNS: frozenset[str] = frozenset(
    {
        f"task_{n:03d}"
        for n in (
            8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128,
        )
    }
)

PLACEHOLDER_OUTPUTS = frozenset({"ok", "7", "excellent", "retry", "demo"})
PLACEHOLDER_INPUT_MARKERS = ("demo", "empty", "edge")


def tc(
    tag: TestTag,
    inputs: str,
    output: str,
    *,
    input_kind: InputKind | str = "",
    note_ru: str = "",
) -> dict[str, str]:
    """Build one tagged test case (inputs must end with newline)."""
    raw_in = str(inputs)
    if raw_in and not raw_in.endswith("\n"):
        raw_in += "\n"
    row: dict[str, str] = {"tag": tag, "inputs": raw_in, "output": str(output)}
    kind = str(input_kind or "").strip()
    if kind:
        row["input_kind"] = kind
    if note_ru.strip():
        row["note_ru"] = note_ru.strip()
    return row


def placeholder_trio() -> list[dict[str, str]]:
    """Beginner scaffold: compile/run smoke tests before real I/O."""
    return [
        tc("typical", "demo\n", "ok", input_kind="placeholder_demo"),
        tc("zero_empty", "empty\n", "ok", input_kind="placeholder_empty"),
        tc("boundary", "edge\n", "ok", input_kind="placeholder_edge"),
    ]


def stdin_lines(*lines: str | int) -> str:
    return "\n".join(str(x) for x in lines) + "\n"


def stdin_tokens(*tokens: str | int) -> str:
    return " ".join(str(t) for t in tokens) + "\n"


def is_placeholder_test(case: dict[str, Any]) -> bool:
    out = str(case.get("output") or "").strip()
    inp = str(case.get("inputs") or "")
    kind = str(case.get("input_kind") or "")
    if kind.startswith("placeholder_"):
        return True
    if out == "7" and inp.strip().startswith("3\n7\n2"):
        return True
    if out in PLACEHOLDER_OUTPUTS and any(m in inp for m in PLACEHOLDER_INPUT_MARKERS):
        return True
    return False


def infer_input_kind(inputs: str, tag: str = "") -> str:
    """Heuristic input shape from stdin text."""
    raw = str(inputs or "")
    stripped = raw.strip()
    if not stripped:
        return "file_sim"
    first = stripped.split("\n", 1)[0].strip()
    if first in ("demo", "empty", "edge") or str(tag).startswith("placeholder"):
        return f"placeholder_{first}" if first in ("demo", "empty", "edge") else "placeholder_demo"

    lines = [ln for ln in raw.split("\n") if ln != ""]
    if not lines:
        return "file_sim"

    head_tokens = first.split()
    if len(head_tokens) == 2 and all(t.lstrip("-").isdigit() for t in head_tokens):
        rows, cols = int(head_tokens[0]), int(head_tokens[1])
        body = lines[1:]
        if rows > 0 and cols > 0 and len(body) >= rows:
            return "matrix"
        if len(head_tokens) == 2 and any(c.isalpha() for c in first):
            return "graph"

    if len(head_tokens) == 2 and all(t.lstrip("-").isdigit() for t in head_tokens) and len(lines) > 1:
        n = int(head_tokens[0])
        if len(lines) == n + 1 or (len(lines) >= 2 and len(head_tokens) == 2):
            return "array"

    if len(head_tokens) == 1 and head_tokens[0].isdigit() and len(lines) > 1:
        n = int(head_tokens[0])
        if len(lines) == n + 1:
            return "array"

    if any(ch.isalpha() for ch in first) and not first.split()[0].isdigit():
        lower = first.lower()
        if lower.split()[0] in {"push", "pop", "enqueue", "dequeue", "add", "do", "undo", "visit", "print", "run"}:
            return "commands"
        if "," in first or " " in first and any(c.isdigit() for c in first):
            return "pairs"
        return "string"

    if len(head_tokens) <= 3 and all(t.lstrip("-").replace(".", "", 1).isdigit() for t in head_tokens):
        return "scalar"

    return "array"


def validate_test_suite(pattern: str, tests: list[dict[str, Any]]) -> list[str]:
    """Return human-readable validation errors for one task's test matrix."""
    errors: list[str] = []
    is_scaffold = pattern in PLACEHOLDER_SCAFFOLD_PATTERNS
    min_count = (
        MIN_TESTS_SCAFFOLD
        if is_scaffold
        else (MIN_TESTS_CAPSTONE if pattern in CAPSTONE_PATTERNS else MIN_TESTS_DEFAULT)
    )
    if len(tests) < min_count:
        errors.append(f"need>={min_count} tests, got {len(tests)}")

    tags: set[str] = set()
    kinds: set[str] = set()
    for idx, case in enumerate(tests):
        tag = str(case.get("tag") or "").strip()
        if not tag:
            errors.append(f"case[{idx}] missing tag")
        elif tag not in ALLOWED_TAGS:
            errors.append(f"case[{idx}] unknown tag {tag!r}")
        else:
            tags.add(tag)

        kind = str(case.get("input_kind") or infer_input_kind(str(case.get("inputs") or ""), tag))
        if kind not in ALLOWED_INPUT_KINDS:
            errors.append(f"case[{idx}] unknown input_kind {kind!r}")
        kinds.add(kind)

        ph = is_placeholder_test(case)
        if ph and not is_scaffold:
            errors.append(f"case[{idx}] placeholder not allowed on {pattern}")
        if not ph and is_scaffold and kind.startswith("placeholder_"):
            pass
        elif ph and is_scaffold:
            pass
        elif not ph and is_scaffold:
            pass

        inp = str(case.get("inputs") or "")
        if inp and not inp.endswith("\n"):
            errors.append(f"case[{idx}] inputs must end with newline")

    if is_scaffold:
        for pk in ("placeholder_demo", "placeholder_empty", "placeholder_edge"):
            if pk not in kinds:
                errors.append(f"missing beginner placeholder {pk}")
    elif any(is_placeholder_test(t) for t in tests):
        errors.append("unexpected placeholder on non-scaffold task")

    semantic = {k for k in kinds if not k.startswith("placeholder_")}
    if len(semantic) < 2:
        errors.append(f"need>=2 input kinds (scalar/array/matrix/…), got {sorted(semantic)}")

    if tags == {"typical"} and len(tests) >= min_count:
        errors.append("only typical tag — diversify matrix")

    return errors
