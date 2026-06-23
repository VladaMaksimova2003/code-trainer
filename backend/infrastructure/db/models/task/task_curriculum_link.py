"""ORM: task ↔ curriculum v2 metadata."""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class TaskCurriculumLinkModel(Base):
    __tablename__ = "task_curriculum_link"
    __table_args__ = (
        sa.UniqueConstraint(
            "task_id",
            "exercise_pattern_id",
            name="uq_task_curriculum_link_task_pattern",
        ),
        sa.Index(
            "uq_task_curriculum_link_primary",
            "task_id",
            unique=True,
            postgresql_where=sa.text("is_primary = true"),
            sqlite_where=sa.text("is_primary = 1"),
        ),
    )

    task_id: Mapped[int] = mapped_column(
        sa.ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    learning_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    technical_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    exercise_pattern_id: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    action: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default=sa.false(),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
