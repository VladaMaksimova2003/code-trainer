"""Group detail, catalog assignment, and per-student catalog progress for teachers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models.task.collection import (
    Collection,
    collection_task_association_table,
)
from infrastructure.db.models.learning.group import Group, group_member_association_table
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user import User
from application.users.services.study_identity import load_study_identity_by_user_ids


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_deadline(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    raw = str(value).strip()
    if not raw:
        return None
    text = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _catalog_task_ids(db: Session, catalog_id: int) -> list[int]:
    return list(
        db.execute(
            select(collection_task_association_table.c.task_id)
            .where(collection_task_association_table.c.collection_id == catalog_id)
            .order_by(
                collection_task_association_table.c.sort_order,
                collection_task_association_table.c.task_id,
            )
        )
        .scalars()
        .all()
    )


def _student_solved_in_catalog(
    db: Session,
    student_id: int,
    task_ids: list[int],
    *,
    before: datetime | None = None,
) -> set[int]:
    if not task_ids:
        return set()
    q = db.query(Submission).filter(
        Submission.user_id == student_id,
        Submission.task_id.in_(task_ids),
        Submission.success.is_(True),
    )
    if before is not None:
        q = q.filter(Submission.created_at <= before)
    rows = q.all()
    return {s.task_id for s in rows}


def _deadline_status(
    *,
    deadline_at: datetime | None,
    solved_count: int,
    total_tasks: int,
    all_solved_before_deadline: bool,
) -> str | None:
    """on_time | late | pending | no_deadline"""
    if deadline_at is None:
        return "no_deadline"
    if total_tasks == 0:
        return "pending"
    now = _utc_now()
    if solved_count >= total_tasks:
        return "on_time" if all_solved_before_deadline else "late"
    if now <= deadline_at:
        return "pending"
    return "late"


def _build_student_summaries(
    db: Session,
    members: list[dict[str, Any]],
    catalog_tasks: dict[int, list[int]],
    *,
    catalog_id: int | None = None,
) -> list[dict[str, Any]]:
    catalog_ids = (
        [catalog_id]
        if catalog_id is not None
        else list(catalog_tasks.keys())
    )
    summaries: list[dict[str, Any]] = []
    for member in members:
        sid = member["id"]
        task_union: set[int] = set()
        for cid in catalog_ids:
            task_union.update(catalog_tasks.get(cid, []))
        total = len(task_union)
        solved = _student_solved_in_catalog(db, sid, list(task_union))
        solved_count = len(solved)
        pct = round(100.0 * solved_count / total, 1) if total else 0.0
        last_sub = None
        if task_union:
            last_sub = (
                db.query(Submission)
                .filter(
                    Submission.user_id == sid,
                    Submission.task_id.in_(task_union),
                )
                .order_by(Submission.created_at.desc())
                .first()
            )
        summaries.append(
            {
                "student_id": sid,
                "student_name": member["name"],
                "study_place": member.get("study_place"),
                "study_group": member.get("study_group"),
                "study_identity": member.get("study_identity"),
                "solved_count": solved_count,
                "total_tasks": total,
                "progress_percent": pct,
                "last_activity_at": last_sub.created_at.isoformat()
                if last_sub and last_sub.created_at
                else None,
            }
        )
    return summaries


def build_group_dashboard(
    db: Session,
    teacher_id: int,
    group_id: int,
    *,
    catalog_id: int | None = None,
) -> dict[str, Any] | None:
    group = db.get(Group, group_id)
    if group is None or group.teacher_id != teacher_id:
        return None

    member_ids = list(
        db.execute(
            select(group_member_association_table.c.student_id).where(
                group_member_association_table.c.group_id == group_id
            )
        ).scalars().all()
    )
    members: list[dict[str, Any]] = []
    if member_ids:
        users = db.query(User).filter(User.id.in_(member_ids)).all()
        user_map = {u.id: u for u in users}
        study_by_user = load_study_identity_by_user_ids(db, member_ids)
        for sid in member_ids:
            u = user_map.get(sid)
            study = study_by_user.get(
                sid,
                {"study_place": None, "study_group": None, "study_identity": None},
            )
            members.append(
                {
                    "id": sid,
                    "name": u.name if u else f"Студент #{sid}",
                    "email": u.email if u else None,
                    "study_place": study["study_place"],
                    "study_group": study["study_group"],
                    "study_identity": study["study_identity"],
                }
            )

    catalog_rows = (
        db.query(Collection)
        .filter(
            Collection.teacher_id == teacher_id,
            Collection.group_id == group_id,
            Collection.is_archived.is_(False),
        )
        .order_by(Collection.name)
        .all()
    )

    catalogs = []
    catalog_tasks: dict[int, list[int]] = {}
    for row in catalog_rows:
        task_ids = _catalog_task_ids(db, row.id)
        catalog_tasks[row.id] = task_ids
        catalogs.append(
            {
                "id": row.id,
                "title": row.name,
                "description": row.description or "",
                "deadline_at": row.deadline_at.isoformat() if row.deadline_at else None,
                "task_count": len(task_ids),
                "visibility": row.visibility.value
                if hasattr(row.visibility, "value")
                else str(row.visibility),
            }
        )

    progress_rows: list[dict[str, Any]] = []
    for member in members:
        sid = member["id"]
        for cat in catalogs:
            cid = cat["id"]
            task_ids = catalog_tasks.get(cid, [])
            total = len(task_ids)
            deadline_at = None
            cat_row = db.get(Collection, cid)
            if cat_row and cat_row.deadline_at:
                deadline_at = cat_row.deadline_at
                if deadline_at.tzinfo is None:
                    deadline_at = deadline_at.replace(tzinfo=timezone.utc)

            solved_all = _student_solved_in_catalog(db, sid, task_ids)
            solved_count = len(solved_all)
            solved_before = (
                _student_solved_in_catalog(db, sid, task_ids, before=deadline_at)
                if deadline_at
                else solved_all
            )
            all_before = total > 0 and len(solved_before) >= total
            pct = round(100.0 * solved_count / total, 1) if total else 0.0
            progress_rows.append(
                {
                    "student_id": sid,
                    "student_name": member["name"],
                    "study_place": member.get("study_place"),
                    "study_group": member.get("study_group"),
                    "study_identity": member.get("study_identity"),
                    "catalog_id": cid,
                    "catalog_title": cat["title"],
                    "solved_count": solved_count,
                    "total_tasks": total,
                    "progress_percent": pct,
                    "deadline_at": cat["deadline_at"],
                    "deadline_status": _deadline_status(
                        deadline_at=deadline_at,
                        solved_count=solved_count,
                        total_tasks=total,
                        all_solved_before_deadline=all_before,
                    ),
                }
            )

    unassigned_catalogs = (
        db.query(Collection)
        .filter(
            Collection.teacher_id == teacher_id,
            Collection.is_archived.is_(False),
            Collection.group_id.is_(None),
        )
        .order_by(Collection.name)
        .all()
    )

    if catalog_id is not None and catalog_id not in catalog_tasks:
        return None

    filtered_progress = (
        [r for r in progress_rows if r["catalog_id"] == catalog_id]
        if catalog_id is not None
        else progress_rows
    )

    student_summaries = _build_student_summaries(
        db,
        members,
        catalog_tasks,
        catalog_id=catalog_id,
    )
    avg_progress = (
        round(
            sum(s["progress_percent"] for s in student_summaries) / len(student_summaries),
            0,
        )
        if student_summaries
        else 0
    )

    return {
        "group": {
            "id": group.id,
            "name": group.name,
            "teacher_id": group.teacher_id,
            "member_count": len(members),
            "avg_progress_percent": avg_progress,
        },
        "members": members,
        "catalogs": catalogs,
        "student_catalog_progress": filtered_progress,
        "student_summaries": student_summaries,
        "assignable_catalogs": [
            {"id": r.id, "title": r.name, "task_count": len(_catalog_task_ids(db, r.id))}
            for r in unassigned_catalogs
        ],
    }


def _task_progress_status(
    db: Session,
    student_id: int,
    task_id: int,
) -> tuple[str, int]:
    """Return (status, attempts): solved | in_progress | not_started."""
    status, attempts, _, _ = _task_progress_detail(db, student_id, task_id)
    return status, attempts


def _task_progress_detail(
    db: Session,
    student_id: int,
    task_id: int,
) -> tuple[str, int, str | None, str | None]:
    """Return (status, attempts, last_activity_at iso, language)."""
    rows = (
        db.query(Submission)
        .filter(
            Submission.user_id == student_id,
            Submission.task_id == task_id,
        )
        .order_by(Submission.created_at.desc())
        .all()
    )
    if not rows:
        return "not_started", 0, None, None
    last = rows[0]
    last_at = last.created_at.isoformat() if last.created_at else None
    language = last.language or None
    attempts = len(rows)
    if any(s.success is True for s in rows):
        return "solved", attempts, last_at, language
    return "in_progress", attempts, last_at, language


def build_student_group_workspace(
    db: Session,
    student_id: int,
    group_id: int,
) -> dict[str, Any] | None:
    group = db.get(Group, group_id)
    if group is None:
        return None

    member_ids = set(
        db.execute(
            select(group_member_association_table.c.student_id).where(
                group_member_association_table.c.group_id == group_id
            )
        ).scalars().all()
    )
    if student_id not in member_ids:
        return None

    progress = build_student_group_task_progress(
        db,
        group.teacher_id,
        group_id,
        student_id,
    )
    if progress is None:
        return None

    teacher = db.get(User, group.teacher_id)
    return {
        "group": {
            "id": group.id,
            "name": group.name,
        },
        "teacher": {
            "id": group.teacher_id,
            "name": teacher.name if teacher else f"Преподаватель #{group.teacher_id}",
        },
        "catalogs": progress["catalogs"],
    }


def build_student_joined_groups_overview(
    db: Session,
    student_id: int,
) -> list[dict[str, Any]]:
    group_ids = list(
        db.execute(
            select(group_member_association_table.c.group_id).where(
                group_member_association_table.c.student_id == student_id
            )
        ).scalars().all()
    )
    if not group_ids:
        return []

    groups = db.query(Group).filter(Group.id.in_(group_ids)).order_by(Group.name).all()
    overview: list[dict[str, Any]] = []
    now = _utc_now()

    for group in groups:
        workspace = build_student_group_workspace(db, student_id, group.id)
        if workspace is None:
            continue

        catalogs = workspace["catalogs"]
        task_count = sum(len(catalog["tasks"]) for catalog in catalogs)
        solved_count = sum(
            1
            for catalog in catalogs
            for task in catalog["tasks"]
            if task["status"] == "solved"
        )

        deadline_alert = None
        for catalog in catalogs:
            deadline_raw = catalog.get("deadline_at")
            if not deadline_raw:
                continue
            deadline_at = _parse_deadline(deadline_raw)
            if deadline_at is None or deadline_at <= now:
                continue
            unsolved = sum(
                1 for task in catalog["tasks"] if task["status"] != "solved"
            )
            if unsolved <= 0:
                continue
            hours_left = (deadline_at - now).total_seconds() / 3600
            level = "urgent" if hours_left <= 48 else "soon"
            deadline_alert = {
                "catalog_id": catalog["catalog_id"],
                "catalog_title": catalog["catalog_title"],
                "deadline_at": deadline_at.isoformat(),
                "level": level,
                "unsolved_count": unsolved,
            }
            break

        overview.append(
            {
                "id": group.id,
                "name": group.name,
                "teacher": workspace["teacher"],
                "catalog_count": len(catalogs),
                "task_count": task_count,
                "solved_count": solved_count,
                "deadline_alert": deadline_alert,
            }
        )

    return overview


def build_student_assigned_catalogs(
    db: Session,
    student_id: int,
) -> list[dict[str, Any]]:
    """Flat list of group-assigned catalogs for the student learn hub."""
    rows: list[dict[str, Any]] = []
    for group in build_student_joined_groups_overview(db, student_id):
        workspace = build_student_group_workspace(db, student_id, group["id"])
        if workspace is None:
            continue
        teacher_name = str(workspace.get("teacher", {}).get("name") or "")
        for catalog in workspace.get("catalogs") or []:
            tasks = catalog.get("tasks") or []
            solved_count = sum(1 for task in tasks if task.get("status") == "solved")
            rows.append(
                {
                    "catalog_id": catalog["catalog_id"],
                    "catalog_title": catalog["catalog_title"],
                    "catalog_description": catalog.get("catalog_description") or "",
                    "group_id": group["id"],
                    "group_name": group["name"],
                    "teacher_name": teacher_name,
                    "deadline_at": catalog.get("deadline_at"),
                    "solved_count": solved_count,
                    "total_tasks": len(tasks),
                }
            )
    return rows


def build_student_own_group_catalogs(
    db: Session,
    student_id: int,
    group_id: int,
) -> dict[str, Any] | None:
    group = db.get(Group, group_id)
    if group is None:
        return None

    member_ids = set(
        db.execute(
            select(group_member_association_table.c.student_id).where(
                group_member_association_table.c.group_id == group_id
            )
        ).scalars().all()
    )
    if student_id not in member_ids:
        return None

    return build_student_group_task_progress(
        db,
        group.teacher_id,
        group_id,
        student_id,
    )


def build_student_group_task_progress(
    db: Session,
    teacher_id: int,
    group_id: int,
    student_id: int,
) -> dict[str, Any] | None:
    group = db.get(Group, group_id)
    if group is None or group.teacher_id != teacher_id:
        return None

    member_ids = set(
        db.execute(
            select(group_member_association_table.c.student_id).where(
                group_member_association_table.c.group_id == group_id
            )
        ).scalars().all()
    )
    if student_id not in member_ids:
        return None

    user = db.get(User, student_id)
    catalog_rows = (
        db.query(Collection)
        .filter(
            Collection.teacher_id == teacher_id,
            Collection.group_id == group_id,
            Collection.is_archived.is_(False),
        )
        .order_by(Collection.name)
        .all()
    )

    catalogs_out: list[dict[str, Any]] = []
    for cat in catalog_rows:
        task_ids = _catalog_task_ids(db, cat.id)
        tasks_out: list[dict[str, Any]] = []
        for tid in task_ids:
            task = db.get(TaskModel, tid)
            if task is None or task.is_delete:
                continue
            status, attempts, last_activity_at, language = _task_progress_detail(
                db, student_id, tid
            )
            raw_type = task.task_type
            public_type = raw_type if raw_type != "diagram" else "blocks"
            tasks_out.append(
                {
                    "task_id": tid,
                    "title": task.title,
                    "task_type": raw_type,
                    "type": public_type,
                    "difficulty": task.difficulty,
                    "language": language,
                    "status": status,
                    "attempts": attempts,
                    "last_activity_at": last_activity_at,
                }
            )
        catalogs_out.append(
            {
                "catalog_id": cat.id,
                "catalog_title": cat.name,
                "catalog_description": cat.description or "",
                "deadline_at": cat.deadline_at.isoformat() if cat.deadline_at else None,
                "tasks": tasks_out,
            }
        )

    return {
        "student_id": student_id,
        "student_name": user.name if user else f"Студент #{student_id}",
        "catalogs": catalogs_out,
    }


def assign_catalog_to_group(
    db: Session,
    teacher_id: int,
    group_id: int,
    catalog_id: int,
    *,
    deadline_at: datetime | str | None = None,
    make_private: bool = True,
) -> dict[str, Any] | None:
    group = db.get(Group, group_id)
    if group is None or group.teacher_id != teacher_id:
        return None
    row = db.get(Collection, catalog_id)
    if row is None or row.teacher_id != teacher_id or row.is_archived:
        return None
    if row.group_id is not None and row.group_id != group_id:
        raise ValueError("Каталог уже назначен другой группе")

    parsed_deadline = _parse_deadline(deadline_at)
    row.group_id = group_id
    row.deadline_at = parsed_deadline
    if make_private:
        from shared.enums import AssignmentSetVisibility

        row.visibility = AssignmentSetVisibility.PRIVATE
    db.commit()
    db.refresh(row)
    return {
        "catalog_id": row.id,
        "group_id": row.group_id,
        "deadline_at": row.deadline_at.isoformat() if row.deadline_at else None,
    }


def get_teacher_submission_detail(
    db: Session,
    teacher_id: int,
    submission_id: int,
) -> dict[str, Any] | None:
    from application.learning.use_cases.analytics.service import _teacher_group_student_ids

    submission = db.get(Submission, submission_id)
    if submission is None or submission.user_id is None:
        return None

    allowed_students = _teacher_group_student_ids(db, teacher_id)
    if submission.user_id not in allowed_students:
        return None

    task = db.get(TaskModel, submission.task_id)
    if task is None or task.teacher_id != teacher_id:
        return None

    user = db.get(User, submission.user_id)
    return {
        "id": submission.id,
        "task_id": submission.task_id,
        "task_title": task.title,
        "student_id": submission.user_id,
        "student_name": user.name if user else "—",
        "language": submission.language,
        "code": submission.code,
        "status": submission.status,
        "success": submission.success,
        "created_at": submission.created_at.isoformat() if submission.created_at else None,
    }
