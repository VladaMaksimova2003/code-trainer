"""Learning API — request schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class GenerateInvitationRequest(BaseModel):
    max_uses: int | None = None
    expires_in_days: int | None = 30


class JoinGroupRequest(BaseModel):
    code: str = Field(min_length=4, max_length=32)


class AssignCatalogToGroupRequest(BaseModel):
    catalog_id: int
    deadline_at: datetime | None = None


class CreateAssignmentSetRequest(BaseModel):
    name: str
    description: str = ""
    visibility: str = Field(description="public | private")
    group_id: int | None = None


class UpdateAssignmentSetRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    visibility: str | None = None
    group_id: int | None = None
    is_archived: bool | None = None


class AddAssignmentSetItemRequest(BaseModel):
    task_id: int
    sort_order: int = 0
    topic: str | None = None
