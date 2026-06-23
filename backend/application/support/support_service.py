"""Support ticket business logic."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session, joinedload

from application.support import notifications_service
from domain.policies.permissions.permissions import Permission, can
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.support.support_ticket import SupportTicket
from infrastructure.db.models.support.support_ticket_message import SupportTicketMessage
from infrastructure.db.models.task.task import Task
from infrastructure.db.models.user.user import User
from shared.enums import (
    NotificationKind,
    SupportTicketCategory,
    SupportTicketMessageType,
    SupportTicketStatus,
    SupportTicketTarget,
    UserType,
)

MIN_BODY_LENGTH = 1
MAX_BODY_LENGTH = 8192
MAX_SUBJECT_LENGTH = 255

_TEACHER_CATEGORIES = {
    SupportTicketCategory.TASK_CONTENT,
    SupportTicketCategory.AUTOGRADER,
}
_ADMIN_CATEGORIES = {
    SupportTicketCategory.TECHNICAL,
    SupportTicketCategory.ACCOUNT,
    SupportTicketCategory.OTHER,
}

_CATEGORY_LABELS = {
    SupportTicketCategory.TASK_CONTENT: "Ошибка в задании",
    SupportTicketCategory.AUTOGRADER: "Проблема с автопроверкой",
    SupportTicketCategory.TECHNICAL: "Техническая проблема",
    SupportTicketCategory.ACCOUNT: "Аккаунт и доступ",
    SupportTicketCategory.OTHER: "Другое",
}

_STATUS_LABELS = {
    SupportTicketStatus.OPEN: "Открыто",
    SupportTicketStatus.IN_PROGRESS: "В работе",
    SupportTicketStatus.RESOLVED: "Решено",
    SupportTicketStatus.CLOSED: "Закрыто",
}


class SupportTicketNotFoundError(LookupError):
    pass


class SupportTicketAccessError(PermissionError):
    pass


class SupportTicketValidationError(ValueError):
    pass


def _normalize_body(body: str) -> str:
    text = (body or "").strip()
    if len(text) < MIN_BODY_LENGTH:
        raise SupportTicketValidationError("Message must not be empty.")
    if len(text) > MAX_BODY_LENGTH:
        raise SupportTicketValidationError(
            f"Message must be at most {MAX_BODY_LENGTH} characters."
        )
    return text


def _normalize_subject(subject: str | None, category: SupportTicketCategory, task: Task | None) -> str:
    text = (subject or "").strip()
    if not text:
        label = _CATEGORY_LABELS.get(category, category.value)
        if task is not None:
            text = f"{label}: {task.title}"
        else:
            text = label
    if len(text) > MAX_SUBJECT_LENGTH:
        text = text[:MAX_SUBJECT_LENGTH]
    return text


def _parse_category(raw: str) -> SupportTicketCategory:
    try:
        return SupportTicketCategory(str(raw).strip().lower())
    except ValueError as exc:
        raise SupportTicketValidationError(f"Invalid category: {raw}") from exc


def _parse_status(raw: str) -> SupportTicketStatus:
    try:
        return SupportTicketStatus(str(raw).strip().lower())
    except ValueError as exc:
        raise SupportTicketValidationError(f"Invalid status: {raw}") from exc


def _user_roles(user_id: int, db: Session) -> frozenset[UserType]:
    from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository

    return SqlAlchemyUserRoleRepository(db).get_roles_for_user(user_id)


def _can_manage_support(user_id: int, db: Session) -> bool:
    return can(_user_roles(user_id, db), Permission.MANAGE_SUPPORT_TICKETS)


def _get_ticket(db: Session, ticket_id: int) -> SupportTicket | None:
    return (
        db.query(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.assignee),
            joinedload(SupportTicket.task),
        )
        .filter(SupportTicket.id == ticket_id)
        .one_or_none()
    )


def _validate_task_context(
    db: Session,
    *,
    category: SupportTicketCategory,
    author_id: int,
    task_id: int | None,
    submission_id: int | None,
) -> tuple[Task | None, Submission | None]:
    task: Task | None = None
    submission: Submission | None = None

    if category in _TEACHER_CATEGORIES:
        if task_id is None:
            raise SupportTicketValidationError("task_id is required for this category.")
        task = db.get(Task, task_id)
        if task is None or task.is_delete:
            raise SupportTicketNotFoundError("Task not found")

    if task_id is not None and task is None:
        task = db.get(Task, task_id)
        if task is None or task.is_delete:
            raise SupportTicketNotFoundError("Task not found")

    if submission_id is not None:
        submission = db.get(Submission, submission_id)
        if submission is None:
            raise SupportTicketNotFoundError("Submission not found")
        if submission.user_id != author_id:
            raise SupportTicketAccessError("You can only reference your own submissions")
        if task is not None and submission.task_id != task.id:
            raise SupportTicketValidationError("submission_id does not match task_id")

    return task, submission


def _resolve_routing(
    category: SupportTicketCategory,
    task: Task | None,
) -> tuple[SupportTicketTarget, int | None]:
    if category in _TEACHER_CATEGORIES:
        if task is None or task.teacher_id is None:
            return SupportTicketTarget.ADMIN, None
        return SupportTicketTarget.TEACHER, task.teacher_id
    return SupportTicketTarget.ADMIN, None


def _participant_ids(ticket: SupportTicket, db: Session) -> list[int]:
    ids = {ticket.author_id}
    if ticket.assignee_id is not None:
        ids.add(ticket.assignee_id)
    if ticket.target == SupportTicketTarget.ADMIN:
        ids.update(notifications_service.admin_user_ids(db))
    return sorted(ids)


def assert_can_view_ticket(db: Session, user_id: int, ticket: SupportTicket) -> None:
    if ticket.author_id == user_id:
        return
    if ticket.target == SupportTicketTarget.TEACHER and ticket.assignee_id == user_id:
        roles = _user_roles(user_id, db)
        if UserType.TEACHER in roles or UserType.ADMIN in roles:
            return
    if ticket.target == SupportTicketTarget.ADMIN and _can_manage_support(user_id, db):
        return
    raise SupportTicketAccessError("You do not have access to this ticket")


def assert_can_post_message(db: Session, user_id: int, ticket: SupportTicket) -> None:
    if ticket.status == SupportTicketStatus.CLOSED:
        raise SupportTicketValidationError("Ticket is closed.")
    assert_can_view_ticket(db, user_id, ticket)


def assert_can_manage_ticket(db: Session, user_id: int, ticket: SupportTicket) -> None:
    if ticket.target == SupportTicketTarget.ADMIN and _can_manage_support(user_id, db):
        return
    roles = _user_roles(user_id, db)
    if (
        ticket.target == SupportTicketTarget.TEACHER
        and ticket.assignee_id == user_id
        and (UserType.TEACHER in roles or UserType.ADMIN in roles)
    ):
        return
    raise SupportTicketAccessError("You cannot manage this ticket")


def serialize_message(message: SupportTicketMessage) -> dict[str, Any]:
    author_name = message.author.name if message.author else None
    msg_type = message.message_type.value if hasattr(message.message_type, "value") else message.message_type
    return {
        "id": message.id,
        "ticket_id": message.ticket_id,
        "author_id": message.author_id,
        "author_name": author_name,
        "body": message.body,
        "message_type": msg_type,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


def serialize_ticket(ticket: SupportTicket, *, include_messages: bool = False) -> dict[str, Any]:
    category = ticket.category.value if hasattr(ticket.category, "value") else ticket.category
    status = ticket.status.value if hasattr(ticket.status, "value") else ticket.status
    target = ticket.target.value if hasattr(ticket.target, "value") else ticket.target
    payload: dict[str, Any] = {
        "id": ticket.id,
        "author_id": ticket.author_id,
        "author_name": ticket.author.name if ticket.author else None,
        "category": category,
        "subject": ticket.subject,
        "status": status,
        "target": target,
        "assignee_id": ticket.assignee_id,
        "assignee_name": ticket.assignee.name if ticket.assignee else None,
        "task_id": ticket.task_id,
        "task_title": ticket.task.title if ticket.task else None,
        "submission_id": ticket.submission_id,
        "context": ticket.context_json or {},
        "escalated_at": ticket.escalated_at.isoformat() if ticket.escalated_at else None,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
        "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
    }
    if include_messages:
        payload["messages"] = [serialize_message(m) for m in ticket.messages]
    return payload


def _add_system_message(
    db: Session,
    ticket: SupportTicket,
    body: str,
) -> SupportTicketMessage:
    message = SupportTicketMessage(
        ticket_id=ticket.id,
        author_id=None,
        body=body,
        message_type=SupportTicketMessageType.SYSTEM,
    )
    db.add(message)
    return message


def create_ticket(
    db: Session,
    *,
    author_id: int,
    category_raw: str,
    body: str,
    subject: str | None = None,
    task_id: int | None = None,
    submission_id: int | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    category = _parse_category(category_raw)
    normalized_body = _normalize_body(body)
    task, submission = _validate_task_context(
        db,
        category=category,
        author_id=author_id,
        task_id=task_id,
        submission_id=submission_id,
    )
    target, assignee_id = _resolve_routing(category, task)

    ticket = SupportTicket(
        author_id=author_id,
        category=category,
        subject=_normalize_subject(subject, category, task),
        status=SupportTicketStatus.OPEN,
        target=target,
        assignee_id=assignee_id,
        task_id=task.id if task else task_id,
        submission_id=submission.id if submission else submission_id,
        context_json=context or None,
    )
    db.add(ticket)
    db.flush()

    first_message = SupportTicketMessage(
        ticket_id=ticket.id,
        author_id=author_id,
        body=normalized_body,
        message_type=SupportTicketMessageType.USER,
    )
    db.add(first_message)

    if assignee_id is not None:
        notifications_service.create_notification(
            db,
            user_id=assignee_id,
            kind=NotificationKind.TICKET_CREATED,
            title="Новое обращение по заданию",
            body=ticket.subject,
            ticket_id=ticket.id,
        )
    elif target == SupportTicketTarget.ADMIN:
        notifications_service.notify_users(
            db,
            user_ids=notifications_service.admin_user_ids(db),
            kind=NotificationKind.TICKET_CREATED,
            title="Новое обращение в поддержку",
            body=ticket.subject,
            ticket_id=ticket.id,
            exclude_user_id=author_id,
        )

    db.commit()
    db.refresh(ticket)
    ticket.author = db.get(User, author_id)
    if assignee_id:
        ticket.assignee = db.get(User, assignee_id)
    if ticket.task_id:
        ticket.task = db.get(Task, ticket.task_id)
    return serialize_ticket(ticket)


def list_my_tickets(db: Session, author_id: int) -> list[dict[str, Any]]:
    rows = (
        db.query(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.assignee),
            joinedload(SupportTicket.task),
        )
        .filter(SupportTicket.author_id == author_id)
        .order_by(SupportTicket.updated_at.desc())
        .all()
    )
    return [serialize_ticket(row) for row in rows]


def list_teacher_inbox(db: Session, teacher_id: int) -> list[dict[str, Any]]:
    rows = (
        db.query(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.assignee),
            joinedload(SupportTicket.task),
        )
        .filter(
            SupportTicket.target == SupportTicketTarget.TEACHER,
            SupportTicket.assignee_id == teacher_id,
        )
        .order_by(SupportTicket.updated_at.desc())
        .all()
    )
    return [serialize_ticket(row) for row in rows]


def list_admin_inbox(db: Session) -> list[dict[str, Any]]:
    rows = (
        db.query(SupportTicket)
        .options(
            joinedload(SupportTicket.author),
            joinedload(SupportTicket.assignee),
            joinedload(SupportTicket.task),
        )
        .filter(SupportTicket.target == SupportTicketTarget.ADMIN)
        .order_by(SupportTicket.updated_at.desc())
        .all()
    )
    return [serialize_ticket(row) for row in rows]


def get_ticket_detail(db: Session, user_id: int, ticket_id: int) -> dict[str, Any]:
    ticket = _get_ticket(db, ticket_id)
    if ticket is None:
        raise SupportTicketNotFoundError("Ticket not found")
    assert_can_view_ticket(db, user_id, ticket)
    messages = (
        db.query(SupportTicketMessage)
        .options(joinedload(SupportTicketMessage.author))
        .filter(SupportTicketMessage.ticket_id == ticket_id)
        .order_by(SupportTicketMessage.created_at.asc())
        .all()
    )
    ticket.messages = messages
    return serialize_ticket(ticket, include_messages=True)


def list_ticket_messages(db: Session, user_id: int, ticket_id: int) -> list[dict[str, Any]]:
    ticket = _get_ticket(db, ticket_id)
    if ticket is None:
        raise SupportTicketNotFoundError("Ticket not found")
    assert_can_view_ticket(db, user_id, ticket)
    rows = (
        db.query(SupportTicketMessage)
        .options(joinedload(SupportTicketMessage.author))
        .filter(SupportTicketMessage.ticket_id == ticket_id)
        .order_by(SupportTicketMessage.created_at.asc())
        .all()
    )
    return [serialize_message(row) for row in rows]


def post_message(
    db: Session,
    *,
    user_id: int,
    ticket_id: int,
    body: str,
) -> dict[str, Any]:
    ticket = _get_ticket(db, ticket_id)
    if ticket is None:
        raise SupportTicketNotFoundError("Ticket not found")
    assert_can_post_message(db, user_id, ticket)

    normalized_body = _normalize_body(body)
    if ticket.status == SupportTicketStatus.RESOLVED:
        ticket.status = SupportTicketStatus.OPEN
        ticket.resolved_at = None
        _add_system_message(db, ticket, "Статус изменён: открыто (новое сообщение).")

    message = SupportTicketMessage(
        ticket_id=ticket.id,
        author_id=user_id,
        body=normalized_body,
        message_type=SupportTicketMessageType.USER,
    )
    db.add(message)
    ticket.updated_at = datetime.now(timezone.utc)

    recipients = [
        uid for uid in _participant_ids(ticket, db) if uid != user_id
    ]
    author = db.get(User, user_id)
    author_label = author.name if author else "Участник"
    notifications_service.notify_users(
        db,
        user_ids=recipients,
        kind=NotificationKind.TICKET_REPLY,
        title="Новый ответ в обращении",
        body=f"{author_label}: {normalized_body[:120]}",
        ticket_id=ticket.id,
        exclude_user_id=user_id,
    )

    db.commit()
    db.refresh(message)
    message.author = author
    return serialize_message(message)


def update_ticket(
    db: Session,
    *,
    user_id: int,
    ticket_id: int,
    status_raw: str | None = None,
    escalate: bool = False,
    note: str | None = None,
) -> dict[str, Any]:
    ticket = _get_ticket(db, ticket_id)
    if ticket is None:
        raise SupportTicketNotFoundError("Ticket not found")
    assert_can_manage_ticket(db, user_id, ticket)

    if escalate:
        if ticket.target != SupportTicketTarget.TEACHER:
            raise SupportTicketValidationError("Only teacher tickets can be escalated.")
        if ticket.assignee_id != user_id and not _can_manage_support(user_id, db):
            raise SupportTicketAccessError("Only the assigned teacher can escalate.")
        ticket.target = SupportTicketTarget.ADMIN
        ticket.assignee_id = None
        ticket.escalated_at = datetime.now(timezone.utc)
        ticket.escalated_by_id = user_id
        system_text = "Обращение передано администратору."
        if note and note.strip():
            system_text = f"{system_text} {note.strip()}"
        _add_system_message(db, ticket, system_text)
        notifications_service.notify_users(
            db,
            user_ids=notifications_service.admin_user_ids(db),
            kind=NotificationKind.TICKET_STATUS,
            title="Эскалация обращения",
            body=ticket.subject,
            ticket_id=ticket.id,
            exclude_user_id=user_id,
        )
        notifications_service.create_notification(
            db,
            user_id=ticket.author_id,
            kind=NotificationKind.TICKET_STATUS,
            title="Обращение передано администратору",
            body=ticket.subject,
            ticket_id=ticket.id,
        )

    if status_raw is not None:
        new_status = _parse_status(status_raw)
        if new_status != ticket.status:
            old_label = _STATUS_LABELS.get(ticket.status, ticket.status.value)
            new_label = _STATUS_LABELS.get(new_status, new_status.value)
            ticket.status = new_status
            if new_status == SupportTicketStatus.RESOLVED:
                ticket.resolved_at = datetime.now(timezone.utc)
            elif new_status in {SupportTicketStatus.OPEN, SupportTicketStatus.IN_PROGRESS}:
                ticket.resolved_at = None
            _add_system_message(db, ticket, f"Статус изменён: {old_label} → {new_label}.")
            notifications_service.create_notification(
                db,
                user_id=ticket.author_id,
                kind=NotificationKind.TICKET_STATUS,
                title="Статус обращения изменён",
                body=f"{ticket.subject}: {new_label}",
                ticket_id=ticket.id,
            )

    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return serialize_ticket(ticket)
