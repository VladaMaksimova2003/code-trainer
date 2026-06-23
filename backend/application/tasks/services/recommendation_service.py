from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from application.learning.submission_analytics import task_constructions
from application.tasks.services.content_access_service import ContentAccessService
from application.tasks.services.catalog.task_catalog_orchestrator import LEGACY_TASKS_DB, get_task
from domain.policies.rbac.rbac import normalize_role
from domain.services.business.recommendation_engine import (
    build_rec_task,
    manual_next_task,
    manual_prev_task,
    recommend_next_task,
    update_student_state,
)
from domain.entities.learning.recommendation import RecTask, StudentState
from infrastructure.db.models.task.collection import collection_task_association_table
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel


def _normalize_role_set(roles) -> frozenset:
    from domain.policies.rbac.role import Role

    return frozenset(normalize_role(r) for r in roles)


def _task_collection_map(db: Session, task_ids: list[int]) -> dict[int, int | None]:
    if not task_ids:
        return {}
    rows = db.execute(
        select(
            collection_task_association_table.c.task_id,
            collection_task_association_table.c.collection_id,
        )
        .where(collection_task_association_table.c.task_id.in_(task_ids))
        .order_by(collection_task_association_table.c.sort_order)
    ).all()
    mapping: dict[int, int | None] = {tid: None for tid in task_ids}
    for task_id, collection_id in rows:
        if mapping.get(task_id) is None:
            mapping[task_id] = collection_id
    return mapping


def _task_to_rec(
    db: Session,
    task: TaskModel,
    collection_map: dict[int, int | None],
) -> RecTask:
    legacy = LEGACY_TASKS_DB.get(task.id, {})
    constructions = task_constructions(db, task)
    if not constructions:
        constructions = list(legacy.get("constructions") or [])

    raw_type = task.task_type
    try:
        from shared.enums import AssignmentType

        parsed = AssignmentType.parse(raw_type)
        task_type = (
            "blocks"
            if parsed == AssignmentType.TASK_FLOWCHART_TO_CODE
            else parsed.value
        )
    except ValueError:
        task_type = "blocks" if raw_type == "diagram" else raw_type

    return build_rec_task(
        task_id=task.id,
        topic_id=task.topic_id,
        type_id=task_type,
        skills=constructions,
        created_by_teacher=task.teacher_id is not None,
        collection_id=collection_map.get(task.id),
    )


def build_student_state(db: Session, user_id: int, tasks: list[RecTask]) -> StudentState:
    task_by_id = {t.id: t for t in tasks}
    rows = (
        db.query(Submission)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.created_at.asc())
        .all()
    )

    state = StudentState()
    for row in rows:
        rec = task_by_id.get(row.task_id)
        if rec is None:
            task_dict = get_task(db=db, task_id=row.task_id)
            if not task_dict:
                continue
            rec = build_rec_task(
                task_id=row.task_id,
                topic_id=task_dict.get("topic_id"),
                type_id=str(task_dict.get("type") or "algorithm"),
                skills=list(task_dict.get("constructions") or []),
                created_by_teacher=False,
                collection_id=None,
            )
        update_student_state(state, rec, success=row.success is True)
    return state


def load_accessible_rec_tasks(
    db: Session,
    user_id: int,
    roles,
) -> list[RecTask]:
    access = ContentAccessService(db)
    allowed = access.list_accessible_task_ids(user_id, _normalize_role_set(roles))
    if not allowed:
        return []

    stmt = (
        select(TaskModel)
        .where(TaskModel.id.in_(allowed), TaskModel.is_delete.is_(False))
        .options(joinedload(TaskModel.constructions))
    )
    orm_tasks = db.execute(stmt).unique().scalars().all()
    collection_map = _task_collection_map(db, [t.id for t in orm_tasks])
    return [_task_to_rec(db, task, collection_map) for task in orm_tasks]


def get_next_recommendation(
    db: Session,
    user_id: int,
    roles,
    *,
    current_task_id: int | None = None,
) -> dict | None:
    rec_tasks = load_accessible_rec_tasks(db, user_id, roles)
    if not rec_tasks:
        return None

    state = build_student_state(db, user_id, rec_tasks)
    next_task = recommend_next_task(
        state,
        rec_tasks,
        current_task_id=current_task_id,
        exclude_collection_tasks=True,
    )
    if next_task is None:
        return None

    task_dict = get_task(db=db, task_id=next_task.id)
    if not task_dict:
        return None

    return {
        "task_id": next_task.id,
        "title": task_dict.get("title"),
        "topic_id": next_task.topic_id,
        "type_id": next_task.type_id,
        "skills_required": list(next_task.skills_required),
        "mode": "adaptive",
    }


def get_catalog_navigation(
    db: Session,
    user_id: int,
    roles,
    catalog_id: int,
    current_task_id: int | None = None,
) -> dict:
    access = ContentAccessService(db)
    if not access.can_access_assignment_set(user_id, _normalize_role_set(roles), catalog_id):
        raise PermissionError(f"Catalog {catalog_id} is not accessible")

    rows = db.execute(
        select(
            collection_task_association_table.c.task_id,
            collection_task_association_table.c.sort_order,
        )
        .where(collection_task_association_table.c.collection_id == catalog_id)
        .order_by(collection_task_association_table.c.sort_order, collection_task_association_table.c.task_id)
    ).all()
    ordered_ids = [row.task_id for row in rows]

    prev_id = None
    next_id = None
    if current_task_id is not None:
        prev_id = manual_prev_task(ordered_ids, current_task_id)
        next_id = manual_next_task(ordered_ids, current_task_id)

    return {
        "catalog_id": catalog_id,
        "task_ids": ordered_ids,
        "current_task_id": current_task_id,
        "prev_task_id": prev_id,
        "next_task_id": next_id,
        "mode": "manual",
    }
