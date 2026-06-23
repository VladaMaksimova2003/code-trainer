"""Persisted adaptive learning state per student."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class StudentLearningProfileModel(Base):
    __tablename__ = "student_learning_profile"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    structures_json: Mapped[dict] = mapped_column(sa.JSON, nullable=False, default=dict)
    weak_areas_json: Mapped[list] = mapped_column(sa.JSON, nullable=False, default=list)
    failure_counts_json: Mapped[dict] = mapped_column(sa.JSON, nullable=False, default=dict)
    learning_level: Mapped[str] = mapped_column(
        sa.String(32), nullable=False, default="beginner", server_default="beginner"
    )
    consecutive_passes: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
