"""Task API — request schemas."""
from pydantic import BaseModel, Field
from typing import Any

from shared.config import get_settings

CODE_MAX_LENGTH = get_settings().security.code_max_length
FLOW_LIST_MAX_ITEMS = 512


class CreateAssignmentRequest(BaseModel):
    assignment_type: str
    difficulty: str = "easy"
    languages: list[str] = Field(default_factory=list)
    title: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict)
    patterns: list[str] | None = None
    test_cases: list[dict] | None = None


class BlockReorderCreateRequest(BaseModel):
    title: str
    description: str
    difficulty: str = "easy"
    original_code: str = Field(min_length=1, max_length=CODE_MAX_LENGTH)
    template: str | None = Field(default=None, max_length=CODE_MAX_LENGTH)
    language: str = "python"
    language_variants: dict | None = None
    teacher_id: int | None = None
    blocks: list[str] | None = Field(default=None, max_length=FLOW_LIST_MAX_ITEMS)
    correct_order: list[int] | None = Field(default=None, max_length=FLOW_LIST_MAX_ITEMS)
    test_cases: list[dict] = Field(default_factory=list, max_length=FLOW_LIST_MAX_ITEMS)
    patterns: list[str] | None = Field(default=None, max_length=FLOW_LIST_MAX_ITEMS)
    patterns_by_language: dict[str, list[str]] | None = None
    task_type: str | None = None


class BlockReorderSolutionRequest(BaseModel):
    order: list[int] = Field(default_factory=list, max_length=FLOW_LIST_MAX_ITEMS)
    language: str | None = None
    indents: list[int] | None = Field(default=None, max_length=FLOW_LIST_MAX_ITEMS)
    assembled_code: str | None = Field(default=None, max_length=CODE_MAX_LENGTH)


class AnalyzeCodeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=CODE_MAX_LENGTH)
    language: str = "python"


class CodeSampleRequest(BaseModel):
    language: str = Field(min_length=1, max_length=32)
    code: str = Field(min_length=1, max_length=CODE_MAX_LENGTH)


class DetectExpectedConceptsRequest(BaseModel):
    samples: list[CodeSampleRequest] = Field(min_length=1, max_length=16)


class ScanExpectedConceptsRequest(BaseModel):
    code: str = Field(min_length=0, max_length=CODE_MAX_LENGTH)
    language: str = Field(min_length=1, max_length=32)
    concept_ids: list[str] | None = Field(default=None, max_length=64)
