from abc import ABC


class Entity(ABC):
    def __init__(self, id: int | None) -> None:
        self.id = id
