from pydantic import BaseModel, Field

from shared.config import get_settings

CODE_MAX_LENGTH = get_settings().security.code_max_length


class GuestCheckRequest(BaseModel):
    task_id: int
    language: str
    code: str = Field(min_length=1, max_length=CODE_MAX_LENGTH)


class GuestCheckQueuedResponse(BaseModel):
    job_id: str
    status: str


class GuestCheckResultResponse(BaseModel):
    job_id: str
    status: str
    success: bool | None = None
    compiler_errors: list[dict] = []
    linter_errors: list[dict] = []
    pattern_errors: list[dict] = []
    test_results: list[dict] = []
    errors: str | None = None
