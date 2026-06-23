from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from domain.entities.learning.recommendation import Skill, TaskType, Topic

_METADATA_PATH = (
    Path(__file__).resolve().parents[3] / "resources" / "recommendation_metadata.json"
)


def _load_raw() -> dict[str, Any]:
    try:
        with _METADATA_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {"topics": [], "skills": [], "task_types": [], "skill_to_topic": {}}


@lru_cache(maxsize=1)
def load_topics() -> dict[int, Topic]:
    raw = _load_raw()
    return {
        item["id"]: Topic(
            id=item["id"],
            name=item["name"],
            prerequisites=tuple(item.get("prerequisites") or []),
            skills=tuple(item.get("skills") or []),
        )
        for item in raw.get("topics") or []
    }


@lru_cache(maxsize=1)
def load_skills() -> dict[str, Skill]:
    raw = _load_raw()
    return {
        item["id"]: Skill(id=item["id"], name=item["name"])
        for item in raw.get("skills") or []
    }


@lru_cache(maxsize=1)
def load_task_types() -> dict[str, TaskType]:
    raw = _load_raw()
    return {
        item["id"]: TaskType(
            id=item["id"],
            name=item["name"],
            required_skills=tuple(item.get("required_skills") or []),
            type_weight=float(item.get("type_weight") or 1.0),
        )
        for item in raw.get("task_types") or []
    }


@lru_cache(maxsize=1)
def load_skill_to_topic() -> dict[str, int]:
    raw = _load_raw()
    return {str(k): int(v) for k, v in (raw.get("skill_to_topic") or {}).items()}


def infer_topic_id(
    explicit_topic_id: int | None,
    skills: list[str],
    skill_to_topic: dict[str, int] | None = None,
) -> int:
    if explicit_topic_id is not None:
        return explicit_topic_id
    mapping = skill_to_topic or load_skill_to_topic()
    for skill in skills:
        if skill in mapping:
            return mapping[skill]
    return 1
