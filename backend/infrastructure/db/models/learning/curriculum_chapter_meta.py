"""Teacher-authored curriculum chapter title and description."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.models.base import Base


class CurriculumChapterMeta(Base):
    __tablename__ = "curriculum_chapter_meta"
    __table_args__ = (
        sa.UniqueConstraint("language", "chapter_key", name="uq_curriculum_chapter_meta_lang_key"),
    )

    language: Mapped[str] = mapped_column(sa.String(32), nullable=False, default="", server_default="")
    chapter_key: Mapped[str] = mapped_column(sa.String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, default="", nullable=False, server_default="")
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False, server_default="0")
    is_custom: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False, server_default="false"
    )
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )
