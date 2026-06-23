"""
Centralized visibility rules for tasks and assignment sets.

Public independent learning:
  - Tasks with visibility=public AND workflow active AND not deleted
  - Tasks in non-archived PUBLIC assignment sets

Teacher-based learning:
  - PRIVATE assignment sets for teacher owner or connected group members
  - PRIVATE tasks only via accessible private sets or teacher ownership
"""

from __future__ import annotations

import time

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from shared.enums import AssignmentSetVisibility, AssignmentWorkflowStatus, TaskVisibility, UserType
from shared.exceptions import AccessDeniedToContentError
from infrastructure.db.models.task.collection import Collection, collection_task_association_table
from infrastructure.db.models.learning.group import Group, group_member_association_table
from infrastructure.db.models.task import Task as TaskModel

_PUBLIC_TASK_IDS_TTL_SECONDS = 60.0
_public_task_ids_cache: tuple[float, frozenset[int]] | None = None


def invalidate_public_task_ids_cache() -> None:
    global _public_task_ids_cache
    _public_task_ids_cache = None


class ContentAccessService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def student_teacher_ids(self, student_id: int) -> set[int]:
        stmt = (
            select(Group.teacher_id)
            .join(
                group_member_association_table,
                group_member_association_table.c.group_id == Group.id,
            )
            .where(group_member_association_table.c.student_id == student_id)
        )
        return set(self._session.execute(stmt).scalars().all())

    def student_group_ids(self, student_id: int) -> set[int]:
        stmt = select(group_member_association_table.c.group_id).where(
            group_member_association_table.c.student_id == student_id
        )
        return set(self._session.execute(stmt).scalars().all())

    def _active_task_clause(self):
        return (
            TaskModel.is_delete.is_(False),
            TaskModel.workflow_status == AssignmentWorkflowStatus.ACTIVE.value,
        )

    def can_access_assignment_set(
        self,
        user_id: int | None,
        roles: frozenset[UserType],
        assignment_set_id: int,
    ) -> bool:
        row = self._session.get(Collection, assignment_set_id)
        if row is None or row.is_archived:
            return False
        if row.visibility == AssignmentSetVisibility.PUBLIC:
            return True
        if user_id is None:
            return False
        if UserType.ADMIN in roles:
            return True
        if user_id == row.teacher_id:
            return True
        if row.group_id is not None:
            return row.group_id in self.student_group_ids(user_id)
        teacher_groups = (
            self._session.execute(
                select(Group.id).where(Group.teacher_id == row.teacher_id)
            )
            .scalars()
            .all()
        )
        student_groups = self.student_group_ids(user_id)
        return bool(set(teacher_groups) & student_groups)

    def can_access_task(
        self,
        user_id: int | None,
        roles: frozenset[UserType],
        task_id: int,
    ) -> bool:
        task = self._session.get(TaskModel, task_id)
        if task is None or task.is_delete:
            return False
        if task.workflow_status != AssignmentWorkflowStatus.ACTIVE.value:
            if UserType.ADMIN not in roles:
                return False

        from application.curriculum.course_scope import curriculum_task_in_scope

        if not curriculum_task_in_scope(task):
            return UserType.ADMIN in roles

        if task.visibility == TaskVisibility.PUBLIC:
            return True

        if user_id is None:
            return False
        if UserType.ADMIN in roles:
            return True
        if task.teacher_id == user_id:
            return True

        sets = (
            self._session.execute(
                select(Collection)
                .join(
                    collection_task_association_table,
                    collection_task_association_table.c.collection_id == Collection.id,
                )
                .where(
                    collection_task_association_table.c.task_id == task_id,
                    Collection.is_archived.is_(False),
                )
            )
            .scalars()
            .all()
        )
        for s in sets:
            if self.can_access_assignment_set(user_id, roles, s.id):
                return True
        return False

    def ensure_task_access(
        self,
        user_id: int | None,
        roles: frozenset[UserType],
        task_id: int,
    ) -> None:
        if not self.can_access_task(user_id, roles, task_id):
            raise AccessDeniedToContentError("You do not have access to this assignment.")

    def list_accessible_task_ids(
        self,
        user_id: int | None,
        roles: frozenset[UserType],
    ) -> set[int]:
        public_ids = self.public_task_ids()
        if user_id is None:
            return public_ids
        if UserType.ADMIN in roles:
            stmt = select(TaskModel.id).where(*self._active_task_clause())
            return set(self._session.execute(stmt).scalars().all())

        private_via_teacher: set[int] = set()
        teacher_ids = self.student_teacher_ids(user_id)
        if teacher_ids:
            stmt = select(TaskModel.id).where(
                TaskModel.teacher_id.in_(teacher_ids),
                *self._active_task_clause(),
            )
            private_via_teacher = set(self._session.execute(stmt).scalars().all())

        private_via_sets: set[int] = set()
        accessible_sets = self.accessible_assignment_sets_for_user(user_id, roles)
        if accessible_sets:
            set_ids = [row.id for row in accessible_sets]
            stmt = select(collection_task_association_table.c.task_id).where(
                collection_task_association_table.c.collection_id.in_(set_ids)
            )
            private_via_sets = set(self._session.execute(stmt).scalars().all())

        return public_ids | private_via_teacher | private_via_sets

    def is_public_task(self, task_id: int) -> bool:
        task = self._session.get(TaskModel, task_id)
        if task is None or task.is_delete:
            return False
        if task.workflow_status != AssignmentWorkflowStatus.ACTIVE.value:
            return False
        from application.curriculum.course_scope import curriculum_task_in_scope

        if not curriculum_task_in_scope(task):
            return False
        if task.visibility == TaskVisibility.PUBLIC:
            return True
        in_public_set = self._session.execute(
            select(collection_task_association_table.c.task_id)
            .join(Collection, Collection.id == collection_task_association_table.c.collection_id)
            .where(
                collection_task_association_table.c.task_id == task_id,
                Collection.visibility == AssignmentSetVisibility.PUBLIC,
                Collection.is_archived.is_(False),
            )
            .limit(1)
        ).first()
        return in_public_set is not None

    def public_task_ids(self) -> set[int]:
        global _public_task_ids_cache
        now = time.monotonic()
        if _public_task_ids_cache is not None:
            cached_at, cached_ids = _public_task_ids_cache
            if now - cached_at < _PUBLIC_TASK_IDS_TTL_SECONDS:
                return set(cached_ids)

        in_public_set = (
            select(collection_task_association_table.c.task_id)
            .join(Collection, Collection.id == collection_task_association_table.c.collection_id)
            .where(
                Collection.visibility == AssignmentSetVisibility.PUBLIC,
                Collection.is_archived.is_(False),
            )
        )
        stmt = select(TaskModel.id).where(
            *self._active_task_clause(),
            or_(
                TaskModel.visibility == TaskVisibility.PUBLIC,
                TaskModel.id.in_(in_public_set),
            ),
        )
        ids = frozenset(self._session.execute(stmt).scalars().all())
        from application.curriculum.course_scope import filter_task_ids_to_course_scope

        ids = frozenset(filter_task_ids_to_course_scope(ids, self._session))
        _public_task_ids_cache = (now, ids)
        return set(ids)

    def accessible_assignment_sets_for_user(
        self, user_id: int, roles: frozenset[UserType]
    ) -> list[Collection]:
        if UserType.ADMIN in roles:
            return list(
                self._session.execute(
                    select(Collection).where(Collection.is_archived.is_(False))
                )
                .scalars()
                .all()
            )
        student_groups = self.student_group_ids(user_id)
        teacher_ids = self.student_teacher_ids(user_id)
        clauses = [Collection.visibility == AssignmentSetVisibility.PUBLIC]
        if student_groups:
            clauses.append(Collection.group_id.in_(student_groups))
        stmt = select(Collection).where(
            Collection.is_archived.is_(False),
            or_(*clauses),
        )
        rows = list(self._session.execute(stmt).scalars().all())
        extra: list[Collection] = []
        if teacher_ids:
            teacher_sets = self._session.execute(
                select(Collection).where(
                    Collection.teacher_id.in_(teacher_ids),
                    Collection.visibility == AssignmentSetVisibility.PRIVATE,
                    Collection.group_id.is_(None),
                    Collection.is_archived.is_(False),
                )
            ).scalars().all()
            extra.extend(teacher_sets)
        seen = {r.id for r in rows}
        for r in extra:
            if r.id not in seen:
                rows.append(r)
                seen.add(r.id)
        return rows

    def _task_ids_for_set(self, set_id: int) -> list[int]:
        stmt = select(collection_task_association_table.c.task_id).where(
            collection_task_association_table.c.collection_id == set_id
        )
        return list(self._session.execute(stmt).scalars().all())

    def is_student_connected_to_teacher(self, student_id: int, teacher_id: int) -> bool:
        return teacher_id in self.student_teacher_ids(student_id)
