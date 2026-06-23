"""Ensure bootstrap admin user with ADMIN + TEACHER + STUDENT roles."""

from __future__ import annotations

import os

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

from shared.enums import UserType
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.user import User
from infrastructure.external.security.password_hasher import PasswordHasherService
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository

SUPER_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@test.com").strip()
SUPER_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "").strip()
SUPER_NAME = os.getenv("SEED_ADMIN_NAME", "Admin").strip() or "Admin"
REQUIRED_ROLES = (UserType.ADMIN, UserType.TEACHER, UserType.STUDENT)


def ensure_super_user() -> None:
    if not SUPER_EMAIL:
        raise ValueError("SEED_ADMIN_EMAIL is required")
    if len(SUPER_PASSWORD) < 12:
        raise ValueError(
            "SEED_ADMIN_PASSWORD must be at least 12 characters. "
            "Set SEED_ADMIN_PASSWORD in backend/deploy/.env.dev (or .env.prod) before running seed."
        )

    load_models()
    configure_mappers()

    session = SessionLocal()
    try:
        roles_repo = SqlAlchemyUserRoleRepository(session)
        user = session.execute(select(User).where(User.email == SUPER_EMAIL)).scalar_one_or_none()

        hasher = PasswordHasherService()
        if user is None:
            user = User(
                name=SUPER_NAME,
                email=SUPER_EMAIL,
                password=hasher.hash(SUPER_PASSWORD),
                role=UserType.ADMIN.value,
            )
            session.add(user)
            session.flush()
            print(f"Created user {SUPER_EMAIL} (id={user.id})")
        else:
            user.password = hasher.hash(SUPER_PASSWORD)
            print(f"Updated password for {SUPER_EMAIL} (id={user.id})")

        for role in REQUIRED_ROLES:
            roles_repo.assign_role(user.id, role)

        session.commit()

        assigned = sorted(r.value for r in roles_repo.get_roles_for_user(user.id))
        print(f"{SUPER_EMAIL} roles: {', '.join(assigned)}")
    finally:
        session.close()


if __name__ == "__main__":
    ensure_super_user()
