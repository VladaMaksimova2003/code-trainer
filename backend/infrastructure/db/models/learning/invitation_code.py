"""Invitation codes for students to join teacher groups."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base


class InvitationCodeModel(Base):
    __tablename__ = "invitation_code"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True, nullable=False, index=True)
    group_id: Mapped[int] = mapped_column(
        sa.ForeignKey("group.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    max_uses: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    use_count: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False, server_default="0")
    expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, nullable=False, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    group = relationship("Group", back_populates="invitation_codes")
