"""Update teacher-defined order of curriculum chapters (collections)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from application.curriculum.display.chapter_task_display_order import set_collection_chapter_order


def update_collection_chapter_order(
    db: Session,
    *,
    teacher_id: int,
    chapter_keys: list[str],
) -> list[str]:
    return set_collection_chapter_order(
        db,
        teacher_id=teacher_id,
        ordered_chapter_keys=chapter_keys,
    )
