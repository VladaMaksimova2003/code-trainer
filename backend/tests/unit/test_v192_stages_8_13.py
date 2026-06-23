"""Stages 8–13: seed readiness, demo docs sync, pitfall bindings, coverage gate."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_validate_pitfall_coverage_high_priority():
    from validate_pitfall_coverage import run_validation

    assert run_validation(strict_high_priority=True) == 0


def test_task_027_list_vs_static_array_binding():
    from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta

    meta = resolve_v128_transfer_meta("task_027")
    assert meta.get("pitfall_id") == "list_vs_static_array"
    assert meta.get("transfer_type") == "AFCC"


def test_task_187_exception_model_binding():
    from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta

    meta = resolve_v128_transfer_meta("task_187")
    assert meta.get("pitfall_id") == "exception_model"
    assert meta.get("transfer_type") == "ATCC"


def test_task_027_contrast_overlay():
    from algo_v128_catalog import ALGO_SYNTAX_META

    tests = (ALGO_SYNTAX_META.get("task_027") or {}).get("test_cases") or []
    assert tests
    assert tests[0].get("mplt_contrast") is True


def test_validate_defense_demo_slots_includes_stage11_slots():
    from validate_defense_demo_slots import DEMO_SLOTS

    slots = {row["slot"] for row in DEMO_SLOTS}
    assert "pas_004" in slots
    assert "pas_027" in slots
    assert "pas_187" in slots
    assert "pas_006" in slots
