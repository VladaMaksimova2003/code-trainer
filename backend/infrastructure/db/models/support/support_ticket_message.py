"""Messages in a support ticket thread."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base
from infrastructure.db.models.task.enum_types import str_enum_column
from shared.enums import SupportTicketMessageType

if TYPE_CHECKING:
    from infrastructure.db.models.support.support_ticket import SupportTicket
    from infrastructure.db.models.user.user import User


class SupportTicketMessage(Base):
    __tablename__ = "support_ticket_message"

    ticket_id: Mapped[int] = mapped_column(
        sa.ForeignKey("support_ticket.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    body: Mapped[str] = mapped_column(sa.Text, nullable=False)
    message_type: Mapped[SupportTicketMessageType] = mapped_column(
        str_enum_column(SupportTicketMessageType, name="support_ticket_message_type_enum"),
        nullable=False,
        default=SupportTicketMessageType.USER,
        server_default=SupportTicketMessageType.USER.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="messages")
    author: Mapped["User | None"] = relationship("User")
