"""Historical snapshots of task (assignment) versions for admin control."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base


class TaskVersion(Base):
    __tablename__ = "task_version"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    task_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    snapshot: Mapped[dict] = mapped_column(sa.JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False, server_default="false"
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    task = relationship("Task", back_populates="versions")

