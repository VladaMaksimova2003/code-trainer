from infrastructure.db.models.task import (
    Task as TaskModel,
    TranslationTask as TranslationTaskModel,
    BlockReorderTask as BlockReorderTaskModel,
)
from domain.entities.tasks.base_task import BaseTask
from domain.entities.tasks.translation_task import TranslationTask
from domain.entities.tasks.block_reorder_task import BlockReorderTask
from shared.enums import TaskType
from infrastructure.repositories.converters.base import Converter
from infrastructure.repositories.converters.construction import (
    SqlAlchemyConstructionConverter,
)


class SqlAlchemyTaskConverter(Converter[BaseTask, TaskModel]):
    def __init__(self):
        self._construction_converter = SqlAlchemyConstructionConverter()

    def to_entity(self, model: TaskModel) -> BaseTask:
        constructions = [
            self._construction_converter.to_entity(construction)
            for construction in model.constructions
        ]

        base_task = BaseTask(
            id=model.id,
            teacher_id=model.teacher_id,
            title=model.title,
            description=model.description,
            difficulty=model.difficulty,
            task_type=model.task_type,
            constructions=constructions,
            version=model.version,
            is_deleted=model.is_delete,
        )

        if model.task_type == TaskType.TRANSLATION:
            base_task.__class__ = TranslationTask
            base_task.source_code = model.translation_task.source_code
            base_task.source_language = model.translation_task.source_language

        elif model.task_type == TaskType.BLOCK_REORDER and model.block_reorder_task:
            base_task.__class__ = BlockReorderTask
            base_task.original_code = model.block_reorder_task.original_code
            base_task.template = model.block_reorder_task.template
            base_task.blocks = model.block_reorder_task.blocks
            base_task.correct_order = model.block_reorder_task.correct_order
            base_task.language = model.block_reorder_task.language
            base_task.language_variants = (
                model.block_reorder_task.language_variants or {}
            )

        return base_task

    def to_model(self, entity: BaseTask) -> TaskModel:
        construction_models = [
            self._construction_converter.to_model(construction)
            for construction in entity.constructions
        ]

        task_model = TaskModel(
            id=entity.id,
            teacher_id=entity.teacher_id,
            title=entity.title,
            description=entity.description,
            difficulty=entity.difficulty,
            task_type=entity.task_type,
            version=entity.version,
            is_delete=entity.is_deleted,
            constructions=construction_models,
        )

        if isinstance(entity, TranslationTask):
            task_model.translation_task = TranslationTaskModel(
                task_id=entity.id,
                source_code=entity.source_code,
                source_language=entity.source_language,
            )

        elif isinstance(entity, BlockReorderTask):
            task_model.block_reorder_task = BlockReorderTaskModel(
                task_id=entity.id,
                original_code=entity.original_code,
                template=entity.template,
                blocks=entity.blocks,
                correct_order=entity.correct_order,
                language=entity.language,
                language_variants=entity.language_variants or None,
            )

        return task_model
