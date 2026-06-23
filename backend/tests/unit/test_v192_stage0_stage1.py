"""Tests for v192-B plan (stage 0) and stage-1 v128 overlays."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_v192_plan_volume():
    from algo_v192_plan import (
        COURSE_VARIANT,
        V192_EXPANSION_INDEX,
        V192_EXPANSION_TASK_COUNT,
        V192_TARGET_TASK_COUNT,
        build_v192_expansion_index,
    )

    assert COURSE_VARIANT == "192-B"
    assert V192_TARGET_TASK_COUNT == 192
    assert V192_EXPANSION_TASK_COUNT == 64
    assert len(V192_EXPANSION_INDEX) == 64
    assert len(build_v192_expansion_index()) == 64
    assert V192_EXPANSION_INDEX[0]["task_num"] == 129
    assert V192_EXPANSION_INDEX[-1]["task_num"] == 192


def test_branches_ch2_tests_not_placeholder():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for task_num in range(9, 17):
        key = f"task_{task_num:03d}"
        tests = ALGO_SYNTAX_META[key]["test_cases"]
        assert len(tests) >= 3
        outputs = {str(t["output"]) for t in tests}
        assert "7" not in outputs or task_num == 9
        assert "excellent" not in outputs or task_num == 13
        assert "ok" not in outputs


def test_branches_debug_has_distinct_buggy_fixed():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for key in ("task_012", "task_015"):
        impl = ALGO_SYNTAX_META[key]["implementations"]["pascal"]
        buggy = impl["buggy_code"].strip()
        fixed = impl["fixed_code"].strip()
        assert buggy and fixed
        assert buggy != fixed


def test_task_020_tests_fixed():
    from algo_v128_catalog import ALGO_SYNTAX_META

    tests = ALGO_SYNTAX_META["task_020"]["test_cases"]
    assert tests[0]["output"] == "6"
    assert "19" not in {t["output"] for t in tests}


def test_task_028_tests_fixed():
    from algo_v128_catalog import ALGO_SYNTAX_META

    tests = ALGO_SYNTAX_META["task_028"]["test_cases"]
    assert tests[0]["output"] == "1 9 2 3"
    assert "19" not in {t["output"] for t in tests}


def test_showcase_target_total(monkeypatch):
    monkeypatch.setenv("COURSE_SCOPE", "192")
    from application.curriculum.shared.algo_v128_showcase import (
        curriculum_catalog_tasks_total,
        curriculum_target_tasks_total,
    )

    assert curriculum_catalog_tasks_total() == 192
    assert curriculum_target_tasks_total() == 192
