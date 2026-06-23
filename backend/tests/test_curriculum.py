"""Curriculum progression — isolated from PASS/FAIL."""
from __future__ import annotations

from application.curriculum.legacy.structure_progression import (
    get_allowed_structures,
    get_level_plan,
    get_next_structure,
    is_structure_allowed,
)


def test_level_2_plan():
    plan = get_level_plan(2)
    assert plan["level"] == 2
    assert "function" in plan["allowed_structures"]
    assert "method" in plan["allowed_structures"]
    assert "lambda" in plan["next_unlock"]


def test_is_structure_allowed():
    assert is_structure_allowed("function", 1) is True
    assert is_structure_allowed("lambda", 1) is False
    assert is_structure_allowed("lambda", 3) is True


def test_get_next_structure():
    nxt = get_next_structure(2)
    assert nxt.get("function") == "lambda"


def test_allowed_includes_core_basics():
    allowed = get_allowed_structures(1)
    assert "condition" in allowed
    assert "return" in allowed

