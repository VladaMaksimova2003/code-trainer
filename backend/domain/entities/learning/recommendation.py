from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Topic:
    id: int
    name: str
    prerequisites: tuple[int, ...]
    skills: tuple[str, ...]


@dataclass(frozen=True)
class Skill:
    id: str
    name: str


@dataclass(frozen=True)
class TaskType:
    id: str
    name: str
    required_skills: tuple[str, ...]
    type_weight: float


@dataclass(frozen=True)
class RecTask:
    id: int
    topic_id: int
    type_id: str
    skills_required: tuple[str, ...]
    created_by_teacher: bool
    collection_id: int | None


@dataclass
class HistoryEntry:
    task_id: int
    topic_id: int
    skills: tuple[str, ...]
    type_id: str
    success: bool


@dataclass
class StudentState:
    topic_mastery: dict[int, float] = field(default_factory=dict)
    skill_mastery: dict[str, float] = field(default_factory=dict)
    history: list[HistoryEntry] = field(default_factory=list)
    solved_task_ids: set[int] = field(default_factory=set)
    last_type_id: str | None = None

    # Сколько раз подряд студент провалил задание на этот навык.
    # Сбрасывается в 0 при первом успехе. Используется для обнаружения
    # «застрял» — когда нужно предложить шаг назад к prerequisites.
    skill_fail_streak: dict[str, int] = field(default_factory=dict)

    # Сколько всего попыток студент делал на задания с этим навыком.
    # Позволяет различить mastery=0 «ещё не учил» от mastery=0 «учил, но забыл».
    skill_attempt_count: dict[str, int] = field(default_factory=dict)
