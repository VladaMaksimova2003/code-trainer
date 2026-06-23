"""CRUD for structure_hints table."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.hints.structure_hint import StructureHintRecord
from infrastructure.db.models.hints.structure_hint import StructureHintModel


class StructureHintRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[StructureHintRecord]:
        rows = self._session.scalars(
            select(StructureHintModel).order_by(
                StructureHintModel.structure_type,
                StructureHintModel.subtype,
            )
        ).all()
        return [_to_record(row) for row in rows]

    def get_by_id(self, hint_id: int) -> StructureHintRecord | None:
        row = self._session.get(StructureHintModel, hint_id)
        return _to_record(row) if row else None

    def get_by_type_subtype(
        self,
        structure_type: str,
        subtype: str,
    ) -> StructureHintRecord | None:
        row = self._session.scalars(
            select(StructureHintModel).where(
                StructureHintModel.structure_type == structure_type,
                StructureHintModel.subtype == subtype,
            )
        ).first()
        return _to_record(row) if row else None

    def upsert(
        self,
        *,
        structure_type: str,
        subtype: str,
        difficulty: int,
        explanation: str,
        examples: dict[str, str],
        title: str | None = None,
    ) -> StructureHintRecord:
        row = self._session.scalars(
            select(StructureHintModel).where(
                StructureHintModel.structure_type == structure_type,
                StructureHintModel.subtype == subtype,
            )
        ).first()
        if row is None:
            row = StructureHintModel(
                structure_type=structure_type,
                subtype=subtype,
                difficulty=difficulty,
                explanation=explanation,
                examples_json=dict(examples),
                title=title,
            )
            self._session.add(row)
        else:
            row.difficulty = difficulty
            row.explanation = explanation
            row.examples_json = dict(examples)
            row.title = title
        self._session.flush()
        self._session.refresh(row)
        return _to_record(row)

    def delete_by_id(self, hint_id: int) -> bool:
        row = self._session.get(StructureHintModel, hint_id)
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True


def _to_record(row: StructureHintModel) -> StructureHintRecord:
    examples = row.examples_json if isinstance(row.examples_json, dict) else {}
    return StructureHintRecord(
        id=row.id,
        structure_type=row.structure_type,
        subtype=row.subtype,
        difficulty=row.difficulty,
        explanation=row.explanation,
        title=row.title,
        examples={str(k).lower(): str(v) for k, v in examples.items()},
        source="db",
    )
