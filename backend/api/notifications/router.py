from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_user
from api.notifications.schemas import MarkAllReadResponse, NotificationListResponse, NotificationResponse
from application.auth.dto import CurrentUserResult
from application.support import notifications_service
from infrastructure.db.session import get_db

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(get_current_user),
):
    rows = notifications_service.list_notifications(db, user.id, unread_only=unread_only)
    unread = notifications_service.unread_count(db, user.id)
    items = [notifications_service.serialize_notification(row) for row in rows]
    return {"items": items, "count": len(items), "unread_count": unread}


@router.get("/unread-count")
def get_unread_notification_count(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(get_current_user),
):
    return {"unread_count": notifications_service.unread_count(db, user.id)}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(get_current_user),
):
    row = notifications_service.mark_read(db, user.id, notification_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notifications_service.serialize_notification(row)


@router.post("/read-all", response_model=MarkAllReadResponse)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(get_current_user),
):
    updated = notifications_service.mark_all_read(db, user.id)
    return {"updated": updated}
