"""Analytics API response schemas (OpenAPI typing only)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyticsOverviewResponse(BaseModel):
    total_tasks: int = 0
    solved_count: int = 0
    completion_percent: float = 0.0
    level: str | None = None
    success_rate: float = 0.0
    total_submissions: int = 0


class AnalyticsLanguageRowResponse(BaseModel):
    language: str
    solved: int = 0
    total: int = 0
    percent: float = 0.0


class AnalyticsStructureRowResponse(BaseModel):
    id: str
    label: str
    hint: str | None = None
    concepts: list[str] = Field(default_factory=list)
    total: int = 0
    solved: int = 0
    percent: float = 0.0


class DisplayTcSkillRowResponse(BaseModel):
    id: str
    label: str
    description: str = ""
    total: int = 0
    solved: int = 0
    percent: float = 0.0


class TcSkillLanguageOptionResponse(BaseModel):
    code: str
    label: str = ""


class TcTaskRecommendationResponse(BaseModel):
    task_id: int
    title: str
    language: str = ""
    difficulty: str = "medium"
    reason: str = ""
    weak_tc_ids: list[str] = Field(default_factory=list)
    weak_tc_labels: list[str] = Field(default_factory=list)
    score: float = 0.0


class AnalyticsActivityRowResponse(BaseModel):
    submission_id: int
    task_id: int
    task_title: str
    success: bool | None = None
    status: str | None = None
    language: str | None = None
    created_at: str | None = None


class AnalyticsPerTaskRowResponse(BaseModel):
    task_id: int
    title: str
    task_type: str | None = None
    attempts: int = 0
    success_rate: float = 0.0
    solved: bool = False


class AnalyticsTaskTypeRowResponse(BaseModel):
    task_type: str
    attempts: int = 0
    success_rate: float = 0.0


class AnalyticsErrorCountsResponse(BaseModel):
    syntax: int = 0
    logic: int = 0
    runtime: int = 0


class AnalyticsErrorBreakdownResponse(BaseModel):
    counts: AnalyticsErrorCountsResponse
    percent: dict[str, float] = Field(default_factory=dict)
    total_failed: int = 0


class StudentRecommendationStreakResponse(BaseModel):
    days: int = 0
    message: str = ""


class StudentRecommendationWeakTopicResponse(BaseModel):
    name: str
    progress: float = 0.0
    recommendation: str = ""


class StudentRecommendationsResponse(BaseModel):
    streak: StudentRecommendationStreakResponse
    weak_topics: list[StudentRecommendationWeakTopicResponse] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class LegacyRecommendationItemResponse(BaseModel):
    kind: str
    message: str
    id: str
    detail: str | None = None


class StudentAnalyticsResponse(BaseModel):
    overview: AnalyticsOverviewResponse
    by_language: list[AnalyticsLanguageRowResponse] = Field(default_factory=list)
    by_structure: list[AnalyticsStructureRowResponse] = Field(default_factory=list)
    tc_skills: list[DisplayTcSkillRowResponse] = Field(default_factory=list)
    tc_skills_by_language: dict[str, list[DisplayTcSkillRowResponse]] = Field(
        default_factory=dict
    )
    tc_skill_groups: list[DisplayTcSkillRowResponse] = Field(default_factory=list)
    tc_skill_groups_by_language: dict[str, list[DisplayTcSkillRowResponse]] = Field(
        default_factory=dict
    )
    tc_skill_languages: list[TcSkillLanguageOptionResponse] = Field(default_factory=list)
    tc_skills_default_language: str = ""
    tc_task_recommendations: list[TcTaskRecommendationResponse] = Field(default_factory=list)
    tc_task_recommendations_by_language: dict[str, list[TcTaskRecommendationResponse]] = Field(
        default_factory=dict
    )
    recent_activity: list[AnalyticsActivityRowResponse] = Field(default_factory=list)
    per_task: list[AnalyticsPerTaskRowResponse] = Field(default_factory=list)
    by_task_type: list[AnalyticsTaskTypeRowResponse] = Field(default_factory=list)
    error_breakdown: AnalyticsErrorBreakdownResponse
    student_recommendations: StudentRecommendationsResponse
    recommendations: list[LegacyRecommendationItemResponse] = Field(default_factory=list)
    streak_days: int = 0
    assumptions: list[str] = Field(default_factory=list)


class TeacherAnalyticsSummaryResponse(BaseModel):
    student_count: int = 0
    students_active_last_7: int = 0
    students_weekly_delta: int = 0
    active_tasks: int = 0
    avg_success_rate: float = 0.0
    avg_success_rate_delta_month: float = 0.0


class TeacherAnalyticsAssignmentRowResponse(BaseModel):
    task_id: int
    title: str
    difficulty: str | None = None
    task_type: str | None = None
    success_percent: float = 0.0
    avg_attempts: float = 0.0
    student_count: int = 0
    total_submissions: int = 0
    error_breakdown: AnalyticsErrorBreakdownResponse


class TeacherAnalyticsTaskTypeRowResponse(BaseModel):
    task_type: str
    submissions: int = 0
    success_rate: float = 0.0


class TeacherAnalyticsGroupRowResponse(BaseModel):
    group_id: int
    name: str
    member_count: int = 0
    avg_progress_percent: float = 0.0
    weak_topics: list[str] = Field(default_factory=list)


class TeacherAnalyticsStudentRowResponse(BaseModel):
    student_id: int
    name: str
    progress_percent: float = 0.0
    solved_count: int = 0
    submissions_count: int = 0
    weak_topics: list[str] = Field(default_factory=list)
    last_activity_at: str | None = None


class TeacherAnalyticsResponse(BaseModel):
    summary: TeacherAnalyticsSummaryResponse
    submissions_by_date: dict[str, int] = Field(default_factory=dict)
    per_assignment: list[TeacherAnalyticsAssignmentRowResponse] = Field(default_factory=list)
    task_type_success: list[TeacherAnalyticsTaskTypeRowResponse] = Field(default_factory=list)
    groups: list[TeacherAnalyticsGroupRowResponse] = Field(default_factory=list)
    students: list[TeacherAnalyticsStudentRowResponse] = Field(default_factory=list)
    error_breakdown_overall: AnalyticsErrorBreakdownResponse
    assumptions: list[str] = Field(default_factory=list)


class TeacherSubmissionListItemResponse(BaseModel):
    id: int
    task_id: int
    task_title: str
    task_type: str | None = None
    student_id: int | None = None
    student_name: str | None = None
    language: str | None = None
    status: str | None = None
    success: bool | None = None
    created_at: str | None = None
    catalog_id: int | None = None
    catalog_title: str | None = None
    is_late: bool | None = None


class TeacherSubmissionsListResponse(BaseModel):
    items: list[TeacherSubmissionListItemResponse] = Field(default_factory=list)
    count: int = 0


class TeacherSubmissionDetailResponse(BaseModel):
    id: int
    task_id: int
    task_title: str
    student_id: int | None = None
    student_name: str | None = None
    language: str | None = None
    code: str | None = None
    status: str | None = None
    success: bool | None = None
    created_at: str | None = None
