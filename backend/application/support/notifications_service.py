"""In-app notification helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models.support.in_app_notification import InAppNotification
from infrastructure.db.models.user.user import User
from infrastructure.db.models.user.user_role import UserRole as UserRoleModel
from shared.enums import NotificationKind, UserType

MAX_NOTIFICATION_BODY = 512

# В колокольчике студента — только комментарии преподавателя и ответы в обращениях.
INBOX_KINDS: tuple[NotificationKind, ...] = (
    NotificationKind.COMMENT,
    NotificationKind.TICKET_REPLY,
)


def _truncate(text: str, limit: int = MAX_NOTIFICATION_BODY) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def admin_user_ids(db: Session) -> list[int]:
    role_ids = (
        db.execute(
            select(UserRoleModel.user_id).where(UserRoleModel.role == UserType.ADMIN.value)
        )
        .scalars()
        .all()
    )
    legacy_ids = (
        db.execute(
            select(User.id).where(
                User.role == UserType.ADMIN.value,
                User.is_deleted.is_(False),
                User.is_blocked.is_(False),
            )
        )
        .scalars()
        .all()
    )
    merged = {int(uid) for uid in role_ids if uid is not None}
    merged.update(int(uid) for uid in legacy_ids if uid is not None)
    return sorted(merged)


def create_notification(
    db: Session,
    *,
    user_id: int,
    kind: NotificationKind,
    title: str,
    body: str,
    ticket_id: int | None = None,
    task_id: int | None = None,
    submission_id: int | None = None,
) -> InAppNotification:
    row = InAppNotification(
        user_id=user_id,
        ticket_id=ticket_id,
        task_id=task_id,
        submission_id=submission_id,
        kind=kind,
        title=title.strip()[:255],
        body=_truncate(body),
    )
    db.add(row)
    return row


def notify_users(
    db: Session,
    *,
    user_ids: list[int],
    kind: NotificationKind,
    title: str,
    body: str,
    ticket_id: int | None = None,
    exclude_user_id: int | None = None,
) -> None:
    for uid in user_ids:
        if exclude_user_id is not None and uid == exclude_user_id:
            continue
        create_notification(
            db,
            user_id=uid,
            kind=kind,
            title=title,
            body=body,
            ticket_id=ticket_id,
        )


def _inbox_query(db: Session, user_id: int):
    return db.query(InAppNotification).filter(
        InAppNotification.user_id == user_id,
        InAppNotification.kind.in_(INBOX_KINDS),
    )


def list_notifications(db: Session, user_id: int, *, unread_only: bool = False) -> list[InAppNotification]:
    query = _inbox_query(db, user_id)
    if unread_only:
        query = query.filter(InAppNotification.is_read.is_(False))
    return query.order_by(InAppNotification.created_at.desc()).all()


def unread_count(db: Session, user_id: int) -> int:
    return (
        _inbox_query(db, user_id)
        .filter(InAppNotification.is_read.is_(False))
        .count()
    )


def mark_read(db: Session, user_id: int, notification_id: int) -> InAppNotification | None:
    row = (
        db.query(InAppNotification)
        .filter(
            InAppNotification.id == notification_id,
            InAppNotification.user_id == user_id,
        )
        .one_or_none()
    )
    if row is None:
        return None
    row.is_read = True
    db.commit()
    db.refresh(row)
    return row


def mark_all_read(db: Session, user_id: int) -> int:
    rows = (
        db.query(InAppNotification)
        .filter(
            InAppNotification.user_id == user_id,
            InAppNotification.is_read.is_(False),
        )
        .all()
    )
    for row in rows:
        row.is_read = True
    db.commit()
    return len(rows)


def serialize_notification(row: InAppNotification) -> dict:
    return {
        "id": row.id,
        "kind": row.kind.value if hasattr(row.kind, "value") else row.kind,
        "title": row.title,
        "body": row.body,
        "ticket_id": row.ticket_id,
        "task_id": row.task_id,
        "submission_id": row.submission_id,
        "is_read": row.is_read,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
