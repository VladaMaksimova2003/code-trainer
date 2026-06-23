"""Structure hints — DB overrides YAML via StructureHintResolver (not used in PASS/FAIL)."""
from __future__ import annotations

from typing import Any

from application.hints.structure_hint_resolver import (
    StructureHintResolver,
    normalize_subtype,
)
from infrastructure.hints.hint_loader import load_structure_hints
from infrastructure.repositories.hints.structure_hint_repository import (
    StructureHintRepository,
)


class StructureHintNotFoundError(KeyError):
    pass


class StructureHintService:
    def __init__(self, repository: StructureHintRepository | None = None) -> None:
        self._repository = repository
        self._resolver = StructureHintResolver(repository)

    def get_hint(self, structure_type: str, subtype: str | None = None) -> dict[str, Any]:
        structure = str(structure_type).strip().lower()
        if not self._structure_known(structure):
            sub = normalize_subtype(subtype, structure)
            raise StructureHintNotFoundError(f"{structure}/{sub}")
        return self._resolver.resolve(structure, subtype).to_api_dict()

    def list_hints(self) -> list[dict[str, Any]]:
        return [record.to_admin_dict() for record in self._resolver.list_resolved()]

    def list_structures(self) -> dict[str, list[str]]:
        return self._resolver.catalog()

    def list_hints_for_structure(self, structure_type: str) -> list[dict[str, Any]]:
        structure = str(structure_type).strip().lower()
        if not self._structure_known(structure):
            raise StructureHintNotFoundError(structure)
        catalog = self._resolver.catalog()
        subtypes = catalog.get(structure, [structure])
        return [self.get_hint(structure, subtype) for subtype in subtypes]

    def upsert_hint(
        self,
        *,
        structure_type: str,
        subtype: str,
        difficulty: int,
        explanation: str,
        examples: dict[str, str],
        title: str | None = None,
    ) -> dict[str, Any]:
        if self._repository is None:
            raise RuntimeError("Database repository required for upsert_hint")
        record = self._repository.upsert(
            structure_type=str(structure_type).strip().lower(),
            subtype=normalize_subtype(subtype, structure_type),
            difficulty=int(difficulty),
            explanation=str(explanation),
            examples=_normalize_examples(examples),
            title=title,
        )
        return record.to_admin_dict()

    def delete_hint(self, hint_id: int) -> bool:
        if self._repository is None:
            raise RuntimeError("Database repository required for delete_hint")
        return self._repository.delete_by_id(int(hint_id))

    def _structure_known(self, structure: str) -> bool:
        if structure in load_structure_hints():
            return True
        if self._repository is None:
            return False
        return any(record.structure_type == structure for record in self._repository.list_all())


def _normalize_examples(raw: dict[str, str]) -> dict[str, str]:
    aliases = {"js": "javascript", "py": "python"}
    out: dict[str, str] = {}
    for key, value in raw.items():
        lang = aliases.get(str(key).strip().lower(), str(key).strip().lower())
        out[lang] = str(value)
    return out
