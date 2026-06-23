"""Teacher courses stored as JSON meta (no extra DB tables)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from application.curriculum.chapters.curriculum_chapter_meta_service import (
    PLATFORM_COURSE_DEFAULT_DESCRIPTION,
    PLATFORM_COURSE_DEFAULT_TITLE,
    _GLOBAL_LANGUAGE,
    resolve_platform_course_display,
    upsert_chapter,
)
from infrastructure.db.models.task.collection import Collection
from infrastructure.repositories.tasks.task_catalog import SqlAlchemyCatalogTaskRelationRepository
from shared.exceptions import AccessDeniedToContentError, CatalogNotFoundError

TEACHER_COURSES_META_KEY = "__teacher_courses__"


def _teacher_courses_meta_key(teacher_id: int) -> str:
    return f"{TEACHER_COURSES_META_KEY}{teacher_id}__"


def _catalog_courses_meta_key(catalog_id: int) -> str:
    return f"__catalog_courses_{catalog_id}__"


def _meta_row(session: Session, *, teacher_id: int, chapter_key: str):
    from sqlalchemy import select

    from infrastructure.db.models.learning.curriculum_chapter_meta import CurriculumChapterMeta

    return session.execute(
        select(CurriculumChapterMeta).where(
            CurriculumChapterMeta.language == _GLOBAL_LANGUAGE,
            CurriculumChapterMeta.chapter_key == chapter_key,
            CurriculumChapterMeta.teacher_id == teacher_id,
        )
    ).scalar_one_or_none()


def _load_courses_raw(session: Session, *, teacher_id: int) -> list[dict[str, Any]]:
    row = _meta_row(session, teacher_id=teacher_id, chapter_key=_teacher_courses_meta_key(teacher_id))
    if row is None or not str(row.description or "").strip():
        return []
    try:
        data = json.loads(str(row.description))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _save_courses_raw(session: Session, *, teacher_id: int, courses: list[dict[str, Any]]) -> None:
    upsert_chapter(
        session,
        teacher_id=teacher_id,
        language=_GLOBAL_LANGUAGE,
        chapter_key=_teacher_courses_meta_key(teacher_id),
        title="Teacher courses",
        description=json.dumps(courses, ensure_ascii=False),
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _curriculum_task_ids(session: Session, *, teacher_id: int) -> list[int]:
    """Tasks linked to the platform curriculum (128 slots), excluding orphan duplicates."""
    from sqlalchemy import select

    from infrastructure.db.models.task.task import Task as TaskModel
    from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel

    rows = session.execute(
        select(TaskCurriculumLinkModel.task_id)
        .join(TaskModel, TaskModel.id == TaskCurriculumLinkModel.task_id)
        .where(
            TaskModel.teacher_id == teacher_id,
            TaskModel.is_delete.is_(False),
        )
        .distinct()
    ).scalars().all()
    return [int(task_id) for task_id in rows]


def _task_count(session: Session, *, teacher_id: int, course: dict[str, Any]) -> int:
    if course.get("is_default"):
        return len(_curriculum_task_ids(session, teacher_id=teacher_id))
    return 0


def _course_to_dict(session: Session, *, teacher_id: int, course: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": int(course["id"]),
        "title": str(course.get("title") or ""),
        "description": str(course.get("description") or ""),
        "is_default": bool(course.get("is_default")),
        "task_count": _task_count(session, teacher_id=teacher_id, course=course),
        "created_at": course.get("created_at") or _now_iso(),
        "updated_at": course.get("updated_at"),
    }


def ensure_default_course(session: Session, *, teacher_id: int) -> list[dict[str, Any]]:
    courses = _load_courses_raw(session, teacher_id=teacher_id)
    if any(bool(item.get("is_default")) for item in courses):
        title, description = resolve_platform_course_display(session)
        for item in courses:
            if item.get("is_default"):
                item["title"] = title or item.get("title") or PLATFORM_COURSE_DEFAULT_TITLE
                item["description"] = description or item.get("description") or PLATFORM_COURSE_DEFAULT_DESCRIPTION
        _save_courses_raw(session, teacher_id=teacher_id, courses=courses)
        return courses

    title, description = resolve_platform_course_display(session)
    courses.insert(
        0,
        {
            "id": 1,
            "title": title or PLATFORM_COURSE_DEFAULT_TITLE,
            "description": description or PLATFORM_COURSE_DEFAULT_DESCRIPTION,
            "is_default": True,
            "created_at": _now_iso(),
            "updated_at": None,
        },
    )
    _save_courses_raw(session, teacher_id=teacher_id, courses=courses)
    return courses


def list_teacher_courses(session: Session, *, teacher_id: int) -> list[dict[str, Any]]:
    courses = ensure_default_course(session, teacher_id=teacher_id)
    return [_course_to_dict(session, teacher_id=teacher_id, course=item) for item in courses]


def create_teacher_course(
    session: Session,
    *,
    teacher_id: int,
    title: str,
    description: str = "",
) -> dict[str, Any]:
    clean_title = str(title or "").strip()
    if not clean_title:
        raise ValueError("title is required")
    courses = ensure_default_course(session, teacher_id=teacher_id)
    next_id = max((int(item["id"]) for item in courses), default=0) + 1
    row = {
        "id": next_id,
        "title": clean_title,
        "description": str(description or "").strip(),
        "is_default": False,
        "created_at": _now_iso(),
        "updated_at": None,
    }
    courses.append(row)
    _save_courses_raw(session, teacher_id=teacher_id, courses=courses)
    return _course_to_dict(session, teacher_id=teacher_id, course=row)


def update_teacher_course(
    session: Session,
    *,
    teacher_id: int,
    course_id: int,
    title: str,
    description: str = "",
) -> dict[str, Any]:
    courses = ensure_default_course(session, teacher_id=teacher_id)
    target = next((item for item in courses if int(item["id"]) == int(course_id)), None)
    if target is None:
        raise AccessDeniedToContentError("Course not found")
    clean_title = str(title or "").strip()
    if not clean_title:
        raise ValueError("title is required")
    target["title"] = clean_title
    target["description"] = str(description or "").strip()
    target["updated_at"] = _now_iso()
    _save_courses_raw(session, teacher_id=teacher_id, courses=courses)

    if target.get("is_default"):
        from application.curriculum.chapters.curriculum_chapter_meta_service import upsert_platform_course_meta

        upsert_platform_course_meta(
            session,
            teacher_id=teacher_id,
            title=clean_title,
            description=str(description or "").strip(),
        )

    return _course_to_dict(session, teacher_id=teacher_id, course=target)


def _load_catalog_course_ids(session: Session, *, teacher_id: int, catalog_id: int) -> list[int]:
    row = _meta_row(session, teacher_id=teacher_id, chapter_key=_catalog_courses_meta_key(catalog_id))
    if row is None or not str(row.description or "").strip():
        return []
    try:
        data = json.loads(str(row.description))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [int(item) for item in data]


def _save_catalog_course_ids(
    session: Session,
    *,
    teacher_id: int,
    catalog_id: int,
    course_ids: list[int],
) -> None:
    upsert_chapter(
        session,
        teacher_id=teacher_id,
        language=_GLOBAL_LANGUAGE,
        chapter_key=_catalog_courses_meta_key(catalog_id),
        title=f"Catalog {catalog_id} courses",
        description=json.dumps(course_ids, ensure_ascii=False),
    )


def _task_ids_for_course(session: Session, *, teacher_id: int, course: dict[str, Any]) -> list[int]:
    if not course.get("is_default"):
        return []
    return _curriculum_task_ids(session, teacher_id=teacher_id)


def list_catalog_courses(session: Session, *, teacher_id: int, catalog_id: int) -> list[dict[str, Any]]:
    catalog = session.get(Collection, catalog_id)
    if catalog is None or catalog.teacher_id != teacher_id:
        raise CatalogNotFoundError(f"Catalog {catalog_id} not found")

    courses = ensure_default_course(session, teacher_id=teacher_id)
    by_id = {int(item["id"]): item for item in courses}
    return [
        _course_to_dict(session, teacher_id=teacher_id, course=by_id[course_id])
        for course_id in _load_catalog_course_ids(session, teacher_id=teacher_id, catalog_id=catalog_id)
        if course_id in by_id
    ]


def add_course_to_catalog(
    session: Session,
    *,
    teacher_id: int,
    catalog_id: int,
    course_id: int,
) -> None:
    catalog = session.get(Collection, catalog_id)
    if catalog is None or catalog.teacher_id != teacher_id:
        raise CatalogNotFoundError(f"Catalog {catalog_id} not found")

    courses = ensure_default_course(session, teacher_id=teacher_id)
    target = next((item for item in courses if int(item["id"]) == int(course_id)), None)
    if target is None:
        raise AccessDeniedToContentError("Course not found")

    course_ids = _load_catalog_course_ids(session, teacher_id=teacher_id, catalog_id=catalog_id)
    if int(course_id) not in course_ids:
        course_ids.append(int(course_id))
        _save_catalog_course_ids(session, teacher_id=teacher_id, catalog_id=catalog_id, course_ids=course_ids)

    relations = SqlAlchemyCatalogTaskRelationRepository(session)
    for task_id in _task_ids_for_course(session, teacher_id=teacher_id, course=target):
        if not relations.is_assigned(task_id, catalog_id):
            relations.assign(task_id, catalog_id)
    session.flush()


def remove_course_from_catalog(
    session: Session,
    *,
    teacher_id: int,
    catalog_id: int,
    course_id: int,
) -> None:
    catalog = session.get(Collection, catalog_id)
    if catalog is None or catalog.teacher_id != teacher_id:
        raise CatalogNotFoundError(f"Catalog {catalog_id} not found")

    courses = ensure_default_course(session, teacher_id=teacher_id)
    target = next((item for item in courses if int(item["id"]) == int(course_id)), None)
    if target is None:
        raise AccessDeniedToContentError("Course not found")

    course_ids = [cid for cid in _load_catalog_course_ids(session, teacher_id=teacher_id, catalog_id=catalog_id) if cid != int(course_id)]
    _save_catalog_course_ids(session, teacher_id=teacher_id, catalog_id=catalog_id, course_ids=course_ids)

    task_ids = set(_task_ids_for_course(session, teacher_id=teacher_id, course=target))
    relations = SqlAlchemyCatalogTaskRelationRepository(session)
    for task_id in relations.list_task_ids_by_catalog(catalog_id):
        if task_id in task_ids and relations.is_assigned(task_id, catalog_id):
            relations.remove(task_id, catalog_id)
    session.flush()
