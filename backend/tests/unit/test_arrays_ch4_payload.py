"""Chapter-4 (arrays) payload: metadata, kinds, Python reference vs tests."""

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

from arrays_ch4_user_payload import (  # noqa: E402
    CH4_TASK_META,
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


@pytest.mark.parametrize("task_num", range(25, 33))
def test_arrays_ch4_python_reference_matches_tests(task_num: int) -> None:
    pattern = f"task_{task_num:03d}"
    task = next(t for t in build_tasks() if t["pattern_id"] == pattern)
    mod = importlib.import_module(f"ch4_user_codes.task_{task_num:03d}")
    kind = _KIND_BY_PATTERN[pattern]
    code = _reference_code(mod, kind)

    for idx, tc in enumerate(task["tests"], start=1):
        actual = _run_python(code, str(tc["inputs"]))
        expected = str(tc["output"]).strip()
        assert actual == expected, f"{pattern} test #{idx}: got {actual!r}, want {expected!r}"


def test_arrays_ch4_no_placeholder_descriptions() -> None:
    for pattern, meta in CH4_TASK_META.items():
        goal = meta["goal"]
        assert "работает с набором чисел" not in goal
        assert goal.strip()


def test_arrays_ch4_kinds_match_catalog_action() -> None:
    expected = {
        "task_025": "assemble",
        "task_026": "assemble",
        "task_027": "translation",
        "task_028": "debug",
        "task_029": "assemble",
        "task_030": "assemble",
        "task_031": "debug",
        "task_032": "translation",
    }
    assert _KIND_BY_PATTERN == expected


def test_arrays_ch4_task_count() -> None:
    assert len(TASKS) == 8


def test_arrays_ch4_overlay_replaces_stale_meta_tests() -> None:
    from application.curriculum.content.algo_syntax_task_extra import ALGO_SYNTAX_META

    for task_num in range(25, 33):
        pattern = f"task_{task_num:03d}"
        tests = ALGO_SYNTAX_META[pattern].get("test_cases") or []
        assert tests, f"{pattern} has no test_cases after overlay"
        assert str(tests[0].get("output")) != "19", f"{pattern} still has placeholder tests"
