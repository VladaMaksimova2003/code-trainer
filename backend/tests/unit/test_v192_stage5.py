"""Stage 5: v192-B expansion wired into v31 task rows and showcase registries."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_build_task_rows_includes_expansion_by_default():
    from algo_v128_catalog import build_task_rows
    from algo_v192_plan import V192_TARGET_TASK_COUNT

    rows = build_task_rows("pas")
    assert len(rows) == V192_TARGET_TASK_COUNT == 192
    assert rows[128][0] == "pas_129"
    assert rows[128][5] == "task_129"
    assert rows[-1][0] == "pas_192"


def test_cpp_task_rows_stay_at_v128_core():
    from algo_v128_catalog import V128_CORE_TASK_COUNT, build_task_rows
    from cpp_v31_tasks import V31_TASKS

    assert len(build_task_rows("cpp", include_expansion=False)) == V128_CORE_TASK_COUNT
    assert len(V31_TASKS) == V128_CORE_TASK_COUNT


def test_pascal_v311_catalog_192(monkeypatch):
    monkeypatch.setenv("COURSE_SCOPE", "192")
    from application.curriculum.course_scope import (
        active_collection_targets,
        active_target_task_count,
        iter_tasks_in_scope,
    )
    from algo_v192_plan import V192_TARGET_TASK_COUNT
    from pascal_v31_tasks import V31_TASKS

    assert active_target_task_count() == V192_TARGET_TASK_COUNT
    assert len(iter_tasks_in_scope(V31_TASKS)) == 192
    assert sum(active_collection_targets().values()) == 192


def test_python_v311_catalog_192(monkeypatch):
    monkeypatch.setenv("COURSE_SCOPE", "192")
    from application.curriculum.course_scope import (
        active_collection_targets,
        active_target_task_count,
        iter_tasks_in_scope,
    )
    from python_v31_tasks import V31_TASKS

    assert active_target_task_count() == 192
    assert len(iter_tasks_in_scope(V31_TASKS)) == 192
    assert sum(active_collection_targets().values()) == 192


def test_expansion_slots_have_algo_meta():
    from algo_v128_catalog import ALGO_SYNTAX_META

    for task_num in range(129, 193):
        key = f"task_{task_num:03d}"
        assert key in ALGO_SYNTAX_META
        meta = ALGO_SYNTAX_META[key]
        assert meta["test_cases"]
        assert meta["chapter_key"]
