from domain.entities.base import Entity


class Construction(Entity):
    def __init__(
        self,
        id: int | None,
        name: str,
        description: str,
        category_id: int | None,
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.category_id = category_id
