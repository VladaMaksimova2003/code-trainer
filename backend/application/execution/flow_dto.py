from pydantic import BaseModel, Field
from typing import Any

_FLOW_TEXT_MAX_LENGTH = 4_000
_FLOW_LIST_MAX_ITEMS = 512


class FlowBlockDTO(BaseModel):
    id: int | str | None = None
    type: str
    text: str | None = Field(default=None, max_length=_FLOW_TEXT_MAX_LENGTH)


class FlowNodeDTO(BaseModel):
    id: int | str | None = None
    type: str
    text: str | None = Field(default=None, max_length=_FLOW_TEXT_MAX_LENGTH)
    position: dict[str, float | int] | None = None


class FlowEdgeDTO(BaseModel):
    id: int | str | None = None
    source: int | str
    target: int | str
    label: str | None = Field(default=None, max_length=128)


class CheckFlowDTO(BaseModel):
    task_id: int
    flow: list[FlowBlockDTO] = Field(max_length=_FLOW_LIST_MAX_ITEMS)
    nodes: list[FlowNodeDTO] | None = Field(default=None, max_length=_FLOW_LIST_MAX_ITEMS)
    edges: list[FlowEdgeDTO] | None = Field(default=None, max_length=_FLOW_LIST_MAX_ITEMS)


class FlowErrorDTO(BaseModel):
    type: str
    text: str = Field(max_length=_FLOW_TEXT_MAX_LENGTH)


class CheckFlowResultDTO(BaseModel):
    success: bool
    errors: list[FlowErrorDTO]
    execution_results: list[dict[str, Any]] = []
    test_cases: list[dict[str, str]] = []
    semantic_checked: bool = False
    execution_job_id: str | None = None
    status: str | None = None
    debug: dict[str, Any] | None = None
