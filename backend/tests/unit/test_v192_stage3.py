"""Tests for v192-B expansion catalog meta (task_129–task_192)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_expansion_meta_in_catalog():
    from algo_v128_catalog import ALGO_SYNTAX_META

    assert "task_129" in ALGO_SYNTAX_META
    assert "task_192" in ALGO_SYNTAX_META
    assert "task_193" not in ALGO_SYNTAX_META
    assert len([k for k in ALGO_SYNTAX_META if k.startswith("task_")]) == 192


def test_expansion_tasks_have_input_kinds():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for n in range(129, 193):
        pattern = f"task_{n:03d}"
        tests = ALGO_SYNTAX_META[pattern]["test_cases"]
        kinds = {t["input_kind"] for t in tests}
        assert len(kinds) >= 2, f"{pattern} kinds={kinds}"
        assert all(t.get("tag") for t in tests)


def test_expansion_catalog_total(monkeypatch):
    monkeypatch.setenv("COURSE_SCOPE", "192")
    from application.curriculum.shared.algo_v128_showcase import (
        curriculum_catalog_tasks_total,
        curriculum_target_tasks_total,
    )

    assert curriculum_catalog_tasks_total() == 192
    assert curriculum_target_tasks_total() == 192


def test_expansion_pitfall_slots():
    from algo_v128_catalog import ALGO_SYNTAX_META

    assert ALGO_SYNTAX_META["task_131"].get("pitfall_id") == "integer_division"
    assert ALGO_SYNTAX_META["task_147"].get("pitfall_id") == "index_1based"
    assert ALGO_SYNTAX_META["task_171"].get("pitfall_id") == "file_text_mode"


def test_expansion_129_144_pascal_cpp_reference():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for n in range(129, 145):
        pattern = f"task_{n:03d}"
        refs = ALGO_SYNTAX_META[pattern]["reference_codes"]
        assert refs["python"].strip()
        assert refs["pascal"].strip()
        assert refs["cpp"].strip()
        assert "writeln" in refs["pascal"] or "write(" in refs["pascal"]
        assert "iostream" in refs["cpp"] or "std::" in refs["cpp"]


def test_expansion_scaffold_placeholders():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for n in (169, 185, 192):
        pattern = f"task_{n:03d}"
        kinds = {t["input_kind"] for t in ALGO_SYNTAX_META[pattern]["test_cases"]}
        assert "placeholder_demo" in kinds, pattern
        assert "placeholder_empty" in kinds, pattern
        assert "placeholder_edge" in kinds, pattern


def test_expansion_debug_pascal_cpp_pairs():
    from algo_v128_catalog import ALGO_SYNTAX_META
    from v192_expansion_debug_cpp_pairs import CPP_DEBUG_PAIRS_129_192
    from v192_expansion_debug_pascal_pairs import PASCAL_DEBUG_PAIRS_129_192

    debug_nums = sorted(set(PASCAL_DEBUG_PAIRS_129_192) | set(CPP_DEBUG_PAIRS_129_192))
    assert debug_nums == sorted(PASCAL_DEBUG_PAIRS_129_192.keys())
    assert debug_nums == sorted(CPP_DEBUG_PAIRS_129_192.keys())

    for n in debug_nums:
        pattern = f"task_{n:03d}"
        row = ALGO_SYNTAX_META[pattern]
        assert row["action"] == "debug", pattern
        for lang in ("pascal", "cpp"):
            impl = row["implementations"][lang]
            buggy = impl["buggy_code"].strip()
            fixed = impl["fixed_code"].strip()
            assert buggy and fixed, pattern
            assert buggy != fixed, f"{pattern} {lang} buggy==fixed"
            assert "// BUG: needs fixing" not in buggy, pattern
