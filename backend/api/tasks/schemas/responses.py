"""Task API — response schemas."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Any


class AssignmentCreatedResponse(BaseModel):
    task_id: int
    assignment_type: str
    type: str
    languages: list[str] | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    type: str
    solution_description: str | None = None
    algorithm_hint: str | None = None
    constructions: list[Any] = []
    code_examples: Any = None
    test_cases: Any = None
    blocks: list[Any] = []
    language: str | None = None
    template: str | None = None
    task_type: str | None = None
    attempted: bool = False
    solved: bool = False
    submissions_count: int = 0


class TaskOverviewItem(BaseModel):
    """Lightweight task row for student list — no starter/tests/blocks payload."""

    id: int
    slot_id: str | None = None
    pedagogical_slot_id: str | None = None
    concept_id: str | None = None
    title: str
    language: str | None = None
    target_language: str | None = None
    course_key: str | None = None
    chapter_key: str | None = None
    available_language_tracks: list[str] = Field(default_factory=list)
    language_track_states: dict[str, str] = Field(default_factory=dict)
    task_format: str | None = None
    difficulty: str | None = None
    type: str | None = None
    task_type: str | None = None
    constructions: list[str] = Field(default_factory=list)
    attempted: bool = False
    solved: bool = False
    completed: bool = False
    submissions_count: int = 0


class TaskOverviewResponse(BaseModel):
    tasks: list[TaskOverviewItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 0


class TaskCurriculumNavigationResponse(BaseModel):
    collection_id: str | None = None
    collection_title_ru: str | None = None
    return_path: str | None = None
    task_index: int | None = None
    total_tasks: int | None = None
    task_ids: list[int] = Field(default_factory=list)
    prev_task_id: int | None = None
    next_task_id: int | None = None
    next_collection_id: str | None = None
    next_collection_title_ru: str | None = None
    course_completed: bool | None = None


class TaskCurriculumDisplayResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    language: str | None = None
    language_label: str | None = None
    theme_name_ru: str | None = None
    subtopic_name_ru: str | None = None
    technical_concept_id: str | None = None
    action: str | None = None
    action_label: str | None = None
    action_skill_label: str | None = None
    action_description_ru: str | None = None
    context_line_ru: str | None = None
    instruction_ru: str | None = None
    slot_id: str | None = None
    flowchart_mode: str | None = None
    navigation: TaskCurriculumNavigationResponse | None = None


class LanguageVariantResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    language: str | None = None
    blocks: list[Any] = Field(default_factory=list)
    template: str | None = None


class PublicTaskDetailResponse(BaseModel):
    """GET /tasks/{task_id} — full public task payload (type-specific fields optional)."""

    model_config = ConfigDict(extra="allow")

    id: int
    title: str | None = None
    description: str | None = None
    difficulty: str | None = None
    type: str | None = None
    task_type: str | None = None
    solution_description: str | None = None
    algorithm_hint: str | None = None
    constructions: list[str] = Field(default_factory=list)
    required_structures: list[str] = Field(default_factory=list)
    construction_hints: dict[str, Any] = Field(default_factory=dict)
    hints: list[str] = Field(default_factory=list)
    post_solve_explanation: str | None = None
    test_cases: list[dict[str, Any]] = Field(default_factory=list)
    code_examples: dict[str, Any] = Field(default_factory=dict)
    source_code: str | None = None
    source_language: str | None = None
    flow_spec: dict[str, Any] = Field(default_factory=dict)
    diagram: dict[str, Any] = Field(default_factory=dict)
    topic_id: int | None = None
    blocks: list[Any] = Field(default_factory=list)
    language: str | None = None
    template: str | None = None
    language_variants: dict[str, LanguageVariantResponse | dict[str, Any]] | list[LanguageVariantResponse | dict[str, Any]] = Field(
        default_factory=dict
    )
    curriculum: TaskCurriculumDisplayResponse | dict[str, Any] | None = None
    attempted: bool = False
    solved: bool = False
    submissions_count: int = 0
    primary_action: str | None = None
    target_language: str | None = None
    primary_technical_concept_id: str | None = None
    detected_technical_concepts: list[Any] = Field(default_factory=list)
    expected_concept_ids: list[str] = Field(default_factory=list)
    expected_concepts: list[dict[str, Any]] = Field(default_factory=list)
    concept_hierarchy: list[Any] = Field(default_factory=list)
    transfer_hints_by_language: dict[str, Any] = Field(default_factory=dict)
    technical_concepts: list[Any] = Field(default_factory=list)


class DetectedPatternResponse(BaseModel):
    id: str
    type: str
    label: str
    confidence: float = 1.0
    source_construct: str


class AnalyzeCodeResponse(BaseModel):
    patterns: list[DetectedPatternResponse]
    raw_constructs: list[str]
    semantic_ir: dict[str, Any] | None = None


class PatternCatalogItem(BaseModel):
    id: str
    type: str
    label: str
    description: str | None = None
    card: dict[str, Any] | None = None


class PatternCatalogResponse(BaseModel):
    patterns: list[PatternCatalogItem]
    source: str = "tc_display_registry.json"
    total: int = 0


class DetectedExpectedConceptItem(BaseModel):
    id: str
    label: str


class DetectExpectedConceptsResponse(BaseModel):
    by_language: dict[str, list[DetectedExpectedConceptItem]]
    suggested_ids: list[str]


class ScannedExpectedConceptItem(BaseModel):
    id: str
    label: str
    detected: bool
    reason: str | None = None


class ScanExpectedConceptsResponse(BaseModel):
    items: list[ScannedExpectedConceptItem]
    detected_ids: list[str]
