from pydantic import BaseModel, Field

from shared.config import get_settings

CODE_MAX_LENGTH = get_settings().security.code_max_length


class SolutionSubmitRequest(BaseModel):
    task_id: int
    code: str = Field(min_length=1, max_length=CODE_MAX_LENGTH)
    language: str
    session_id: str | None = None


class SubmissionQueuedResponse(BaseModel):
    submission_id: int
    status: str
    message: str = "Submission queued"


class JobQueuedResponse(BaseModel):
    job_id: str
    status: str
    deduplicated: bool = False


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    language: str | None = None
    op: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    result: dict | None = None


class JobResultResponse(BaseModel):
    job_id: str
    status: str
    output: dict | None = None
    errors: str | None = None
