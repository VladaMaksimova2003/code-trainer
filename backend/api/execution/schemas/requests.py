"""Execution API — request schemas."""
from pydantic import BaseModel, Field

from shared.config import get_settings

CODE_MAX_LENGTH = get_settings().security.code_max_length


class SubmissionCreateRequest(BaseModel):
    task_id: int
    language: str
    code: str = Field(min_length=1, max_length=CODE_MAX_LENGTH)


class LintCreateRequest(BaseModel):
    task_id: int
    language: str
    code: str = Field(min_length=1, max_length=CODE_MAX_LENGTH)
    session_id: str | None = None
