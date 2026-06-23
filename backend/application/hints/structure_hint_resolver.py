"""Single source of truth per hint: DB row OR YAML row — never merged."""
from __future__ import annotations

from typing import Any

from domain.hints.structure_hint import StructureHintRecord
from infrastructure.hints.hint_loader import load_structure_hints
from infrastructure.repositories.hints.structure_hint_repository import (
    StructureHintRepository,
)

DEFAULT_SUBTYPE = "default"
DEFAULT_DIFFICULTY = 1


def normalize_subtype(subtype: str | None, structure_type: str) -> str:
    if subtype is None or not str(subtype).strip():
        return DEFAULT_SUBTYPE
    return str(subtype).strip().lower()


def normalize_difficulty(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return DEFAULT_DIFFICULTY
    return parsed if parsed >= 1 else DEFAULT_DIFFICULTY


class StructureHintResolver:
    """if DB hint exists → return DB; else → YAML; else → runtime defaults."""

    def __init__(self, repository: StructureHintRepository | None = None) -> None:
        self._repository = repository

    def resolve(
        self,
        structure_type: str,
        subtype: str | None = None,
    ) -> StructureHintRecord:
        structure = str(structure_type).strip().lower()
        sub = normalize_subtype(subtype, structure)

        db_record = self._resolve_db(structure, sub)
        if db_record is not None:
            return db_record

        yaml_record = self._resolve_yaml(structure, sub)
        if yaml_record is not None:
            return yaml_record

        return StructureHintRecord(
            structure_type=structure,
            subtype=sub,
            difficulty=DEFAULT_DIFFICULTY,
            explanation="",
            examples={},
            title=f"{structure.title()} ({sub})",
            source="yaml",
        )

    def list_keys(self) -> list[tuple[str, str]]:
        keys: set[tuple[str, str]] = set()
        for structure, subtypes in load_structure_hints().items():
            for subtype in subtypes:
                keys.add((structure, subtype))
        if self._repository is not None:
            for record in self._repository.list_all():
                keys.add((record.structure_type, record.subtype))
        return sorted(keys)

    def list_resolved(self) -> list[StructureHintRecord]:
        return [self.resolve(structure, subtype) for structure, subtype in self.list_keys()]

    def catalog(self) -> dict[str, list[str]]:
        grouped: dict[str, set[str]] = {}
        for structure, subtype in self.list_keys():
            grouped.setdefault(structure, set()).add(subtype)
        return {structure: sorted(subtypes) for structure, subtypes in sorted(grouped.items())}

    def _resolve_db(self, structure: str, subtype: str) -> StructureHintRecord | None:
        if self._repository is None:
            return None
        for candidate in _subtype_lookup_order(subtype, structure):
            row = self._repository.get_by_type_subtype(structure, candidate)
            if row is not None:
                return row
        return None

    def _resolve_yaml(self, structure: str, subtype: str) -> StructureHintRecord | None:
        hints = load_structure_hints()
        subtypes = hints.get(structure)
        if not subtypes:
            return None
        for candidate in _subtype_lookup_order(subtype, structure):
            entry = subtypes.get(candidate)
            if entry is not None:
                return _yaml_entry_to_record(structure, candidate, entry)
        return None


def _subtype_lookup_order(subtype: str, structure: str) -> tuple[str, ...]:
    ordered: list[str] = []
    for candidate in (subtype, DEFAULT_SUBTYPE, structure):
        if candidate not in ordered:
            ordered.append(candidate)
    return tuple(ordered)


def _yaml_entry_to_record(
    structure: str,
    subtype: str,
    entry: dict[str, Any],
) -> StructureHintRecord:
    examples = entry.get("examples") or {}
    if not isinstance(examples, dict):
        examples = {}
    return StructureHintRecord(
        structure_type=structure,
        subtype=normalize_subtype(subtype, structure),
        difficulty=normalize_difficulty(entry.get("difficulty")),
        explanation=str(entry.get("explanation") or ""),
        title=str(entry["title"]) if entry.get("title") else None,
        examples={str(k).lower(): str(v) for k, v in examples.items()},
        source="yaml",
    )
