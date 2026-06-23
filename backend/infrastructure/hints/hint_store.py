"""Deprecated facade — use StructureHintResolver directly."""
from __future__ import annotations

from application.hints.structure_hint_resolver import StructureHintResolver
from domain.hints.structure_hint import StructureHintRecord
from infrastructure.repositories.hints.structure_hint_repository import (
    StructureHintRepository,
)


class HintStore:
    def __init__(self, repository: StructureHintRepository | None = None) -> None:
        self._resolver = StructureHintResolver(repository)

    def get(self, structure_type: str, subtype: str) -> StructureHintRecord:
        return self._resolver.resolve(structure_type, subtype)

    def list_merged(self) -> list[StructureHintRecord]:
        return self._resolver.list_resolved()

    def catalog(self) -> dict[str, list[str]]:
        return self._resolver.catalog()
