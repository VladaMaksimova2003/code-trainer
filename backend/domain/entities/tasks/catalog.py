from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Task:
    """Pure task aggregate — no catalog reference."""

    id: int
    title: str
    content: str
    topic_id: int | None
    type_id: str
    created_at: datetime
    updated_at: datetime | None = None
    difficulty: str | None = None
    language: str | None = None
    languages: tuple[str, ...] = ()
    chapter_key: str | None = None
    chapter_key: str | None = None
    chapter_title: str | None = None
    chapter_order: int | None = None
    display_order: int | None = None
    primary_action: str | None = None
    activity_label: str | None = None
    task_format: str | None = None
    is_debug_task: bool = False
    action_sort_order: int = 99


@dataclass(frozen=True)
class Catalog:
    id: int
    title: str
    description: str | None
    created_at: datetime
    visibility: str = "public"
    group_id: int | None = None
    deadline_at: datetime | None = None


@dataclass(frozen=True)
class CatalogTaskRelation:
    task_id: int
    catalog_id: int
