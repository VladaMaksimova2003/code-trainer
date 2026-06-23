"""Runtime language registry — populated by language_loader from YAML files."""

from __future__ import annotations

from typing import Iterator

from domain.entities.language import LanguageConfig


class LanguageRegistry:
    def __init__(self) -> None:
        self._store: dict[str, LanguageConfig] = {}

    def clear(self) -> None:
        self._store.clear()

    def register(self, config: LanguageConfig) -> None:
        self._store[config.id] = config

    def get(self, language_id: str) -> LanguageConfig | None:
        self._ensure_loaded()
        return self._store.get(str(language_id).lower())

    def get_or_raise(self, language_id: str) -> LanguageConfig:
        self._ensure_loaded()
        cfg = self._store.get(str(language_id).lower())
        if cfg is None:
            raise ValueError(
                f"Language '{language_id}' is not registered. "
                f"Available: {', '.join(sorted(self._store))}"
            )
        return cfg

    def all(self) -> list[LanguageConfig]:
        self._ensure_loaded()
        return list(self._store.values())

    def ids(self) -> list[str]:
        self._ensure_loaded()
        return list(self._store.keys())

    def __iter__(self) -> Iterator[LanguageConfig]:
        self._ensure_loaded()
        return iter(self._store.values())

    def __contains__(self, language_id: str) -> bool:
        self._ensure_loaded()
        return str(language_id).lower() in self._store

    @staticmethod
    def _ensure_loaded() -> None:
        if language_registry._store:
            return
        from infrastructure.execution.language_loader import load_languages

        load_languages()


language_registry = LanguageRegistry()
