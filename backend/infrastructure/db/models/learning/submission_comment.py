"""Teacher feedback comments on student submissions."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from infrastructure.db.models.learning.submission import Submission
    from infrastructure.db.models.user.user import User


class SubmissionComment(Base):
    __tablename__ = "submission_comment"

    submission_id: Mapped[int] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    body: Mapped[str] = mapped_column(sa.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    submission: Mapped["Submission"] = relationship(
        "Submission",
        back_populates="teacher_comments",
    )
    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id])
