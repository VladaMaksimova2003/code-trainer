from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.learning.group import IGroupRepository
from domain.entities.learning.group import Group
from infrastructure.db.models.learning.group import Group as GroupModel
from infrastructure.db.models.learning.group import group_member_association_table
from infrastructure.db.models.learning.invitation_code import InvitationCodeModel


class SqlAlchemyGroupRepository(IGroupRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: GroupModel) -> Group:
        return Group(
            id=model.id,
            name=model.name,
            teacher_id=model.teacher_id,
            created_at=model.created_at,
        )

    def create(self, name: str, teacher_id: int) -> Group:
        row = GroupModel(name=name, teacher_id=teacher_id)
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return self._to_entity(row)

    def get_by_id(self, group_id: int) -> Group | None:
        row = self._session.get(GroupModel, group_id)
        return self._to_entity(row) if row else None

    def list_by_teacher(self, teacher_id: int) -> list[Group]:
        rows = self._session.execute(
            select(GroupModel)
            .where(GroupModel.teacher_id == teacher_id)
            .order_by(GroupModel.name)
        ).scalars().all()
        return [self._to_entity(r) for r in rows]

    def list_for_student(self, student_id: int) -> list[Group]:
        rows = self._session.execute(
            select(GroupModel)
            .join(
                group_member_association_table,
                group_member_association_table.c.group_id == GroupModel.id,
            )
            .where(group_member_association_table.c.student_id == student_id)
            .order_by(GroupModel.name)
        ).scalars().all()
        return [self._to_entity(r) for r in rows]

    def add_member(self, group_id: int, student_id: int) -> None:
        self._session.execute(
            group_member_association_table.insert().values(
                group_id=group_id, student_id=student_id
            )
        )
        self._session.flush()

    def is_member(self, group_id: int, student_id: int) -> bool:
        stmt = select(group_member_association_table).where(
            group_member_association_table.c.group_id == group_id,
            group_member_association_table.c.student_id == student_id,
        )
        return self._session.execute(stmt).first() is not None

    def student_teacher_ids(self, student_id: int) -> set[int]:
        stmt = (
            select(GroupModel.teacher_id)
            .join(
                group_member_association_table,
                group_member_association_table.c.group_id == GroupModel.id,
            )
            .where(group_member_association_table.c.student_id == student_id)
        )
        return set(self._session.execute(stmt).scalars().all())

    def list_member_ids(self, group_id: int) -> list[int]:
        stmt = select(group_member_association_table.c.student_id).where(
            group_member_association_table.c.group_id == group_id
        )
        return list(self._session.execute(stmt).scalars().all())

    def delete(self, group_id: int) -> bool:
        row = self._session.get(GroupModel, group_id)
        if row is None:
            return False
        self._session.execute(
            delete(InvitationCodeModel).where(InvitationCodeModel.group_id == group_id)
        )
        self._session.delete(row)
        self._session.flush()
        return True
