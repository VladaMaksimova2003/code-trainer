"""Student-facing curriculum API response schemas (OpenAPI typing only)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CurriculumProgressSummary(BaseModel):
    total_tasks: int = 0
    passed_tasks: int = 0
    progress_percent: float = 0.0
    catalog_tasks: int | None = None


class CurriculumNextTaskRef(BaseModel):
    task_id: int
    slug: str | None = None
    title: str | None = None
    task_type: str | None = None
    technical_concept_id: str | None = None
    action: str | None = None
    progress_status: str | None = None


class CurriculumCollectionRef(BaseModel):
    collection_id: str
    language: str | None = None
    chapter_key: str | None = None
    learning_concept_id: str | None = None
    title_ru: str | None = None
    route_path: str | None = None


class CurriculumGlobalNextResponse(BaseModel):
    next_task: CurriculumNextTaskRef | None = None
    collection: CurriculumCollectionRef | None = None
    completed: bool = False
    button_label: str | None = None
    progress: CurriculumProgressSummary


class CurriculumCollectionSummary(BaseModel):
    collection_id: str
    language: str
    chapter_key: str
    learning_concept_id: str
    title_ru: str
    description_ru: str | None = None
    route_path: str
    progress: CurriculumProgressSummary
    completed: bool = False
    button_label: str | None = None
    next_task: CurriculumNextTaskRef | None = None


class CurriculumLanguageBlockResponse(BaseModel):
    language: str
    language_label: str | None = None
    track_description_ru: str | None = None
    available: bool = False
    progress: CurriculumProgressSummary
    collections: list[CurriculumCollectionSummary] = Field(default_factory=list)


class PlatformCourseSummaryResponse(BaseModel):
    title: str
    description: str = ""
    author_user_id: int | None = None
    author_name: str | None = None


class CurriculumCollectionsViewResponse(BaseModel):
    languages: list[CurriculumLanguageBlockResponse] = Field(default_factory=list)
    collections: list[CurriculumCollectionSummary] = Field(default_factory=list)
    platform_course: PlatformCourseSummaryResponse | None = None


class CurriculumCollectionNavigationResponse(BaseModel):
    collection_id: str
    collection_title_ru: str | None = None
    return_path: str | None = None
    task_index: int
    total_tasks: int
    task_ids: list[int] = Field(default_factory=list)
    prev_task_id: int | None = None
    next_task_id: int | None = None
    next_collection_id: str | None = None
    next_collection_title_ru: str | None = None
    course_completed: bool = False


class PascalShowcaseNextResponse(BaseModel):
    collection_id: str
    collection_key: str | None = None
    language: str | None = None
    learning_concept_id: str | None = None
    title_ru: str | None = None
    next_task: CurriculumNextTaskRef | None = None
    completed: bool = False
    button_label: str | None = None
    progress: CurriculumProgressSummary


class PascalShowcaseTaskCard(BaseModel):
    task_id: int
    slug: str | None = None
    title: str | None = None
    task_type: str | None = None
    difficulty: str | None = None
    technical_concept_name_ru: str | None = None
    subtopic_name_ru: str | None = None
    action: str | None = None
    action_label: str | None = None
    action_skill_label: str | None = None
    action_description_ru: str | None = None
    short_instruction: str | None = None
    progress_status: str | None = None


class PascalShowcaseSectionProgress(BaseModel):
    total_tasks: int | None = None
    passed_tasks: int | None = None
    progress_percent: float | None = None


class PascalShowcaseSectionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name_ru: str | None = None
    tasks: list[PascalShowcaseTaskCard] = Field(default_factory=list)
    progress: PascalShowcaseSectionProgress | dict[str, Any] | None = None


class LearningConceptBrief(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name_ru: str | None = None
    description_ru: str | None = None
    tier: str | None = None
    order: int | None = None


class PascalShowcaseActionLabel(BaseModel):
    badge: str | None = None
    skill: str | None = None
    description_ru: str | None = None


class PascalShowcaseStudentViewResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    language: str
    collection_key: str | None = None
    collection_id: str | None = None
    title_ru: str | None = None
    description_ru: str | None = None
    learning_concept: LearningConceptBrief | dict[str, Any] | None = None
    theme: LearningConceptBrief | dict[str, Any] | None = None
    study_order_tc: list[str] | None = None
    subtopics: list[PascalShowcaseSectionResponse] = Field(default_factory=list)
    technical_concepts: list[PascalShowcaseSectionResponse] = Field(default_factory=list)
    total_tasks: int = 0
    progress: CurriculumProgressSummary | None = None
    labels: dict[str, Any] | None = None


class PascalShowcaseTaskListItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    task_id: int
    slug: str | None = None
    title: str | None = None
    task_type: str | None = None
    difficulty: str | None = None
    technical_concept_id: str | None = None
    action: str | None = None
    collection_key: str | None = None


class PascalShowcaseTasksListResponse(BaseModel):
    collection_key: str | None = None
    learning_concept_id: str
    language: str
    tasks: list[PascalShowcaseTaskListItem] = Field(default_factory=list)
