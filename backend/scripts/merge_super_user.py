"""Merge legacy dev accounts into a single super-user (admin@test.com)."""

from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.orm import configure_mappers

from shared.enums import UserType
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task import Task
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.learning.group import Group, group_member_association_table
from infrastructure.db.models.learning.invitation_code import InvitationCodeModel
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.learning.user_solution import UserSolution
from infrastructure.db.models.learning.student_learning_profile import StudentLearningProfileModel
from infrastructure.db.models.user import User
from infrastructure.db.models.user.auth_session import AuthSession
from infrastructure.db.models.user.teacher_activity import TeacherActivity
from infrastructure.db.models.user.teacher_profile import TeacherProfile
from infrastructure.db.models.user.teacher_role_request import TeacherRoleRequestModel
from infrastructure.db.models.user.user_preferences import UserPreferences
from infrastructure.db.models.user.user_role import UserRole
from infrastructure.external.security.password_hasher import PasswordHasherService

TARGET_EMAIL = "admin@test.com"
SOURCE_EMAILS = (
    "maximov4.vladyslava@yandex.ru",
    "vladamaximova2003@gmail.com",
)
SUPER_ROLES = (UserType.ADMIN, UserType.TEACHER, UserType.STUDENT)


def _ensure_super_user(session) -> User:
    user = session.execute(select(User).where(User.email == TARGET_EMAIL)).scalar_one_or_none()
    hasher = PasswordHasherService()

    if user is None:
        user = User(
            name="Admin",
            email=TARGET_EMAIL,
            password=hasher.hash("admin123"),
            role=UserType.ADMIN.value,
        )
        session.add(user)
        session.flush()
    else:
        user.role = UserType.ADMIN.value

    for role in SUPER_ROLES:
        exists = session.execute(
            select(UserRole).where(UserRole.user_id == user.id, UserRole.role == role.value)
        ).scalar_one_or_none()
        if exists is None:
            session.add(UserRole(user_id=user.id, role=role.value))

    session.flush()
    return user


def _merge_one_to_one(session, model, field_name: str, source_id: int, target_id: int) -> None:
    """Move or drop source row when target may already have the same 1:1 record."""
    column = getattr(model, field_name)
    source_pk = session.execute(select(model.id).where(column == source_id)).scalar_one_or_none()
    if source_pk is None:
        return

    target_pk = session.execute(select(model.id).where(column == target_id)).scalar_one_or_none()
    if target_pk is not None:
        session.execute(delete(model).where(column == source_id))
    else:
        session.execute(update(model).where(column == source_id).values({field_name: target_id}))
    session.flush()


def _reassign_one_to_one(session, model, field_name: str, source_id: int, target_id: int) -> None:
    _merge_one_to_one(session, model, field_name, source_id, target_id)


def _merge_group_memberships(session, source_id: int, target_id: int) -> None:
    source_rows = session.execute(
        select(group_member_association_table).where(
            group_member_association_table.c.student_id == source_id
        )
    ).all()

    target_group_ids = set(
        session.execute(
            select(group_member_association_table.c.group_id).where(
                group_member_association_table.c.student_id == target_id
            )
        ).scalars()
    )

    for row in source_rows:
        group_id = row.group_id
        if group_id in target_group_ids:
            session.execute(
                delete(group_member_association_table).where(
                    group_member_association_table.c.group_id == group_id,
                    group_member_association_table.c.student_id == source_id,
                )
            )
            continue
        session.execute(
            update(group_member_association_table)
            .where(
                group_member_association_table.c.group_id == group_id,
                group_member_association_table.c.student_id == source_id,
            )
            .values(student_id=target_id)
        )
        target_group_ids.add(group_id)


def _merge_user_roles(session, source_id: int, target_id: int) -> None:
    source_roles = session.execute(
        select(UserRole.role).where(UserRole.user_id == source_id)
    ).scalars()
    target_roles = set(
        session.execute(select(UserRole.role).where(UserRole.user_id == target_id)).scalars()
    )
    for role in source_roles:
        if role not in target_roles:
            session.add(UserRole(user_id=target_id, role=role))
    session.execute(delete(UserRole).where(UserRole.user_id == source_id))


def _merge_user_data(session, target_id: int, source_id: int) -> None:
    if source_id == target_id:
        return

    _reassign_one_to_one(session, TeacherProfile, "user_id", source_id, target_id)
    _reassign_one_to_one(session, StudentLearningProfileModel, "user_id", source_id, target_id)
    _reassign_one_to_one(session, UserPreferences, "user_id", source_id, target_id)

    session.execute(update(Task).where(Task.teacher_id == source_id).values(teacher_id=target_id))
    session.execute(
        update(Collection).where(Collection.teacher_id == source_id).values(teacher_id=target_id)
    )
    session.execute(update(Group).where(Group.teacher_id == source_id).values(teacher_id=target_id))
    session.execute(
        update(InvitationCodeModel)
        .where(InvitationCodeModel.teacher_id == source_id)
        .values(teacher_id=target_id)
    )
    session.execute(
        update(TeacherActivity)
        .where(TeacherActivity.teacher_id == source_id)
        .values(teacher_id=target_id)
    )
    session.execute(
        update(UserSolution).where(UserSolution.student_id == source_id).values(student_id=target_id)
    )
    session.execute(
        update(Submission).where(Submission.user_id == source_id).values(user_id=target_id)
    )
    session.execute(
        update(TeacherRoleRequestModel)
        .where(TeacherRoleRequestModel.user_id == source_id)
        .values(user_id=target_id)
    )
    session.execute(
        update(TeacherRoleRequestModel)
        .where(TeacherRoleRequestModel.reviewed_by_id == source_id)
        .values(reviewed_by_id=target_id)
    )

    _merge_group_memberships(session, source_id, target_id)
    _merge_user_roles(session, source_id, target_id)

    session.execute(delete(AuthSession).where(AuthSession.user_id == source_id))
    session.execute(delete(User).where(User.id == source_id))


def merge_super_user() -> None:
    load_models()
    configure_mappers()

    session = SessionLocal()
    try:
        with session.begin():
            target = _ensure_super_user(session)
            print(f"Target super-user: {target.email} (id={target.id})")

            for email in SOURCE_EMAILS:
                source = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
                if source is None:
                    print(f"Skip missing source account: {email}")
                    continue
                print(f"Merging {email} (id={source.id}) -> {TARGET_EMAIL}")
                _merge_user_data(session, target.id, source.id)

        print("Merge complete.")
    finally:
        session.close()


if __name__ == "__main__":
    merge_super_user()
