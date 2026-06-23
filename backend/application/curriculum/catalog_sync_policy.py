"""Control whether curriculum task bodies are loaded from catalog files or DB only."""

from __future__ import annotations

from shared.config import get_settings


def is_catalog_sync_enabled() -> bool:
    """When False, task content is served and stored only from DB (teacher edits)."""
    return bool(get_settings().curriculum.catalog_sync_enabled)


def catalog_sync_disabled_message() -> str:
    return (
        "Catalog sync is disabled (CURRICULUM__CATALOG_SYNC_ENABLED=false). "
        "Task content is DB-only; seed/sync scripts will not overwrite or create from files. "
        "Pass --force-catalog-sync to override."
    )
