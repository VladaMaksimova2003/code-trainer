from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from application.hints.structure_hint_service import StructureHintService
from infrastructure.db.session import get_db
from infrastructure.repositories.hints.structure_hint_repository import (
    StructureHintRepository,
)


def get_structure_hint_service(
    db: Session = Depends(get_db),
) -> StructureHintService:
    return StructureHintService(StructureHintRepository(db))
