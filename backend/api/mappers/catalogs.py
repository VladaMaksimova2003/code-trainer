from domain.entities.tasks.catalog import Catalog, Task
from api.tasks.catalog_schemas import CatalogResponse, TaskResponse


def to_task_response(
    task: Task,
    *,
    catalog_ids: list[int] | None = None,
) -> TaskResponse:
    ids = catalog_ids or []
    return TaskResponse(
        id=task.id,
        title=task.title,
        content=task.content,
        topic_id=task.topic_id,
        type_id=task.type_id,
        created_at=task.created_at,
        updated_at=task.updated_at or task.created_at,
        difficulty=task.difficulty,
        language=task.language,
        languages=list(task.languages or ()),
        catalog_ids=ids,
        is_assigned=bool(ids),
        chapter_key=task.chapter_key,
        chapter_title=task.chapter_title,
        chapter_order=task.chapter_order,
        display_order=task.display_order,
        primary_action=task.primary_action,
        activity_label=task.activity_label,
        task_format=task.task_format,
        is_debug_task=task.is_debug_task,
        action_sort_order=task.action_sort_order,
    )


def to_catalog_response(catalog: Catalog, *, task_count: int = 0) -> CatalogResponse:
    return CatalogResponse(
        id=catalog.id,
        title=catalog.title,
        description=catalog.description,
        created_at=catalog.created_at,
        task_count=task_count,
        visibility=catalog.visibility,
        group_id=catalog.group_id,
        deadline_at=catalog.deadline_at,
    )
