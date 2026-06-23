"""GET /languages — returns all supported programming languages."""
from fastapi import APIRouter
from pydantic import BaseModel

from infrastructure.execution.language_registry import language_registry

router = APIRouter()

_HIDDEN_LANGUAGE_IDS = frozenset({"javascript"})


class LanguageResponse(BaseModel):
    id: str
    label: str
    file_extension: str
    monaco_language: str
    supported_features: list[str]


@router.get("/", response_model=list[LanguageResponse])
def list_languages() -> list[LanguageResponse]:
    """Return all languages available for task creation and execution."""
    return [
        LanguageResponse(**cfg.to_dict())
        for cfg in language_registry.all()
        if cfg.id not in _HIDDEN_LANGUAGE_IDS
    ]
