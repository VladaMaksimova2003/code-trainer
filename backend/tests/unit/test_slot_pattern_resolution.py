"""After catalog reorder, slot number and pattern_id can diverge — resolve via slot_pattern_id."""

from __future__ import annotations

from application.curriculum.content.algo_syntax_task_extra import (
    algo_reference_code,
    resolve_slot_pattern_key,
)
from application.curriculum.content.v4_reference_code import get_reference_code


def test_resolve_slot_pattern_key_prefers_slot_pattern_id():
    assert resolve_slot_pattern_key("pas_002", slot_pattern_id="task_001") == "task_001"
    assert resolve_slot_pattern_key("pas_002") == "task_002"


def test_pas_002_maximum_task_uses_task_001_reference_after_reorder():
    code = get_reference_code("pas_002", "pascal", pattern_key="task_001")
    assert "best" in code
    assert "score" in code
    assert "target" not in code


def test_pas_001_linear_search_uses_task_002_reference_after_reorder():
    code = algo_reference_code("pas_001", "pascal", slot_pattern_id="task_002")
    assert "target" in code
    assert "position" in code
