"""Admin API — request schemas."""
from pydantic import BaseModel, Field


class SetUserBlockedRequest(BaseModel):
    blocked: bool


class AssignRoleRequest(BaseModel):
    role: str = Field(description="student | teacher | admin")


class SetAssignmentWorkflowRequest(BaseModel):
    status: str = Field(description="active | under_review | archived")
