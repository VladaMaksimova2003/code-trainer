from typing import TYPE_CHECKING
from datetime import date

from shared.enums import SolutionStatus
from infrastructure.db.models.base import Base

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from infrastructure.db.models.user import User
    from infrastructure.db.models.task import Task

class UserSolution(Base):
    __tablename__ = "user_solution"

    student_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[int] = mapped_column(sa.ForeignKey("task.id"))
    task_version: Mapped[int] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(sa.Text)
    language: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    status: Mapped[SolutionStatus] = mapped_column(
        sa.Enum(SolutionStatus, name="user_solution_status_enum", native_enum=False),
        default=SolutionStatus.NOT_STARTED,
    )
    completed_at: Mapped[date] = mapped_column(sa.Date)

    student: Mapped["User"] = relationship(back_populates="solutions")
    task: Mapped["Task"] = relationship(back_populates="solutions")
