"""Assign orphan tasks (teacher_id IS NULL) to the seed admin for manual editing."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select, update

from infrastructure.db.models.task import Task
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.user import User
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import DEFAULT_SEED_TEACHER_EMAIL


def assign_tasks_to_teacher(teacher_email: str = DEFAULT_SEED_TEACHER_EMAIL) -> int:
    """Assign all tasks with NULL teacher_id to the given user. Returns rows updated."""
    load_models()
    session = SessionLocal()
    try:
        teacher = session.execute(
            select(User).where(User.email == teacher_email.strip())
        ).scalar_one_or_none()
        if teacher is None:
            raise RuntimeError(
                f"User not found: {teacher_email}. Run scripts/ensure_super_user.py first."
            )

        result = session.execute(
            update(Task)
            .where(Task.teacher_id.is_(None))
            .values(teacher_id=teacher.id)
        )
        session.commit()
        return int(result.rowcount or 0)
    finally:
        session.close()


if __name__ == "__main__":
    count = assign_tasks_to_teacher()
    print(f"Assigned {count} tasks to {DEFAULT_SEED_TEACHER_EMAIL}")
