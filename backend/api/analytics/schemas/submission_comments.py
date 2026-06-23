from pydantic import BaseModel, Field


class SubmissionCommentCreateRequest(BaseModel):
    body: str = Field(..., min_length=1, max_length=4096)


class SubmissionCommentUpdateRequest(BaseModel):
    body: str = Field(..., min_length=1, max_length=4096)


class SubmissionCommentResponse(BaseModel):
    id: int
    submission_id: int
    teacher_id: int
    teacher_name: str | None
    body: str
    created_at: str | None
    updated_at: str | None


class SubmissionCommentListResponse(BaseModel):
    items: list[SubmissionCommentResponse]
    count: int
