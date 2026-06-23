from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from infrastructure.db.models.user import User


class TeacherProfile(Base):
    """Extended profile for LMS-style teacher dashboards."""

    __tablename__ = "teacher_profile"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    full_name: Mapped[str] = mapped_column(
        sa.String(256), nullable=False, server_default="", default=""
    )
    bio: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    languages: Mapped[list[str]] = mapped_column(
        sa.JSON(), nullable=False, default=list,
    )
    specialization: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    is_public: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=True, server_default="true"
    )

    user: Mapped["User"] = relationship(back_populates="teacher_profile")
