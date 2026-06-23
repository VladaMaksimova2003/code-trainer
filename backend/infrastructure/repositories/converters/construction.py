from infrastructure.db.models.task.construction import Construction as ConstructionModel
from domain.entities.construction import Construction
from infrastructure.repositories.converters.category_construction import (
    SqlAlchemyCategoryConstructionConverter,
)
from infrastructure.repositories.converters.base import Converter


class SqlAlchemyConstructionConverter(Converter[Construction, ConstructionModel]):
    def to_entity(self, model: ConstructionModel) -> Construction:
        return Construction(
            id=model.id,
            name=model.name,
            description=model.description,
            category_id=model.category_id,
        )

    def to_model(self, entity: Construction) -> ConstructionModel:
        return ConstructionModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            category_id=entity.category_id,
        )
