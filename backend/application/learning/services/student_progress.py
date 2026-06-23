from sqlalchemy import func, select
from sqlalchemy.orm import Session

from application.tasks.services.content_access_service import ContentAccessService
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel


class ListTeacherStudentsProgressUseCase:
    """Students who joined teacher groups only — not independent public-only solvers."""

    def __init__(self, session: Session, access: ContentAccessService) -> None:
        self._session = session
        self._access = access

    def execute(self, teacher_id: int) -> list[dict]:
        from infrastructure.db.models.learning.group import Group, group_member_association_table

        member_ids = set(
            self._session.execute(
                select(group_member_association_table.c.student_id)
                .join(Group, Group.id == group_member_association_table.c.group_id)
                .where(Group.teacher_id == teacher_id)
            ).scalars().all()
        )
        if not member_ids:
            return []

        teacher_task_ids = set(
            self._session.execute(
                select(TaskModel.id).where(TaskModel.teacher_id == teacher_id)
            ).scalars().all()
        )

        results = []
        for student_id in member_ids:
            if not teacher_task_ids:
                total, success = 0, 0
            else:
                stmt = (
                    select(
                        func.count(Submission.id),
                        func.count(Submission.id).filter(Submission.success.is_(True)),
                    )
                    .where(
                        Submission.user_id == student_id,
                        Submission.task_id.in_(teacher_task_ids),
                    )
                )
                total, success = self._session.execute(stmt).one()
            results.append(
                {
                    "student_id": student_id,
                    "total_submissions": int(total or 0),
                    "successful_submissions": int(success or 0),
                }
            )
        return results
