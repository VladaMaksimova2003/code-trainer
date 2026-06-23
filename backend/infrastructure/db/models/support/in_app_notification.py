"""In-app notifications (no email/push in MVP)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base
from infrastructure.db.models.task.enum_types import str_enum_column
from shared.enums import NotificationKind

if TYPE_CHECKING:
    from infrastructure.db.models.support.support_ticket import SupportTicket
    from infrastructure.db.models.user.user import User


class InAppNotification(Base):
    __tablename__ = "in_app_notification"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticket_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("support_ticket.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    task_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    submission_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("submission.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    kind: Mapped[NotificationKind] = mapped_column(
        str_enum_column(NotificationKind, name="notification_kind_enum"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    body: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    is_read: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    user: Mapped["User"] = relationship("User")
    ticket: Mapped["SupportTicket | None"] = relationship("SupportTicket")
