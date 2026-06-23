"""Support tickets — student/teacher feedback and platform issues."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base
from infrastructure.db.models.task.enum_types import str_enum_column
from shared.enums import SupportTicketCategory, SupportTicketStatus, SupportTicketTarget

if TYPE_CHECKING:
    from infrastructure.db.models.learning.submission import Submission
    from infrastructure.db.models.support.support_ticket_message import SupportTicketMessage
    from infrastructure.db.models.task.task import Task
    from infrastructure.db.models.user.user import User


class SupportTicket(Base):
    __tablename__ = "support_ticket"

    author_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[SupportTicketCategory] = mapped_column(
        str_enum_column(SupportTicketCategory, name="support_ticket_category_enum"),
        nullable=False,
        index=True,
    )
    subject: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    status: Mapped[SupportTicketStatus] = mapped_column(
        str_enum_column(SupportTicketStatus, name="support_ticket_status_enum"),
        nullable=False,
        default=SupportTicketStatus.OPEN,
        server_default=SupportTicketStatus.OPEN.value,
        index=True,
    )
    target: Mapped[SupportTicketTarget] = mapped_column(
        str_enum_column(SupportTicketTarget, name="support_ticket_target_enum"),
        nullable=False,
        index=True,
    )
    assignee_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    task_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("task.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    submission_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    context_json: Mapped[dict[str, Any] | None] = mapped_column(sa.JSON(), nullable=True)
    escalated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    escalated_by_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
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
    resolved_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )

    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
    assignee: Mapped["User | None"] = relationship("User", foreign_keys=[assignee_id])
    task: Mapped["Task | None"] = relationship("Task")
    submission: Mapped["Submission | None"] = relationship("Submission")
    messages: Mapped[list["SupportTicketMessage"]] = relationship(
        "SupportTicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="SupportTicketMessage.created_at",
    )
