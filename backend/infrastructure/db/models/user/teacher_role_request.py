import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.base import Base


class TeacherRoleRequestModel(Base):
    __tablename__ = "teacher_role_request"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
    reviewed_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    reviewed_by_id: Mapped[int | None] = mapped_column(
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="teacher_role_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by_id])
