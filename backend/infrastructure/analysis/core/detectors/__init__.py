"""Six structure checks — explicit list (no auto-discovery)."""
from __future__ import annotations

from collections.abc import Callable
from importlib import import_module

from tree_sitter import Tree

from infrastructure.analysis.core.detectors import assignment, call, condition, function, loop

_return = import_module("infrastructure.analysis.core.detectors.return")

StructureCheck = Callable[[Tree], bool]

ALL_DETECTORS: tuple[tuple[str, StructureCheck], ...] = (
    (loop.STRUCTURE_ID, loop.detect),
    (function.STRUCTURE_ID, function.detect),
    (call.STRUCTURE_ID, call.detect),
    (condition.STRUCTURE_ID, condition.detect),
    (_return.STRUCTURE_ID, _return.detect),
    (assignment.STRUCTURE_ID, assignment.detect),
)

STRUCTURE_IDS: frozenset[str] = frozenset(name for name, _ in ALL_DETECTORS)
