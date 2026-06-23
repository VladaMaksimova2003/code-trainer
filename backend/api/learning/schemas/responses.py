"""Learning API — response schemas."""
from datetime import datetime
from pydantic import BaseModel


class GroupResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    created_at: datetime | None = None
    member_count: int = 0


class InvitationCodeResponse(BaseModel):
    id: int
    code: str
    group_id: int
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    is_active: bool


class GroupMemberResponse(BaseModel):
    id: int
    name: str
    email: str | None = None


class GroupCatalogSummaryResponse(BaseModel):
    id: int
    title: str
    description: str = ""
    deadline_at: datetime | None = None
    task_count: int = 0
    visibility: str = "private"


class GroupCatalogProgressResponse(BaseModel):
    student_id: int
    student_name: str
    catalog_id: int
    catalog_title: str
    solved_count: int
    total_tasks: int
    progress_percent: float
    deadline_at: datetime | None = None
    deadline_status: str | None = None


class AssignableCatalogResponse(BaseModel):
    id: int
    title: str
    task_count: int = 0


class StudentCatalogTaskProgressItem(BaseModel):
    task_id: int
    title: str
    task_type: str | None = None
    type: str | None = None
    difficulty: str | None = None
    language: str | None = None
    status: str
    attempts: int = 0
    last_activity_at: datetime | str | None = None


class StudentCatalogTasksProgress(BaseModel):
    catalog_id: int
    catalog_title: str
    catalog_description: str = ""
    deadline_at: datetime | None = None
    tasks: list[StudentCatalogTaskProgressItem] = []


class StudentGroupTeacherResponse(BaseModel):
    id: int
    name: str


class StudentGroupInfoResponse(BaseModel):
    id: int
    name: str


class GroupDeadlineAlertResponse(BaseModel):
    catalog_id: int
    catalog_title: str
    deadline_at: datetime
    level: str
    unsolved_count: int = 0


class StudentJoinedGroupOverviewResponse(BaseModel):
    id: int
    name: str
    teacher: StudentGroupTeacherResponse
    catalog_count: int = 0
    task_count: int = 0
    solved_count: int = 0
    deadline_alert: GroupDeadlineAlertResponse | None = None


class StudentAssignedCatalogSummaryResponse(BaseModel):
    catalog_id: int
    catalog_title: str
    catalog_description: str = ""
    group_id: int
    group_name: str
    teacher_name: str = ""
    deadline_at: datetime | None = None
    solved_count: int = 0
    total_tasks: int = 0


class StudentGroupWorkspaceResponse(BaseModel):
    group: StudentGroupInfoResponse
    teacher: StudentGroupTeacherResponse
    catalogs: list[StudentCatalogTasksProgress] = []


class StudentGroupTaskProgressResponse(BaseModel):
    student_id: int
    student_name: str
    catalogs: list[StudentCatalogTasksProgress] = []


class GroupStudentSummaryResponse(BaseModel):
    student_id: int
    student_name: str
    solved_count: int = 0
    total_tasks: int = 0
    progress_percent: float = 0.0
    last_activity_at: datetime | None = None


class GroupDashboardResponse(BaseModel):
    group: GroupResponse
    members: list[GroupMemberResponse]
    catalogs: list[GroupCatalogSummaryResponse]
    student_catalog_progress: list[GroupCatalogProgressResponse]
    student_summaries: list[GroupStudentSummaryResponse] = []
    assignable_catalogs: list[AssignableCatalogResponse]


class AssignmentSetItemResponse(BaseModel):
    task_id: int
    sort_order: int
    topic: str | None = None


class AssignmentSetResponse(BaseModel):
    id: int
    name: str
    description: str
    teacher_id: int
    visibility: str
    group_id: int | None
    is_archived: bool
    items: list[AssignmentSetItemResponse] = []
    total_tasks: int = 0
    solved_count: int = 0
    created_at: datetime | None = None
    deadline_at: datetime | None = None


class TeacherSearchResultResponse(BaseModel):
    user_id: int
    full_name: str
    bio: str | None
    languages: list[str]
    specialization: str | None
    assignment_count: int
    assignment_set_count: int


class TeacherProfileDetailResponse(TeacherSearchResultResponse):
    public_assignment_sets: list[AssignmentSetResponse] = []


class StudentProgressItemResponse(BaseModel):
    student_id: int
    total_submissions: int
    successful_submissions: int
