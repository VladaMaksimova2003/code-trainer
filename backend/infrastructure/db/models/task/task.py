from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.enums import Difficulty, TaskType, TaskVisibility
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.enum_types import str_enum_column

if TYPE_CHECKING:
    from infrastructure.db.models.user import User
    from infrastructure.db.models.learning.user_solution import UserSolution
    from infrastructure.db.models.task.collection import Collection
    from infrastructure.db.models.task.construction import Construction

class Task(Base):
    __tablename__ = "task"

    teacher_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"), nullable=True)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text)
    task_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    difficulty: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    version: Mapped[int] = mapped_column(sa.Integer, default=1, nullable=False)
    is_delete: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    workflow_status: Mapped[str] = mapped_column(
        sa.String(32),
        default="active",
        nullable=False,
        server_default="active",
    )
    visibility: Mapped[TaskVisibility] = mapped_column(
        str_enum_column(TaskVisibility, name="task_visibility_enum"),
        default=TaskVisibility.PUBLIC,
        nullable=False,
        server_default=TaskVisibility.PUBLIC.value,
    )
    test_cases: Mapped[dict | list] = mapped_column(
        sa.JSON(), default=list, nullable=False
    )
    code_examples: Mapped[dict] = mapped_column(sa.JSON(), default=dict, nullable=False)
    flow_spec: Mapped[dict] = mapped_column(sa.JSON(), default=dict, nullable=False)
    topic_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )

    teacher: Mapped["User"] = relationship("User", back_populates="created_tasks")
    solutions: Mapped[list["UserSolution"]] = relationship("UserSolution", back_populates="task")
    collections: Mapped[list["Collection"]] = relationship(
        "Collection",
        secondary="collection_task_association",
        back_populates="tasks",
    )
    constructions: Mapped[list["Construction"]] = relationship(
        "Construction",
        secondary="task_construction_association",
        back_populates="tasks",
    )

    translation_task: Mapped["TranslationTask"] = relationship(
        back_populates="task", uselist=False, lazy="select"
    )
    block_reorder_task: Mapped["BlockReorderTask"] = relationship(
        back_populates="task", uselist=False, lazy="select"
    )
    versions: Mapped[list["TaskVersion"]] = relationship(
        "TaskVersion",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskVersion.version_number.desc()",
    )


class TranslationTask(Base):
    __tablename__ = "translation_task"

    task_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("task.id", ondelete="CASCADE")
    )
    source_code: Mapped[str] = mapped_column(sa.Text, nullable=False)
    source_language: Mapped[str] = mapped_column(sa.String(32), nullable=False)

    task: Mapped["Task"] = relationship(back_populates="translation_task")


class BlockReorderTask(Base):
    __tablename__ = "block_reorder_task"

    task_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("task.id", ondelete="CASCADE")
    )
    original_code: Mapped[str] = mapped_column(sa.Text, nullable=False)
    template: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    blocks: Mapped[list] = mapped_column(sa.JSON, nullable=False)
    correct_order: Mapped[list] = mapped_column(sa.JSON, nullable=False)
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    language_variants: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    task: Mapped["Task"] = relationship(back_populates="block_reorder_task")
