"""Admin API — response schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class AdminUserListItemResponse(BaseModel):
    id: int
    name: str
    email: str
    roles: list[str]
    is_blocked: bool
    is_deleted: bool
    created_at: datetime | None = None


class AdminUserDetailResponse(AdminUserListItemResponse):
    total_submissions: int
    successful_submissions: int
    solved_tasks_count: int
    last_login_at: datetime | None = None
    created_tasks_count: int | None = None
    created_catalogs_count: int | None = None
    groups_count: int | None = None
    about: str | None = None
    success_rate: float = 0.0
    streak_days: int = 0
    member_groups_count: int = 0
    member_group_names: list[str] = Field(default_factory=list)


class AdminAssignmentListItemResponse(BaseModel):
    id: int
    title: str
    task_type: str
    difficulty: str
    teacher_id: int | None
    version: int
    workflow_status: str
    is_delete: bool
    collection_title: str | None = None
    chapter_title: str | None = None
    chapter_key: str | None = None
    language: str | None = None
    chapter_slug: str | None = None
    teacher_name: str | None = None
    teacher_email: str | None = None
    teacher_is_deleted: bool = False


class AdminAssignmentVersionResponse(BaseModel):
    id: int
    task_id: int
    version_number: int
    title: str
    is_active: bool
    created_at: datetime | None = None


class RegistrationDayBucketResponse(BaseModel):
    student: int = 0
    teacher: int = 0
    admin: int = 0


class SystemStatisticsResponse(BaseModel):
    users_total: int
    users_by_role: dict[str, int]
    assignments_total: int
    curriculum_catalog_tasks: int = 0
    assignments_by_status: dict[str, int]
    submissions_total: int
    submissions_successful: int
    solved_assignments_count: int
    teacher_requests_pending: int
    registrations_by_period: dict[str, list[RegistrationDayBucketResponse]] = Field(
        default_factory=dict
    )
    users_new_last_month: int = 0
    users_new_last_month_by_role: dict[str, int] = Field(default_factory=dict)
    tasks_new_last_30_days: int = 0
