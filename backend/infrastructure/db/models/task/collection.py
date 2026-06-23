from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.enums import AssignmentSetVisibility
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.enum_types import str_enum_column

if TYPE_CHECKING:
    from infrastructure.db.models.user import User
    from infrastructure.db.models.task import Task
    from infrastructure.db.models.learning.group import Group


collection_task_association_table = sa.Table(
    "collection_task_association",
    Base.metadata,
    sa.Column(
        "collection_id",
        sa.Integer,
        sa.ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "task_id",
        sa.Integer,
        sa.ForeignKey("task.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    sa.Column("topic", sa.String(128), nullable=True),
)


class Collection(Base):
    """Assignment set (teacher-curated group of tasks). Table name kept for compatibility."""

    __tablename__ = "collections"

    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, default="", nullable=False, server_default="")
    teacher_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    visibility: Mapped[AssignmentSetVisibility] = mapped_column(
        str_enum_column(AssignmentSetVisibility, name="collection_visibility_enum"),
        default=AssignmentSetVisibility.PRIVATE,
        nullable=False,
        server_default=AssignmentSetVisibility.PRIVATE.value,
    )
    group_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("group.id", ondelete="SET NULL"), nullable=True
    )
    deadline_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    is_archived: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False, server_default="false"
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    teacher: Mapped["User"] = relationship("User", back_populates="collections")
    group = relationship("Group", back_populates="assignment_sets")
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=collection_task_association_table,
        back_populates="collections",
    )
