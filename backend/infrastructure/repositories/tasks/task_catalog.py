from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from application.curriculum.mirror.pedagogical_task_model import available_language_tracks
from application.curriculum.mirror.pedagogical_task_store import unified_pedagogical_slot_key
from application.tasks.services.catalog.task_display import display_title_for_task_model
from application.tasks.services.catalog.task_teacher_list_meta import teacher_list_meta_for_row
from domain.learning.curriculum.constants import SUPPORTED_CURRICULUM_LANGUAGES
from shared.interfaces.repositories.tasks.task_catalog import (
    ICatalogRepository,
    ICatalogTaskRelationRepository,
    ITaskRepository,
)
from domain.entities.tasks.catalog import Catalog, CatalogTaskRelation, Task
from shared.enums import AssignmentSetVisibility, TaskVisibility
from infrastructure.db.models.task.collection import (
    Collection,
    collection_task_association_table,
)
from infrastructure.db.models.task import Task as TaskModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


_NON_LANGUAGE_CODE_EXAMPLE_KEYS = frozenset(
    {
        "patterns",
        "constructions",
        "curriculum_showcase",
        "mcq_options",
    }
)


def _showcase_dict(row: TaskModel) -> dict:
    raw = (row.code_examples or {}).get("curriculum_showcase")
    return dict(raw) if isinstance(raw, dict) else {}


def _display_title_for_task(row: TaskModel) -> str:
    return display_title_for_task_model(row)


def _teacher_list_dedupe_key(row: TaskModel) -> str:
    showcase = _showcase_dict(row)
    unified = unified_pedagogical_slot_key(showcase)
    if unified:
        return f"ped:{unified}"
    return f"row:{row.id}"


def _canonical_teacher_row_score(row: TaskModel, showcase: dict) -> tuple[int, int]:
    """Keep the earliest curriculum row (lowest id), not the mirror copy."""
    del showcase
    return (0, -row.id)


