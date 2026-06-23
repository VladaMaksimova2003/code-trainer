"""Chapter-5 (strings) payload: metadata, kinds, Python reference vs tests."""

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

from strings_ch5_user_payload import (  # noqa: E402
    CH5_TASK_META,
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


@pytest.mark.parametrize("task_num", range(33, 41))
def test_strings_ch5_python_reference_matches_tests(task_num: int) -> None:
    pattern = f"task_{task_num:03d}"
    task = next(t for t in build_tasks() if t["pattern_id"] == pattern)
    mod = importlib.import_module(f"ch5_user_codes.task_{task_num:03d}")
    kind = _KIND_BY_PATTERN[pattern]
    code = _reference_code(mod, kind)

    for idx, tc in enumerate(task["tests"], start=1):
        actual = _run_python(code, str(tc["inputs"]))
        expected = str(tc["output"]).strip()
        assert actual == expected, f"{pattern} test #{idx}: got {actual!r}, want {expected!r}"


def test_strings_ch5_no_placeholder_descriptions() -> None:
    for pattern, meta in CH5_TASK_META.items():
        goal = meta["goal"]
        assert "анализирует строку" not in goal
        assert goal.strip()


def test_strings_ch5_kinds_match_catalog_action() -> None:
    expected = {
        "task_033": "assemble",
        "task_034": "assemble",
        "task_035": "translation",
        "task_036": "debug",
        "task_037": "assemble",
        "task_038": "assemble",
        "task_039": "debug",
        "task_040": "translation",
    }
    assert _KIND_BY_PATTERN == expected


def test_strings_ch5_task_count() -> None:
    assert len(TASKS) == 8


def test_strings_ch5_overlay_replaces_stale_meta_tests() -> None:
    from application.curriculum.content.algo_syntax_task_extra import ALGO_SYNTAX_META

    for task_num in range(33, 41):
        pattern = f"task_{task_num:03d}"
        tests = ALGO_SYNTAX_META[pattern].get("test_cases") or []
        assert tests, f"{pattern} has no test_cases after overlay"
        first_out = str(tests[0].get("output"))
        assert first_out not in {"19"}, f"{pattern} still has placeholder tests"
        if pattern == "task_033":
            assert first_out == "5"
