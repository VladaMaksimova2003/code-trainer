"""Curriculum v2 API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LearningConceptResponse(BaseModel):
    id: str
    name_ru: str
    tier: str
    order: int
    description_ru: str = ""


class TechnicalConceptSummaryResponse(BaseModel):
    id: str
    name_ru: str
    tier: str
    learning_concept_id: str
    notes: str = ""
    optional_in_track: bool = False


class ExercisePatternResponse(BaseModel):
    id: str
    action: str
    description_ru: str = ""
    grading: str = ""
    legacy_adapter: str | None = None
    source: dict | None = None
    target: dict | None = None
    transfer: dict | None = None


class ActionMaskResponse(BaseModel):
    technical_concept_id: str
    required_actions: list[str]
    optional_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    active_actions: list[str]
    required_patterns_by_action: dict[str, list[str]] = Field(default_factory=dict)
    optional_patterns_by_action: dict[str, list[str]] = Field(default_factory=dict)
    disabled_patterns_by_action: dict[str, list[str]] = Field(default_factory=dict)


class CurriculumSummaryResponse(BaseModel):
    language: str
    version: int
    target_language: str
    learning_concepts_count: int
    technical_concepts_count: int
    exercise_patterns_count: int
    mastery_rules_version: int
    review_rules_version: int
    learning_path_default_sequence: list[str] = Field(default_factory=list)


class TechnicalConceptInChapterResponse(BaseModel):
    id: str
    name_ru: str
    tier: str
    optional_in_track: bool = False
    required_actions: list[str]
    optional_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    active_actions: list[str]
    required_patterns_by_action: dict[str, list[str]] = Field(default_factory=dict)


class LearningConceptDetailResponse(BaseModel):
    learning_concept: LearningConceptResponse
    prerequisites: list[str] = Field(default_factory=list)
    study_order_tc: list[str] = Field(default_factory=list)
    technical_concepts: list[TechnicalConceptInChapterResponse] = Field(default_factory=list)


class CurriculumValidationResponse(BaseModel):
    language: str
    valid: bool
    errors: list[str] = Field(default_factory=list)
    stats: dict = Field(default_factory=dict)


class TechnicalConceptPatternsResponse(BaseModel):
    technical_concept_id: str
    action_mask: ActionMaskResponse
    patterns: list[ExercisePatternResponse] = Field(default_factory=list)
    patterns_by_action: dict[str, list[ExercisePatternResponse]] = Field(default_factory=dict)
