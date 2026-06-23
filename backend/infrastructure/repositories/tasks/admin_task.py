from sqlalchemy import select
from sqlalchemy.orm import Session

from application.admin.assignment_placement import admin_assignment_placement_for_row
from application.curriculum.chapters.curriculum_chapter_meta_service import get_chapter_title_map
from shared.interfaces.repositories.admin.admin_task import (
    AdminAssignmentListItem,
    AdminAssignmentVersionItem,
    IAdminTaskRepository,
)
from shared.enums import AssignmentWorkflowStatus
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task.task_version import TaskVersion
from infrastructure.db.models.user.user import User


class SqlAlchemyAdminTaskRepository(IAdminTaskRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_assignments(self, include_deleted: bool = True) -> list[AdminAssignmentListItem]:
        stmt = (
            select(TaskModel, User)
            .outerjoin(User, TaskModel.teacher_id == User.id)
            .order_by(TaskModel.id.desc())
        )
        if not include_deleted:
            stmt = stmt.where(TaskModel.is_delete.is_(False))
        rows = self._session.execute(stmt).all()
        chapter_titles = get_chapter_title_map(self._session)

        items: list[AdminAssignmentListItem] = []
        for task, teacher in rows:
            placement = admin_assignment_placement_for_row(
                task,
                chapter_titles=chapter_titles,
                teacher_name=str(teacher.name) if teacher is not None else None,
                teacher_email=str(teacher.email) if teacher is not None else None,
            )
            items.append(
                AdminAssignmentListItem(
                    id=task.id,
                    title=task.title,
                    task_type=task.task_type,
                    difficulty=task.difficulty,
                    teacher_id=task.teacher_id,
                    version=task.version,
                    workflow_status=task.workflow_status or AssignmentWorkflowStatus.ACTIVE.value,
                    is_delete=bool(task.is_delete),
                    created_at=None,
                    collection_title=placement.collection_title,
                    chapter_title=placement.chapter_title,
                    chapter_key=placement.chapter_key,
                    language=placement.language,
                    chapter_slug=placement.chapter_slug,
                    teacher_name=placement.teacher_name,
                    teacher_email=placement.teacher_email,
                    teacher_is_deleted=bool(teacher.is_deleted) if teacher is not None else False,
                )
            )
        return items

    def set_workflow_status(self, task_id: int, status: AssignmentWorkflowStatus) -> None:
        task = self._session.get(TaskModel, task_id)
        if task is None or task.is_delete:
            raise ValueError("Assignment not found")
        task.workflow_status = status.value
        if status == AssignmentWorkflowStatus.ARCHIVED:
            task.is_delete = False
        self._session.flush()

    def archive_assignment(self, task_id: int) -> None:
        self.set_workflow_status(task_id, AssignmentWorkflowStatus.ARCHIVED)

    def list_versions(self, task_id: int) -> list[AdminAssignmentVersionItem]:
        stmt = (
            select(TaskVersion)
            .where(TaskVersion.task_id == task_id)
            .order_by(TaskVersion.version_number.desc())
        )
        rows = self._session.execute(stmt).scalars().all()
        return [
            AdminAssignmentVersionItem(
                id=v.id,
                task_id=v.task_id,
                version_number=v.version_number,
                title=v.title,
                is_active=bool(v.is_active),
                created_at=v.created_at,
            )
            for v in rows
        ]

    def create_version_snapshot(self, task_id: int) -> AdminAssignmentVersionItem:
        task = self._session.get(TaskModel, task_id)
        if task is None or task.is_delete:
            raise ValueError("Assignment not found")

        next_version = task.version + 1
        snapshot = {
            "test_cases": task.test_cases,
            "code_examples": task.code_examples,
            "flow_spec": task.flow_spec,
        }
        row = TaskVersion(
            task_id=task.id,
            version_number=next_version,
            title=task.title,
            description=task.description or "",
            difficulty=task.difficulty,
            task_type=task.task_type,
            snapshot=snapshot,
            is_active=True,
        )
        self._session.add(row)
        task.version = next_version
        self._session.flush()
        self._session.refresh(row)
        for existing in (
            self._session.execute(
                select(TaskVersion).where(
                    TaskVersion.task_id == task_id,
                    TaskVersion.id != row.id,
                )
            )
            .scalars()
            .all()
        ):
            existing.is_active = False
        self._session.flush()
        return AdminAssignmentVersionItem(
            id=row.id,
            task_id=row.task_id,
            version_number=row.version_number,
            title=row.title,
            is_active=row.is_active,
            created_at=row.created_at,
        )

    def activate_version(self, task_id: int, version_id: int) -> None:
        version = self._session.get(TaskVersion, version_id)
        if version is None or version.task_id != task_id:
            raise ValueError("Version not found")
        task = self._session.get(TaskModel, task_id)
        if task is None:
            raise ValueError("Assignment not found")

        all_versions = (
            self._session.execute(
                select(TaskVersion).where(TaskVersion.task_id == task_id)
            )
            .scalars()
            .all()
        )
        for v in all_versions:
            v.is_active = v.id == version_id

        task.title = version.title
        task.description = version.description
        task.difficulty = version.difficulty
        task.task_type = version.task_type
        task.version = version.version_number
        snap = version.snapshot or {}
        if "test_cases" in snap:
            task.test_cases = snap["test_cases"]
        if "code_examples" in snap:
            task.code_examples = snap["code_examples"]
        if "flow_spec" in snap:
            task.flow_spec = snap["flow_spec"]
        self._session.flush()
