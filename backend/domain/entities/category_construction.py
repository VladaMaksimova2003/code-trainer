from domain.entities.base import Entity


class CategoryConstruction(Entity):
    def __init__(
        self,
        id: int | None,
        name: str,
    ):
        super().__init__(id)
        self.name = name
