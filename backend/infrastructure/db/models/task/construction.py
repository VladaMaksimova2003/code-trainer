from typing import TYPE_CHECKING
from infrastructure.db.models.base import Base

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from infrastructure.db.models.learning.user_solution import UserSolution
    from infrastructure.db.models.task import Task
    from infrastructure.db.models.learning.group import (
        Group,
        group_member_association_table,
    )
    from infrastructure.db.models.task.collection import Collection

task_construction_association_table = sa.Table(
    "task_construction_association",
    Base.metadata,
    sa.Column(
        "task_id",
        sa.Integer,
        sa.ForeignKey("task.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "construction_id",
        sa.Integer,
        sa.ForeignKey("constructions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Construction(Base):
    __tablename__ = "constructions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text)
    category_id: Mapped[int] = mapped_column(
        sa.ForeignKey("category_construction.id", ondelete="RESTRICT"), nullable=False
    )

    category: Mapped["CategoryConstruction"] = relationship(
        back_populates="constructions"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_construction_association_table,
        back_populates="constructions",
    )


class CategoryConstruction(Base):
    __tablename__ = "category_construction"

    name: Mapped[str] = mapped_column(sa.String(64), nullable=False)

    constructions: Mapped[list["Construction"]] = relationship(
        back_populates="category"
    )
