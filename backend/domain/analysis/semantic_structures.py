"""Core exam structures vs analytics-only labels."""
from __future__ import annotations

from enum import Enum


class CoreStructure(str, Enum):
    LOOP = "loop"
    FUNCTION = "function"
    CALL = "call"
    CONDITION = "condition"
    RETURN = "return"
    ASSIGNMENT = "assignment"


class AnalyticsStructure(str, Enum):
    TRANSFORMATION = "transformation"
    DATA_FLOW = "data_flow"
    IO_OPERATION = "io_operation"
    RECURSION = "recursion"
    EXPRESSION = "expression"
    ASYNC_FLOW = "async_flow"
    COMPLEXITY_SPIKE = "complexity_spike"


SemanticStructure = CoreStructure


def get_all_structure_ids() -> frozenset[str]:
    from domain.analysis.semantic_core import get_core_structure_ids

    return get_core_structure_ids() | frozenset(s.value for s in AnalyticsStructure)
