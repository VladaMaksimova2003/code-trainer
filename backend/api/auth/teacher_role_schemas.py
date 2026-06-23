from datetime import datetime

from pydantic import BaseModel


class TeacherRoleRequestCreate(BaseModel):
    message: str | None = None


class TeacherRoleRequestResponse(BaseModel):
    id: int
    user_id: int
    user_name: str | None = None
    user_email: str | None = None
    status: str
    message: str | None = None
    created_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewed_by_id: int | None = None
