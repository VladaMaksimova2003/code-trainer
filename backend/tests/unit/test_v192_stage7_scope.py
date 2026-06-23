"""Stage 7: defense stand scope 128 vs 192-B."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_scope_targets():
    from course_scope import scope_chapter_task_count, scope_collection_targets, scope_target_count

    assert scope_target_count("128") == 128
    assert scope_target_count("192") == 192
    assert scope_chapter_task_count("128") == 8
    assert scope_chapter_task_count("192") == 12
    assert sum(scope_collection_targets("128").values()) == 128
    assert sum(scope_collection_targets("192").values()) == 192


def test_validate_catalog_scope_192():
    from course_scope import validate_catalog_scope

    assert validate_catalog_scope("192") == []


def test_validate_catalog_scope_128():
    from course_scope import validate_catalog_scope

    errors = validate_catalog_scope("128")
    assert errors == [], errors


def test_demo_slots_respect_scope():
    from course_scope import demo_slots_for_scope

    core = demo_slots_for_scope("128")
    full = demo_slots_for_scope("192")
    assert "pas_131" not in core
    assert "pas_131" in full
    assert "pas_006" in core
    assert len(full) >= len(core)


def test_validate_course_scope_runner():
    from validate_course_scope import run_validation

    code, report = run_validation(scope="192", check_db=False)
    assert code == 0
    assert report["catalog_errors"] == []
    assert report["scope"]["target_tasks"] == 192
