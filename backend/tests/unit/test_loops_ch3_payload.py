"""Chapter-3 (loops) payload: metadata, kinds, Python reference vs tests."""

from __future__ import annotations

import importlib
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[2]
SCRIPTS = BACKEND / "scripts"
for p in (BACKEND, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from loops_ch3_user_payload import (  # noqa: E402
    CH3_TASK_META,
    TASKS,
    _KIND_BY_PATTERN,
    build_tasks,
)


def _run_python(code: str, stdin: str) -> str:
    buf = io.StringIO()
    ns: dict = {}
    old_in = sys.stdin
    try:
        sys.stdin = io.StringIO(stdin)
        with redirect_stdout(buf):
            exec(compile(code, "<ref>", "exec"), ns, ns)
    finally:
        sys.stdin = old_in
    return buf.getvalue().strip()


def _reference_code(mod, kind: str) -> str:
    if kind == "debug":
        return mod.FIXED_PYTHON
    return mod.PYTHON


@pytest.mark.parametrize("task_num", range(17, 25))
def test_loops_ch3_python_reference_matches_tests(task_num: int) -> None:
    pattern = f"task_{task_num:03d}"
    task = next(t for t in build_tasks() if t["pattern_id"] == pattern)
    mod = importlib.import_module(f"ch3_user_codes.task_{task_num:03d}")
    kind = _KIND_BY_PATTERN[pattern]
    code = _reference_code(mod, kind)

    for idx, tc in enumerate(task["tests"], start=1):
        actual = _run_python(code, str(tc["inputs"]))
        expected = str(tc["output"]).strip()
        assert actual == expected, f"{pattern} test #{idx}: got {actual!r}, want {expected!r}"


def test_loops_ch3_no_placeholder_descriptions() -> None:
    for pattern, meta in CH3_TASK_META.items():
        goal = meta["goal"]
        assert "обрабатывает последовательность значений" not in goal
        assert goal.strip()


def test_loops_ch3_kinds_match_catalog_action() -> None:
    expected = {
        "task_017": "assemble",
        "task_018": "assemble",
        "task_019": "translation",
        "task_020": "debug",
        "task_021": "assemble",
        "task_022": "debug",
        "task_023": "debug",
        "task_024": "translation",
    }
    assert _KIND_BY_PATTERN == expected


def test_loops_ch3_task_count() -> None:
    assert len(TASKS) == 8
