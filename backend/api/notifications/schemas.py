from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    kind: str
    title: str
    body: str
    ticket_id: int | None
    task_id: int | None = None
    submission_id: int | None = None
    is_read: bool
    created_at: str | None


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    count: int
    unread_count: int


class MarkAllReadResponse(BaseModel):
    updated: int
