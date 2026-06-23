from pydantic import BaseModel, Field


class SupportTicketCreateRequest(BaseModel):
    category: str = Field(
        ...,
        description="task_content | autograder | technical | account | other",
    )
    body: str = Field(..., min_length=1, max_length=8192)
    subject: str | None = Field(default=None, max_length=255)
    task_id: int | None = None
    submission_id: int | None = None
    context: dict | None = None


class SupportTicketMessageCreateRequest(BaseModel):
    body: str = Field(..., min_length=1, max_length=8192)


class SupportTicketUpdateRequest(BaseModel):
    status: str | None = Field(
        default=None,
        description="open | in_progress | resolved | closed",
    )
    escalate: bool = False
    note: str | None = Field(default=None, max_length=512)


class SupportTicketMessageResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int | None
    author_name: str | None
    body: str
    message_type: str
    created_at: str | None


class SupportTicketResponse(BaseModel):
    id: int
    author_id: int
    author_name: str | None
    category: str
    subject: str
    status: str
    target: str
    assignee_id: int | None
    assignee_name: str | None
    task_id: int | None
    task_title: str | None
    submission_id: int | None
    context: dict
    escalated_at: str | None
    created_at: str | None
    updated_at: str | None
    resolved_at: str | None
    messages: list[SupportTicketMessageResponse] | None = None


class SupportTicketListResponse(BaseModel):
    items: list[SupportTicketResponse]
    count: int


class SupportTemplateChipResponse(BaseModel):
    id: str
    label: str
    draft: str


class SupportTemplateCategoryResponse(BaseModel):
    id: str
    label: str
    templates: list[SupportTemplateChipResponse]


class SupportTemplatesResponse(BaseModel):
    context: str
    role: str
    categories: list[SupportTemplateCategoryResponse]
