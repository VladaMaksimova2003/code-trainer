"""Persisted structure hints (admin-editable; core grading does not use this table)."""
from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class StructureHintModel(Base):
    __tablename__ = "structure_hints"
    __table_args__ = (
        sa.UniqueConstraint("structure_type", "subtype", name="uq_structure_hints_type_subtype"),
    )

    structure_type: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    subtype: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    difficulty: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    title: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    explanation: Mapped[str] = mapped_column(sa.Text, nullable=False, default="")
    examples_json: Mapped[dict] = mapped_column(sa.JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )
