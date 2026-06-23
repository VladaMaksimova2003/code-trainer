"""Structure hints — YAML-backed, separate from grading."""
from __future__ import annotations

import pytest

from application.hints.structure_hint_service import (
    StructureHintNotFoundError,
    StructureHintService,
)


def test_get_hint_lambda_difficulty():
    hint = StructureHintService().get_hint("function", "lambda")
    assert hint["difficulty"] == 3
    assert "Lambda" in hint["title"] or "lambda" in hint["title"].lower()
    assert "python" in hint["examples"]


def test_get_hint_api_contract():
    hint = StructureHintService().get_hint("function", "lambda")
    assert set(hint.keys()) >= {"type", "subtype", "difficulty", "title", "explanation", "examples"}
    assert hint["type"] == "function"
    assert hint["subtype"] == "lambda"
    assert hint["difficulty"] == 3


def test_get_hint_default_subtype():
    hint = StructureHintService().get_hint("return", "return")
    assert hint["type"] == "return"
    assert hint["difficulty"] == 1


def test_missing_hint_raises():
    with pytest.raises(StructureHintNotFoundError):
        StructureHintService().get_hint("unknown", "x")


def test_list_structures_catalog():
    catalog = StructureHintService().list_structures()
    assert "loop" in catalog
    assert "lambda" in catalog["function"]
