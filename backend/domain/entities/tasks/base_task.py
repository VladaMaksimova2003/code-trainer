from abc import abstractmethod
from typing import Self
from shared.enums import Difficulty, TaskType
from domain.entities.base import Entity
from domain.entities.construction import Construction


class BaseTask(Entity):

    def __init__(
        self,
        id: int | None,
        teacher_id: int,
        title: str,
        difficulty: Difficulty,
        description: str,
        task_type: TaskType,
        constructions: list[Construction] | None = None,
        version: int = 1,
        is_deleted: bool = False,
    ):
        super().__init__(id)
        self.teacher_id = teacher_id
        self.title = title
        self.difficulty = difficulty
        self.description = description
        self.task_type = task_type
        self.constructions = constructions or []
        self.version = version
        self.is_deleted = is_deleted

    def clone(self) -> Self:
        return type(self)(
            id=None,
            title=self.title,
            difficulty=self.difficulty,
            description=self.description,
            task_type=self.task_type,
            constructions=self.constructions.copy(),
            version=self.version + 1,
            is_deleted=False,
        )

    @abstractmethod
    def update(self, data: "BaseTask") -> "BaseTask":
        pass
