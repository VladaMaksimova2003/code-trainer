"""Student mastery map over concepts.yml (adaptive layer only)."""
from __future__ import annotations

from dataclasses import dataclass, field

from domain.learning.skill_groups import CONCEPT_IDS

CONCEPT_LIST: tuple[str, ...] = tuple(sorted(CONCEPT_IDS))


@dataclass
class StudentStructureProfile:
    user_id: int
    structures: dict[str, bool] = field(default_factory=dict)
    weak_areas: list[str] = field(default_factory=list)
    failure_counts: dict[str, int] = field(default_factory=dict)
    learning_level: str = "beginner"
    consecutive_passes: int = 0

    def __post_init__(self) -> None:
        for name in CONCEPT_LIST:
            self.structures.setdefault(name, False)
            self.failure_counts.setdefault(name, 0)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "structures": {k: bool(self.structures.get(k, False)) for k in CONCEPT_LIST},
            "weak_areas": list(self.weak_areas),
            "failure_counts": dict(self.failure_counts),
            "learning_level": self.learning_level,
            "consecutive_passes": self.consecutive_passes,
        }

    @classmethod
    def empty(cls, user_id: int) -> StudentStructureProfile:
        return cls(user_id=user_id)
