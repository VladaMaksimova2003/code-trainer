"""Language id validation against the runtime registry."""
from __future__ import annotations

LanguageId = str


def parse_language(value: str | LanguageId) -> str:
    """Validate language id against YAML-loaded registry."""
    from infrastructure.execution.language_registry import language_registry

    lang_id = str(value).strip().lower()
    language_registry.get_or_raise(lang_id)
    return lang_id


def is_valid_language(value: str | None) -> bool:
    if not value:
        return False
    from infrastructure.execution.language_registry import language_registry

    return language_registry.get(str(value).lower()) is not None
