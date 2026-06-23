"""Resolve seed task author — all curriculum tasks owned by admin for manual editing."""

from __future__ import annotations

import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models.user import User
from shared.super_user import SUPER_USER_EMAIL

DEFAULT_SEED_TEACHER_EMAIL = os.getenv("SEED_ADMIN_EMAIL", SUPER_USER_EMAIL).strip()


def resolve_seed_teacher_id(session: Session, email: str | None = None) -> int:
    """Return user id for seeded tasks. Defaults to admin@test.com (SEED_ADMIN_EMAIL)."""
    effective = (email or DEFAULT_SEED_TEACHER_EMAIL).strip()
    if not effective:
        raise RuntimeError("Seed teacher email is empty (set SEED_ADMIN_EMAIL)")
    user = session.execute(select(User).where(User.email == effective)).scalar_one_or_none()
    if user is None:
        raise RuntimeError(
            f"Seed teacher not found: {effective}. "
            "Run scripts/ensure_super_user.py first."
        )
    return int(user.id)
