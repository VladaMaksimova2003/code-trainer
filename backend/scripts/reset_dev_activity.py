import argparse

from sqlalchemy import delete, or_, select

from shared.enums import UserType
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.learning.group import Group, group_member_association_table
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.learning.submission import (
    Submission,
    SubmissionLintError,
    SubmissionPatternError,
    SubmissionTestResult,
)
from infrastructure.db.models.task import Task
from infrastructure.db.models.user import User
from infrastructure.db.models.learning.user_solution import UserSolution
from infrastructure.db.models.user.auth_session import AuthSession
from infrastructure.external.security.password_hasher import PasswordHasherService


def ensure_default_admin(
    session,
    email: str = "admin@test.com",
    password: str = "admin123",
    name: str = "Admin",
) -> bool:
    existing_admin = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing_admin is not None:
        return False

    hasher = PasswordHasherService()
    admin = User(
        name=name,
        email=email,
        password=hasher.hash(password),
        role=UserType.ADMIN.value,
    )
    session.add(admin)
    return True


def _confirm(force: bool) -> bool:
    print("WARNING: DEVELOPMENT-ONLY SCRIPT")
    print("This will delete user activity/progress data.")
    print("Educational content (tasks/collections/constructions) will be preserved.")
    if force:
        return True

    typed = input("Type 'RESET DEV DATA' to continue: ").strip()
    return typed == "RESET DEV DATA"


def reset_dev_activity(with_admin: bool, admin_email: str, admin_password: str) -> None:
    load_models()

    session = SessionLocal()
    summary: dict[str, int] = {}
    try:
        with session.begin():
            protected_user_ids = set(
                uid
                for uid in session.execute(
                    select(Task.teacher_id).where(Task.teacher_id.is_not(None))
                ).scalars()
                if uid is not None
            )
            protected_user_ids.update(
                uid
                for uid in session.execute(
                    select(Collection.teacher_id).where(Collection.teacher_id.is_not(None))
                ).scalars()
                if uid is not None
            )
            protected_user_ids.update(
                uid
                for uid in session.execute(
                    select(Group.teacher_id).where(Group.teacher_id.is_not(None))
                ).scalars()
                if uid is not None
            )

            all_user_ids = set(session.execute(select(User.id)).scalars().all())
            deletable_user_ids = sorted(all_user_ids - protected_user_ids)

            summary["submission_lint_error"] = (
                session.execute(delete(SubmissionLintError)).rowcount or 0
            )
            summary["submission_pattern_error"] = (
                session.execute(delete(SubmissionPatternError)).rowcount or 0
            )
            summary["submission_test_result"] = (
                session.execute(delete(SubmissionTestResult)).rowcount or 0
            )
            summary["submission"] = session.execute(delete(Submission)).rowcount or 0

            if deletable_user_ids:
                summary["auth_session"] = (
                    session.execute(
                        delete(AuthSession).where(AuthSession.user_id.in_(deletable_user_ids))
                    ).rowcount
                    or 0
                )
                summary["user_solution"] = (
                    session.execute(
                        delete(UserSolution).where(UserSolution.student_id.in_(deletable_user_ids))
                    ).rowcount
                    or 0
                )
                summary["group_member_association"] = (
                    session.execute(
                        delete(group_member_association_table).where(
                            or_(
                                group_member_association_table.c.student_id.in_(
                                    deletable_user_ids
                                ),
                                group_member_association_table.c.group_id.in_(
                                    select(Group.id).where(
                                        Group.teacher_id.in_(deletable_user_ids)
                                    )
                                ),
                            )
                        )
                    ).rowcount
                    or 0
                )
                summary["group"] = (
                    session.execute(
                        delete(Group).where(Group.teacher_id.in_(deletable_user_ids))
                    ).rowcount
                    or 0
                )
                summary["user"] = (
                    session.execute(delete(User).where(User.id.in_(deletable_user_ids))).rowcount
                    or 0
                )
            else:
                summary["auth_session"] = 0
                summary["user_solution"] = 0
                summary["group_member_association"] = 0
                summary["group"] = 0
                summary["user"] = 0

            admin_created = False
            if with_admin:
                admin_created = ensure_default_admin(
                    session,
                    email=admin_email,
                    password=admin_password,
                )

        print("Cleanup complete.")
        print("Cleaned data:")
        for table_name, count in summary.items():
            print(f"- {table_name}: {count}")

        print("Preserved data:")
        print("- task")
        print("- collections")
        print("- constructions")
        print("- task relation tables and static metadata")

        if with_admin:
            if admin_created:
                print(f"Default admin created: {admin_email}")
            else:
                print(f"Default admin already exists: {admin_email}")
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Development-only cleanup for user activity data."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation prompt.",
    )
    parser.add_argument(
        "--with-admin",
        action="store_true",
        help="Ensure default admin exists after cleanup.",
    )
    parser.add_argument(
        "--admin-email",
        default="admin@test.com",
        help="Default admin email to seed when --with-admin is used.",
    )
    parser.add_argument(
        "--admin-password",
        default="admin123",
        help="Default admin password to seed when --with-admin is used.",
    )
    args = parser.parse_args()

    if not _confirm(force=args.yes):
        print("Cancelled.")
        return

    reset_dev_activity(
        with_admin=args.with_admin,
        admin_email=args.admin_email,
        admin_password=args.admin_password,
    )


if __name__ == "__main__":
    main()
