from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from api.support.schemas import (
    SupportTicketCreateRequest,
    SupportTicketListResponse,
    SupportTicketMessageCreateRequest,
    SupportTicketMessageResponse,
    SupportTicketResponse,
    SupportTicketUpdateRequest,
    SupportTemplatesResponse,
)
from application.auth.dto import CurrentUserResult
from application.support import support_service
from application.support.support_service import (
    SupportTicketAccessError,
    SupportTicketNotFoundError,
    SupportTicketValidationError,
)
from application.support.templates import get_support_templates
from application.users.services.teacher_service import is_teacher_user
from domain.policies.permissions.permissions import Permission
from infrastructure.db.models.user.user import User
from infrastructure.db.session import get_db

router = APIRouter()


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, SupportTicketNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, SupportTicketAccessError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, SupportTicketValidationError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    raise exc


@router.get("/templates", response_model=SupportTemplatesResponse)
def list_support_templates(
    context: str = Query(default="general"),
    user: CurrentUserResult = Depends(require_permission(Permission.SUBMIT_SUPPORT_REQUEST)),
):
    role = user.role.value if hasattr(user.role, "value") else str(user.role)
    return get_support_templates(role=role, context=context)


@router.post("/tickets", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
def create_support_ticket(
    payload: SupportTicketCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SUBMIT_SUPPORT_REQUEST)),
):
    try:
        return support_service.create_ticket(
            db,
            author_id=user.id,
            category_raw=payload.category,
            body=payload.body,
            subject=payload.subject,
            task_id=payload.task_id,
            submission_id=payload.submission_id,
            context=payload.context,
        )
    except (SupportTicketNotFoundError, SupportTicketAccessError, SupportTicketValidationError) as exc:
        raise _http_error(exc) from exc


@router.get("/tickets/mine", response_model=SupportTicketListResponse)
def list_my_support_tickets(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SUBMIT_SUPPORT_REQUEST)),
):
    items = support_service.list_my_tickets(db, user.id)
    return {"items": items, "count": len(items)}


@router.get("/tickets/inbox", response_model=SupportTicketListResponse)
def list_teacher_support_inbox(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    db_user = db.get(User, user.id)
    if db_user is None or not is_teacher_user(db, db_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher access required")
    items = support_service.list_teacher_inbox(db, user.id)
    return {"items": items, "count": len(items)}


@router.get("/tickets/admin/inbox", response_model=SupportTicketListResponse)
def list_admin_support_inbox(
    db: Session = Depends(get_db),
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_SUPPORT_TICKETS)),
):
    items = support_service.list_admin_inbox(db)
    return {"items": items, "count": len(items)}


@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
def get_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SUBMIT_SUPPORT_REQUEST)),
):
    try:
        return support_service.get_ticket_detail(db, user.id, ticket_id)
    except (SupportTicketNotFoundError, SupportTicketAccessError) as exc:
        raise _http_error(exc) from exc


@router.get("/tickets/{ticket_id}/messages", response_model=list[SupportTicketMessageResponse])
def list_support_ticket_messages(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SUBMIT_SUPPORT_REQUEST)),
):
    try:
        return support_service.list_ticket_messages(db, user.id, ticket_id)
    except (SupportTicketNotFoundError, SupportTicketAccessError) as exc:
        raise _http_error(exc) from exc


@router.post(
    "/tickets/{ticket_id}/messages",
    response_model=SupportTicketMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_support_ticket_message(
    ticket_id: int,
    payload: SupportTicketMessageCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SUBMIT_SUPPORT_REQUEST)),
):
    try:
        return support_service.post_message(
            db,
            user_id=user.id,
            ticket_id=ticket_id,
            body=payload.body,
        )
    except (SupportTicketNotFoundError, SupportTicketAccessError, SupportTicketValidationError) as exc:
        raise _http_error(exc) from exc


@router.patch("/tickets/{ticket_id}", response_model=SupportTicketResponse)
def update_support_ticket(
    ticket_id: int,
    payload: SupportTicketUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SUBMIT_SUPPORT_REQUEST)),
):
    if not payload.status and not payload.escalate:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide status and/or escalate=true.",
        )
    try:
        return support_service.update_ticket(
            db,
            user_id=user.id,
            ticket_id=ticket_id,
            status_raw=payload.status,
            escalate=payload.escalate,
            note=payload.note,
        )
    except (SupportTicketNotFoundError, SupportTicketAccessError, SupportTicketValidationError) as exc:
        raise _http_error(exc) from exc
