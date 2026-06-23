from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from infrastructure.db.models.user import User


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    preferred_languages: Mapped[list[str]] = mapped_column(
        sa.JSON(), nullable=False, default=list, server_default="[]"
    )
    preferred_difficulty: Mapped[str] = mapped_column(
        sa.String(32), nullable=False, default="beginner", server_default="beginner"
    )
    preferred_topics: Mapped[list[str]] = mapped_column(
        sa.JSON(), nullable=False, default=list, server_default="[]"
    )
    study_place: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    study_group: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)

    user: Mapped["User"] = relationship(back_populates="preferences")
