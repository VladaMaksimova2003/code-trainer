from typing import TYPE_CHECKING
from infrastructure.db.models.base import Base

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from infrastructure.db.models.learning.user_solution import UserSolution
    from infrastructure.db.models.task import Task
    from infrastructure.db.models.learning.group import Group
    from infrastructure.db.models.task.collection import Collection
    from infrastructure.db.models.user.teacher_profile import TeacherProfile
    from infrastructure.db.models.user.teacher_activity import TeacherActivity
    from infrastructure.db.models.user.user_preferences import UserPreferences
    from infrastructure.db.models.user.user_role import UserRole
    from infrastructure.db.models.user.teacher_role_request import TeacherRoleRequestModel


class User(Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    password: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    role: Mapped[str] = mapped_column(sa.String(64), default="student", nullable=False)
    is_blocked: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False, server_default="false"
    )
    is_deleted: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False, server_default="false"
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
    avatar_url: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    about: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    solutions: Mapped[list["UserSolution"]] = relationship("UserSolution", back_populates="student")
    created_tasks: Mapped[list["Task"]] = relationship("Task", back_populates="teacher")

    created_groups: Mapped[list["Group"]] = relationship("Group", back_populates="teacher")
    groups: Mapped[list["Group"]] = relationship(
        "Group", secondary="group_member_association", back_populates="students"
    )
    collections: Mapped[list["Collection"]] = relationship("Collection", back_populates="teacher")
    teacher_profile: Mapped["TeacherProfile | None"] = relationship(
        "TeacherProfile", back_populates="user", uselist=False
    )
    teacher_activities: Mapped[list["TeacherActivity"]] = relationship(
        "TeacherActivity", back_populates="teacher"
    )
    role_assignments: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    teacher_role_requests: Mapped[list["TeacherRoleRequestModel"]] = relationship(
        "TeacherRoleRequestModel",
        back_populates="user",
        foreign_keys="TeacherRoleRequestModel.user_id",
    )
    preferences: Mapped["UserPreferences | None"] = relationship(
        "UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
