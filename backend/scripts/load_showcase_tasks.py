#!/usr/bin/env python3
"""
Load demo assignments for преподавательское демо (author: Admin / admin@test.com).

Run after ensure_super_user:
  poetry run python scripts/load_showcase_tasks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from application.tasks.services.assignment_creation_service import (
    create_build_from_blocks_handler,
    create_flowchart_handler,
    create_translation_handler,
)
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.user import User
from shared.enums import AssignmentType
from showcase_task_data import FLOW_SPEC, showcase_tasks

ADMIN_EMAIL = "admin@test.com"


def load_showcase_tasks(*, replace_existing: bool = True) -> int:
    """Create showcase tasks owned by admin@test.com. Returns count created."""
    from infrastructure.db.models.task.registry import load_models
    from sqlalchemy.orm import configure_mappers

    load_models()
    configure_mappers()

    session = SessionLocal()
    created = 0
    try:
        admin = session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        ).scalar_one_or_none()
        if admin is None:
            raise RuntimeError(
                f"{ADMIN_EMAIL} not found — run ensure_super_user first"
            )

        if replace_existing:
            _clear_teacher_tasks(session, admin.id)

        for item in showcase_tasks():
            assignment_type = item["assignment_type"]
            common = {
                "title": item["title"],
                "description": item["description"],
                "difficulty": item["difficulty"],
                "teacher_id": admin.id,
                "test_cases": item.get("test_cases"),
                "patterns": item.get("patterns"),
            }

            if assignment_type == AssignmentType.TASK_BUILD_FROM_BLOCKS.value:
                create_build_from_blocks_handler(
                    session,
                    assignment_type=assignment_type,
                    language=item["language"],
                    original_code=item["original_code"],
                    template=item.get("template"),
                    blocks=item.get("blocks"),
                    correct_order=item.get("correct_order"),
                    **common,
                )
            elif assignment_type in (
                AssignmentType.TASK_TRANSLATE_SNIPPET.value,
                AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            ):
                create_translation_handler(
                    session,
                    assignment_type=assignment_type,
                    source_language=item["language"],
                    source_code=item["source_code"],
                    **common,
                )
            elif assignment_type == AssignmentType.TASK_FLOWCHART_TO_CODE.value:
                create_flowchart_handler(
                    session,
                    assignment_type=assignment_type,
                    language=item["language"],
                    diagram=item["diagram"],
                    flow_spec=FLOW_SPEC,
                    reference_code=item.get("reference_code", ""),
                    expose_reference_code=bool(item.get("expose_reference_code")),
                    **common,
                )
            else:
                raise ValueError(f"Unsupported assignment type: {assignment_type}")

            created += 1
            print(f"  + [{created:02d}] {item['title']}")

        print(f"Loaded {created} showcase tasks for {ADMIN_EMAIL} (id={admin.id}).")
        return created
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _clear_teacher_tasks(session, teacher_id: int) -> None:
    """Remove all tasks (and dependent rows) before re-seeding showcase data."""
    from sqlalchemy import text

    session.execute(
        text(
            """
            DELETE FROM collection_task_association
            WHERE task_id IN (SELECT id FROM task)
            """
        )
    )
    session.execute(text("DELETE FROM task_construction_association"))
    session.execute(text("DELETE FROM task_version"))
    session.execute(text("DELETE FROM block_reorder_task"))
    session.execute(text("DELETE FROM translation_task"))
    session.execute(text("DELETE FROM task"))
    session.commit()
    print("Cleared existing tasks.")


if __name__ == "__main__":
    load_showcase_tasks()
