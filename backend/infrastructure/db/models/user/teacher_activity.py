from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from infrastructure.db.models.user import User


class TeacherActivity(Base):
    """Teacher actions for activity feed / heatmap (create/edit tasks)."""

    __tablename__ = "teacher_activity"

    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    action_type: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
    )

    teacher: Mapped["User"] = relationship(back_populates="teacher_activities")
