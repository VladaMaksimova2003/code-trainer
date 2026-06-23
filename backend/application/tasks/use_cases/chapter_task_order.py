"""Update teacher-defined order of tasks within a curriculum chapter."""

from __future__ import annotations

from sqlalchemy.orm import Session

from application.curriculum.display.chapter_task_display_order import set_chapter_task_order


def update_chapter_task_order(
    db: Session,
    *,
    teacher_id: int,
    chapter_key: str,
    task_ids: list[int],
) -> list[int]:
    return set_chapter_task_order(
        db,
        teacher_id=teacher_id,
        chapter_key=chapter_key,
        ordered_task_ids=task_ids,
    )
