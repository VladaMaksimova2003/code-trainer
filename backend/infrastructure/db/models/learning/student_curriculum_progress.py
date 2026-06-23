"""ORM: per-user progress on curriculum-linked tasks."""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class StudentCurriculumProgressModel(Base):
    __tablename__ = "student_curriculum_progress"
    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "task_id",
            "language",
            name="uq_student_curriculum_progress_user_task_lang",
        ),
        sa.Index("ix_student_curriculum_progress_user_lc", "user_id", "language", "learning_concept_id"),
    )

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[int] = mapped_column(
        sa.ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False,
    )
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    learning_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    technical_concept_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    action: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    exercise_pattern_id: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    attempts_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    passed_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0, server_default="0")
    last_status: Mapped[str | None] = mapped_column(sa.String(16), nullable=True)
    last_submission_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="SET NULL"),
        nullable=True,
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    first_passed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
