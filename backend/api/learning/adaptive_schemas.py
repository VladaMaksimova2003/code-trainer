from __future__ import annotations

from pydantic import BaseModel, Field


class AdaptiveCheckRequest(BaseModel):
    code: str
    language: str
    required: list[str | dict] = Field(default_factory=list)


class StructureProfileResponse(BaseModel):
    loop: bool = False
    function: bool = False
    call: bool = False
    condition: bool = False
    return_: bool = Field(False, alias="return")
    assignment: bool = False

    model_config = {"populate_by_name": True}
