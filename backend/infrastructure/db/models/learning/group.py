from typing import TYPE_CHECKING
from infrastructure.db.models.base import Base

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from infrastructure.db.models.user import User


group_member_association_table = sa.Table(
    "group_member_association",
    Base.metadata,
    sa.Column(
        "group_id",
        sa.Integer,
        sa.ForeignKey("group.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "student_id",
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Group(Base):
    __tablename__ = "group"

    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    teacher: Mapped["User"] = relationship("User", back_populates="created_groups")
    students: Mapped[list["User"]] = relationship(
        "User", secondary=group_member_association_table, back_populates="groups"
    )
    assignment_sets = relationship("Collection", back_populates="group")
    invitation_codes = relationship(
        "InvitationCodeModel",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
