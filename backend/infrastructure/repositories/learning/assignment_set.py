from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.learning.assignment_set import IAssignmentSetRepository
from shared.enums import AssignmentSetVisibility
from domain.entities.tasks.assignment_set import AssignmentSet, AssignmentSetItem
from infrastructure.db.models.task.collection import (
    Collection,
    collection_task_association_table,
)
from infrastructure.db.models.task.enum_types import coerce_enum


class SqlAlchemyAssignmentSetRepository(IAssignmentSetRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _items_for_set(self, set_id: int) -> list[AssignmentSetItem]:
        stmt = (
            select(
                collection_task_association_table.c.task_id,
                collection_task_association_table.c.sort_order,
                collection_task_association_table.c.topic,
            )
            .where(collection_task_association_table.c.collection_id == set_id)
            .order_by(collection_task_association_table.c.sort_order)
        )
        return [
            AssignmentSetItem(
                assignment_set_id=set_id,
                task_id=task_id,
                sort_order=sort_order or 0,
                topic=topic,
            )
            for task_id, sort_order, topic in self._session.execute(stmt).all()
        ]

    def _to_entity(self, row: Collection) -> AssignmentSet:
        items = self._items_for_set(row.id)
        return AssignmentSet(
            id=row.id,
            name=row.name,
            description=row.description or "",
            teacher_id=row.teacher_id,
            visibility=coerce_enum(
                AssignmentSetVisibility,
                row.visibility,
                default=AssignmentSetVisibility.PRIVATE,
            ),
            group_id=row.group_id,
            is_archived=bool(row.is_archived),
            items=items,
            created_at=row.created_at,
            deadline_at=row.deadline_at,
        )

    def _load(self, set_id: int) -> Collection | None:
        return self._session.get(Collection, set_id)

    def create(
        self,
        name: str,
        description: str,
        teacher_id: int,
        visibility: AssignmentSetVisibility,
        group_id: int | None,
    ) -> AssignmentSet:
        row = Collection(
            name=name,
            description=description,
            teacher_id=teacher_id,
            visibility=visibility,
            group_id=group_id,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return AssignmentSet(
            id=row.id,
            name=row.name,
            description=row.description or "",
            teacher_id=row.teacher_id,
            visibility=coerce_enum(
                AssignmentSetVisibility, row.visibility, default=visibility
            ),
            group_id=row.group_id,
            is_archived=False,
            created_at=row.created_at,
            deadline_at=row.deadline_at,
        )

    def get_by_id(self, set_id: int) -> AssignmentSet | None:
        row = self._load(set_id)
        return self._to_entity(row) if row else None

    def update(
        self,
        set_id: int,
        name: str | None,
        description: str | None,
        visibility: AssignmentSetVisibility | None,
        group_id: int | None,
        is_archived: bool | None,
    ) -> AssignmentSet:
        row = self._session.get(Collection, set_id)
        if row is None:
            raise ValueError("Assignment set not found")
        if name is not None:
            row.name = name
        if description is not None:
            row.description = description
        if visibility is not None:
            row.visibility = visibility
        row.group_id = group_id
        if is_archived is not None:
            row.is_archived = is_archived
        self._session.flush()
        refreshed = self._load(set_id)
        return self._to_entity(refreshed)

    def list_for_teacher(self, teacher_id: int, include_archived: bool = False) -> list[AssignmentSet]:
        stmt = select(Collection).where(Collection.teacher_id == teacher_id)
        if not include_archived:
            stmt = stmt.where(Collection.is_archived.is_(False))
        rows = self._session.execute(stmt.order_by(Collection.name)).scalars().all()
        return [
            AssignmentSet(
                id=r.id,
                name=r.name,
                description=r.description or "",
                teacher_id=r.teacher_id,
                visibility=coerce_enum(
                    AssignmentSetVisibility,
                    r.visibility,
                    default=AssignmentSetVisibility.PRIVATE,
                ),
                group_id=r.group_id,
                is_archived=bool(r.is_archived),
                created_at=r.created_at,
                deadline_at=r.deadline_at,
            )
            for r in rows
        ]

    def list_discoverable_public(self) -> list[AssignmentSet]:
        rows = self._session.execute(
            select(Collection).where(
                Collection.visibility == AssignmentSetVisibility.PUBLIC,
                Collection.is_archived.is_(False),
            ).order_by(Collection.name)
        ).scalars().all()
        return [
            AssignmentSet(
                id=r.id,
                name=r.name,
                description=r.description or "",
                teacher_id=r.teacher_id,
                visibility=AssignmentSetVisibility.PUBLIC,
                group_id=r.group_id,
                is_archived=False,
                created_at=r.created_at,
                deadline_at=r.deadline_at,
            )
            for r in rows
        ]

    def add_item(
        self, set_id: int, task_id: int, sort_order: int, topic: str | None
    ) -> AssignmentSetItem:
        self._session.execute(
            collection_task_association_table.insert().values(
                collection_id=set_id,
                task_id=task_id,
                sort_order=sort_order,
                topic=topic,
            )
        )
        self._session.flush()
        return AssignmentSetItem(
            assignment_set_id=set_id,
            task_id=task_id,
            sort_order=sort_order,
            topic=topic,
        )

    def remove_item(self, set_id: int, task_id: int) -> None:
        self._session.execute(
            delete(collection_task_association_table).where(
                collection_task_association_table.c.collection_id == set_id,
                collection_task_association_table.c.task_id == task_id,
            )
        )
        self._session.flush()

    def task_ids_in_set(self, set_id: int) -> list[int]:
        stmt = (
            select(collection_task_association_table.c.task_id)
            .where(collection_task_association_table.c.collection_id == set_id)
            .order_by(collection_task_association_table.c.sort_order)
        )
        return list(self._session.execute(stmt).scalars().all())

    def sets_containing_task(self, task_id: int) -> list[AssignmentSet]:
        rows = self._session.execute(
            select(Collection)
            .join(
                collection_task_association_table,
                collection_task_association_table.c.collection_id == Collection.id,
            )
            .where(collection_task_association_table.c.task_id == task_id)
        ).scalars().all()
        return [
            AssignmentSet(
                id=r.id,
                name=r.name,
                description=r.description or "",
                teacher_id=r.teacher_id,
                visibility=coerce_enum(
                    AssignmentSetVisibility,
                    r.visibility,
                    default=AssignmentSetVisibility.PRIVATE,
                ),
                group_id=r.group_id,
                is_archived=bool(r.is_archived),
                created_at=r.created_at,
                deadline_at=r.deadline_at,
            )
            for r in rows
        ]

    def count_by_teacher(self, teacher_id: int) -> int:
        from sqlalchemy import func

        return (
            self._session.scalar(
                select(func.count())
                .select_from(Collection)
                .where(
                    Collection.teacher_id == teacher_id,
                    Collection.is_archived.is_(False),
                )
            )
            or 0
        )
