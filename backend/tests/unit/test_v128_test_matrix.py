"""Tests for v128 test matrix overlays."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_all_tasks_have_tagged_tests():
    from algo_v128_catalog import ALGO_SYNTAX_META, V128_CORE_TASK_COUNT
    from v128_test_matrix import PLACEHOLDER_SCAFFOLD_PATTERNS

    assert len(ALGO_SYNTAX_META) >= V128_CORE_TASK_COUNT
    for pattern, row in ALGO_SYNTAX_META.items():
        if not pattern.startswith("task_"):
            continue
        tests = row.get("test_cases") or []
        assert len(tests) >= 4, f"{pattern} has {len(tests)} tests"
        assert all(t.get("tag") for t in tests), f"{pattern} missing tags"
        assert all(t.get("input_kind") for t in tests), f"{pattern} missing input_kind"
        if pattern in PLACEHOLDER_SCAFFOLD_PATTERNS:
            kinds = {t["input_kind"] for t in tests}
            assert "placeholder_demo" in kinds
            assert "placeholder_empty" in kinds
            assert "placeholder_edge" in kinds


def test_input_kind_diversity():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for pattern in ("task_001", "task_025", "task_033", "task_081"):
        kinds = {
            t["input_kind"]
            for t in ALGO_SYNTAX_META[pattern]["test_cases"]
            if not str(t["input_kind"]).startswith("placeholder_")
        }
        assert len(kinds) >= 2, f"{pattern} input kinds: {kinds}"


def test_branches_have_diverse_tags():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for n in range(9, 17):
        pattern = f"task_{n:03d}"
        tags = {t["tag"] for t in ALGO_SYNTAX_META[pattern]["test_cases"]}
        assert len(tags) >= 2, f"{pattern} tags too uniform: {tags}"


def test_task_020_028_stage1_tests_preserved():
    from algo_v128_catalog import ALGO_SYNTAX_META

    t20 = ALGO_SYNTAX_META["task_020"]["test_cases"]
    assert any(t["output"] == "6" for t in t20)
    t28 = ALGO_SYNTAX_META["task_028"]["test_cases"]
    assert any("9 2 3" in t["output"] for t in t28)


def test_corrections_override_wrong_suites():
    from algo_v128_catalog import ALGO_SYNTAX_META

    assert ALGO_SYNTAX_META["task_065"]["test_cases"][0]["output"] == "7"
    assert ALGO_SYNTAX_META["task_033"]["test_cases"][0]["output"] == "5"


def test_overlay_validation_mostly_clean():
    from v128_test_overlays import overlay_validation_errors

    errors = overlay_validation_errors()
    assert len(errors) == 0, f"Matrix errors: {list(errors.items())[:3]}"
