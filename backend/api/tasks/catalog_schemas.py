from datetime import datetime

from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    id: int
    title: str
    content: str
    topic_id: int | None = None
    type_id: str
    created_at: datetime
    updated_at: datetime | None = None
    difficulty: str | None = None
    language: str | None = None
    languages: list[str] = Field(default_factory=list)
    catalog_ids: list[int] = Field(default_factory=list)
    is_assigned: bool = False
    chapter_key: str | None = None
    chapter_title: str | None = None
    chapter_order: int | None = None
    display_order: int | None = None
    primary_action: str | None = None
    activity_label: str | None = None
    task_format: str | None = None
    is_debug_task: bool = False
    action_sort_order: int = 99


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = ""
    topic_id: int | None = None
    type_id: str = Field(min_length=1, max_length=32)


class CatalogResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    created_at: datetime
    task_count: int = 0
    visibility: str = "public"
    group_id: int | None = None
    deadline_at: datetime | None = None


class CreateCatalogRequest(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    description: str | None = None
    visibility: str = Field(default="public", description="public | private")
    group_id: int | None = None
    deadline_at: datetime | None = None


class UpdateCatalogRequest(BaseModel):
    group_id: int | None = None
    deadline_at: datetime | None = None
    visibility: str | None = None


class AssignTaskRequest(BaseModel):
    task_id: int


class AssignTaskChapterRequest(BaseModel):
    language: str = Field(min_length=1, max_length=32)
    chapter_key: str = Field(min_length=1, max_length=128)


class AssignTaskChapterResponse(BaseModel):
    task_id: int
    language: str
    chapter_key: str
    chapter_title: str


class ChapterTaskOrderRequest(BaseModel):
    chapter_key: str = Field(min_length=1, max_length=128)
    task_ids: list[int] = Field(min_length=1, max_length=512)


class CollectionChapterOrderRequest(BaseModel):
    chapter_keys: list[str] = Field(min_length=1, max_length=128)


class ChapterResponse(BaseModel):
    language: str
    chapter_key: str
    title: str
    description: str = ""
    sort_order: int = 0
    is_custom: bool = False
    task_count: int = 0
    registry_title: str | None = None
    updated_at: datetime | None = None


class CreateChapterRequest(BaseModel):
    language: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class UpdateChapterRequest(BaseModel):
    language: str = Field(default="", max_length=32)
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class CollectionMetaResponse(BaseModel):
    language: str
    title: str
    description: str = ""
    registry_title: str | None = None
    updated_at: datetime | None = None


class UpdateCollectionMetaRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class PlatformCourseMetaResponse(BaseModel):
    title: str
    description: str = ""
    registry_title: str | None = None
    updated_at: datetime | None = None
    author_user_id: int | None = None
    author_name: str | None = None


class UpdatePlatformCourseMetaRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class TeacherCourseResponse(BaseModel):
    id: int
    title: str
    description: str
    is_default: bool
    task_count: int
    created_at: str
    updated_at: datetime | None = None


class CreateTeacherCourseRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class UpdateTeacherCourseRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class AssignCourseToCatalogRequest(BaseModel):
    course_id: int


class TaskRetireResponse(BaseModel):
    action: str
    task_id: int
    submissions_count: int = 0


class UpdateTaskWorkflowRequest(BaseModel):
    status: str = Field(min_length=1, max_length=32)


class CreateTaskInCatalogRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = ""
    topic_id: int | None = None
    type_id: str = Field(min_length=1, max_length=32)