def _merge_languages_from_rows(rows: list[TaskModel]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for lang in _collect_task_languages(row):
            if lang in seen:
                continue
            seen.add(lang)
            ordered.append(lang)
    return ordered


def _teacher_list_sort_key(
    item: tuple[TaskModel, list[str] | None],
    *,
    chapter_titles: dict[str, str] | None = None,
) -> tuple[int, int, int]:
    meta = teacher_list_meta_for_row(item[0], chapter_titles=chapter_titles)
    return (
        meta.chapter_order if meta.chapter_order is not None else 999,
        meta.display_order if meta.display_order is not None else 999_999,
        item[0].id,
    )


def _dedupe_teacher_task_rows(
    rows: list[TaskModel],
    *,
    chapter_titles: dict[str, str] | None = None,
) -> list[tuple[TaskModel, list[str] | None]]:
    groups: dict[str, list[TaskModel]] = {}
    for row in rows:
        groups.setdefault(_teacher_list_dedupe_key(row), []).append(row)

    deduped: list[tuple[TaskModel, list[str] | None]] = []
    for group in groups.values():
        if len(group) == 1:
            deduped.append((group[0], None))
            continue
        canonical = max(
            group,
            key=lambda candidate: _canonical_teacher_row_score(candidate, _showcase_dict(candidate)),
        )
        deduped.append((canonical, _merge_languages_from_rows(group)))
    deduped.sort(key=lambda item: _teacher_list_sort_key(item, chapter_titles=chapter_titles))
    return deduped


def _collect_task_languages(row: TaskModel) -> list[str]:
    showcase = _showcase_dict(row)
    if showcase:
        tracks = available_language_tracks(showcase)
        if tracks:
            return tracks

    ordered: list[str] = []
    seen: set[str] = set()
    allowed = set(SUPPORTED_CURRICULUM_LANGUAGES)

    def add(lang: str | None) -> None:
        if not lang:
            return
        key = str(lang).strip().lower()
        if not key or key in seen or key not in allowed:
            return
        seen.add(key)
        ordered.append(key)

    block = getattr(row, "block_reorder_task", None)
    if block is not None:
        add(block.language)
        for variant_lang in (block.language_variants or {}):
            add(variant_lang)

    translation = getattr(row, "translation_task", None)
    if translation is not None:
        add(translation.source_language)
        add(getattr(translation, "target_language", None))

    for example_lang in (row.code_examples or {}):
        if example_lang in _NON_LANGUAGE_CODE_EXAMPLE_KEYS:
            continue
        add(example_lang)

    return ordered


def _task_from_model(
    row: TaskModel,
    *,
    languages: list[str] | None = None,
    chapter_titles: dict[str, str] | None = None,
) -> Task:
    created_at = getattr(row, "created_at", None) or _utc_now()
    updated_at = getattr(row, "updated_at", None) or created_at
    topic_id = getattr(row, "topic_id", None)
    resolved_languages = languages if languages is not None else _collect_task_languages(row)
    meta = teacher_list_meta_for_row(row, chapter_titles=chapter_titles)
    return Task(
        id=row.id,
        title=_display_title_for_task(row),
        content=row.description or "",
        topic_id=topic_id,
        type_id=row.task_type,
        created_at=created_at,
        updated_at=updated_at,
        difficulty=getattr(row, "difficulty", None),
        language=resolved_languages[0] if resolved_languages else None,
        languages=tuple(resolved_languages),
        chapter_key=meta.chapter_key,
        chapter_title=meta.chapter_title,
        chapter_order=meta.chapter_order,
        display_order=meta.display_order,
        primary_action=meta.primary_action,
        activity_label=meta.activity_label,
        task_format=meta.task_format,
        is_debug_task=meta.is_debug_task,
        action_sort_order=meta.action_sort_order,
    )


def _task_query():
    return select(TaskModel).options(
        joinedload(TaskModel.block_reorder_task),
        joinedload(TaskModel.translation_task),
    )


class SqlAlchemyTaskCatalogRepository(ITaskRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        title: str,
        content: str,
        topic_id: int | None,
        type_id: str,
        teacher_id: int,
    ) -> Task:
        row = TaskModel(
            teacher_id=teacher_id,
            title=title,
            description=content,
            task_type=type_id,
            difficulty="easy",
            test_cases=[],
            code_examples={},
            flow_spec={},
        )
        if hasattr(TaskModel, "topic_id"):
            row.topic_id = topic_id
        if hasattr(TaskModel, "created_at"):
            row.created_at = _utc_now()
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return _task_from_model(row)

    def get_by_id(self, task_id: int) -> Task | None:
        row = self._session.execute(
            _task_query().where(TaskModel.id == task_id, TaskModel.is_delete == False)
        ).unique().scalar_one_or_none()
        if row is None:
            return None
        return _task_from_model(row)

    def list_for_teacher(self, teacher_id: int) -> list[Task]:
        from application.curriculum.chapters.curriculum_chapter_meta_service import get_chapter_title_map

        chapter_titles = get_chapter_title_map(self._session)
        from shared.enums import AssignmentWorkflowStatus

        rows = self._session.execute(
            _task_query()
            .where(
                TaskModel.teacher_id == teacher_id,
                TaskModel.is_delete == False,
                TaskModel.workflow_status == AssignmentWorkflowStatus.ACTIVE.value,
            )
            .order_by(TaskModel.id)
        ).unique().scalars().all()
        return [
            _task_from_model(row, languages=languages, chapter_titles=chapter_titles)
            for row, languages in _dedupe_teacher_task_rows(rows, chapter_titles=chapter_titles)
        ]

    def delete(self, task_id: int) -> None:
        row = self._session.get(TaskModel, task_id)
        if row is None:
            return
        row.is_delete = True
        self._session.flush()


class SqlAlchemyCatalogRepository(ICatalogRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, row: Collection) -> Catalog:
        return Catalog(
            id=row.id,
            title=row.name,
            description=row.description or None,
            created_at=row.created_at or _utc_now(),
            visibility=row.visibility.value if hasattr(row.visibility, "value") else str(row.visibility),
            group_id=row.group_id,
            deadline_at=getattr(row, "deadline_at", None),
        )

    def create(
        self,
        *,
        title: str,
        description: str | None,
        teacher_id: int,
        visibility: str = AssignmentSetVisibility.PUBLIC.value,
        group_id: int | None = None,
    ) -> Catalog:
        visibility_enum = AssignmentSetVisibility(visibility)
        row = Collection(
            name=title,
            description=description or "",
            teacher_id=teacher_id,
            visibility=visibility_enum,
            group_id=group_id,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return self._to_entity(row)

    def get_by_id(self, catalog_id: int) -> Catalog | None:
        row = self._session.get(Collection, catalog_id)
        if row is None or row.is_archived:
            return None
        return self._to_entity(row)

    def list_for_teacher(self, teacher_id: int) -> list[Catalog]:
        rows = self._session.execute(
            select(Collection)
            .where(
                Collection.teacher_id == teacher_id,
                Collection.is_archived.is_(False),
            )
            .order_by(Collection.name)
        ).scalars().all()
        return [self._to_entity(row) for row in rows]

    def delete(self, catalog_id: int) -> None:
        row = self._session.get(Collection, catalog_id)
        if row is None:
            return
        self._session.delete(row)
        self._session.flush()


class SqlAlchemyCatalogTaskRelationRepository(ICatalogTaskRelationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def assign(self, task_id: int, catalog_id: int) -> CatalogTaskRelation:
        catalog = self._session.get(Collection, catalog_id)
        task = self._session.get(TaskModel, task_id)
        self._session.execute(
            collection_task_association_table.insert().values(
                collection_id=catalog_id,
                task_id=task_id,
                sort_order=0,
            )
        )
        if (
            catalog is not None
            and task is not None
            and catalog.visibility == AssignmentSetVisibility.PRIVATE
        ):
            task.visibility = TaskVisibility.PRIVATE
        self._session.flush()
        return CatalogTaskRelation(task_id=task_id, catalog_id=catalog_id)

    def remove(self, task_id: int, catalog_id: int) -> None:
        self._session.execute(
            delete(collection_task_association_table).where(
                collection_task_association_table.c.collection_id == catalog_id,
                collection_task_association_table.c.task_id == task_id,
            )
        )
        self._session.flush()

    def remove_all_for_task(self, task_id: int) -> None:
        self._session.execute(
            delete(collection_task_association_table).where(
                collection_task_association_table.c.task_id == task_id
            )
        )
        self._session.flush()

    def list_task_ids_by_catalog(self, catalog_id: int) -> list[int]:
        stmt = (
            select(collection_task_association_table.c.task_id)
            .where(collection_task_association_table.c.collection_id == catalog_id)
            .order_by(collection_task_association_table.c.sort_order)
        )
        return list(self._session.execute(stmt).scalars().all())

    def list_catalog_ids_by_task(self, task_id: int) -> list[int]:
        stmt = select(collection_task_association_table.c.collection_id).where(
            collection_task_association_table.c.task_id == task_id
        )
        return list(self._session.execute(stmt).scalars().all())

    def is_assigned(self, task_id: int, catalog_id: int) -> bool:
        stmt = select(collection_task_association_table.c.task_id).where(
            collection_task_association_table.c.collection_id == catalog_id,
            collection_task_association_table.c.task_id == task_id,
        )
        return self._session.execute(stmt).first() is not None
