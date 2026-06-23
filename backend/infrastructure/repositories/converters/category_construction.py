from infrastructure.db.models.task.construction import (
    CategoryConstruction as CategoryConstructionModel,
)
from domain.entities.category_construction import CategoryConstruction
from infrastructure.repositories.converters.base import Converter


class SqlAlchemyCategoryConstructionConverter(
    Converter[CategoryConstruction, CategoryConstructionModel]
):
    def to_entity(self, model: CategoryConstructionModel) -> CategoryConstruction:
        return CategoryConstruction(id=model.id, name=model.name)

    def to_model(self, entity: CategoryConstruction) -> CategoryConstructionModel:
        return CategoryConstructionModel(id=entity.id, name=entity.name)
