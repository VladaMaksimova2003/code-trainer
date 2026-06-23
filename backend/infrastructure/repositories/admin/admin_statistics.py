from datetime import date, datetime, timedelta, timezone



from sqlalchemy import func, select

from sqlalchemy.orm import Session



from application.curriculum.shared.algo_v128_showcase import curriculum_catalog_tasks_total
from shared.interfaces.repositories.admin.admin_statistics import (

    IAdminStatisticsRepository,

    RegistrationDayBucket,

    SystemStatistics,

)

from shared.enums import AssignmentWorkflowStatus, TeacherRoleRequestStatus, UserType

from infrastructure.db.models.learning.submission import Submission

from infrastructure.db.models.task import Task as TaskModel

from infrastructure.db.models.user.teacher_role_request import TeacherRoleRequestModel

from infrastructure.db.models.user import User as UserModel

from infrastructure.db.models.user.user_role import UserRole as UserRoleModel



REGISTRATION_PERIODS: dict[str, int] = {

    "week": 7,

    "month": 30,

    "half_year": 182,

    "year": 365,

}





class SqlAlchemyAdminStatisticsRepository(IAdminStatisticsRepository):

    def __init__(self, session: Session) -> None:

        self._session = session



    def collect(self) -> SystemStatistics:

        users_total = self._session.scalar(

            select(func.count()).select_from(UserModel).where(UserModel.is_deleted.is_(False))

        ) or 0



        users_by_role: dict[str, int] = {r.value: 0 for r in UserType}

        role_rows = self._session.execute(

            select(UserRoleModel.role, func.count(func.distinct(UserRoleModel.user_id)))

            .join(UserModel, UserModel.id == UserRoleModel.user_id)

            .where(UserModel.is_deleted.is_(False))

            .group_by(UserRoleModel.role)

        ).all()

        for role_value, cnt in role_rows:

            users_by_role[role_value] = int(cnt)



        assignments_total = self._session.scalar(

            select(func.count())

            .select_from(TaskModel)

            .where(TaskModel.is_delete.is_(False))

        ) or 0



        assignments_by_status: dict[str, int] = {

            s.value: 0 for s in AssignmentWorkflowStatus

        }

        status_rows = self._session.execute(

            select(TaskModel.workflow_status, func.count())

            .where(TaskModel.is_delete.is_(False))

            .group_by(TaskModel.workflow_status)

        ).all()

        for status_value, cnt in status_rows:

            key = status_value or AssignmentWorkflowStatus.ACTIVE.value

            assignments_by_status[key] = int(cnt)



        submissions_total = self._session.scalar(

            select(func.count()).select_from(Submission)

        ) or 0

        submissions_successful = self._session.scalar(

            select(func.count())

            .select_from(Submission)

            .where(Submission.success.is_(True))

        ) or 0



        solved_assignments_count = self._session.scalar(

            select(func.count(func.distinct(Submission.task_id))).where(

                Submission.success.is_(True)

            )

        ) or 0



        teacher_requests_pending = self._session.scalar(

            select(func.count())

            .select_from(TeacherRoleRequestModel)

            .where(

                TeacherRoleRequestModel.status == TeacherRoleRequestStatus.PENDING.value

            )

        ) or 0



        now = datetime.now(timezone.utc)

        month_ago = now - timedelta(days=30)



        users_new_last_month = self._session.scalar(

            select(func.count())

            .select_from(UserModel)

            .where(

                UserModel.is_deleted.is_(False),

                UserModel.created_at >= month_ago,

            )

        ) or 0



        users_new_last_month_by_role: dict[str, int] = {r.value: 0 for r in UserType}

        new_role_rows = self._session.execute(

            select(UserRoleModel.role, func.count(func.distinct(UserRoleModel.user_id)))

            .join(UserModel, UserModel.id == UserRoleModel.user_id)

            .where(

                UserModel.is_deleted.is_(False),

                UserModel.created_at >= month_ago,

            )

            .group_by(UserRoleModel.role)

        ).all()

        for role_value, cnt in new_role_rows:

            users_new_last_month_by_role[role_value] = int(cnt)



        tasks_new_last_30_days = self._session.scalar(

            select(func.count())

            .select_from(TaskModel)

            .where(

                TaskModel.is_delete.is_(False),

                TaskModel.created_at >= month_ago,

            )

        ) or 0



        registrations_by_period = {

            key: self._registrations_by_role_for_days(days)

            for key, days in REGISTRATION_PERIODS.items()

        }



        return SystemStatistics(

            users_total=users_total,

            users_by_role=users_by_role,

            assignments_total=assignments_total,

            assignments_by_status=assignments_by_status,

            submissions_total=submissions_total,

            submissions_successful=submissions_successful,

            solved_assignments_count=solved_assignments_count,

            teacher_requests_pending=teacher_requests_pending,

            registrations_by_period=registrations_by_period,

            users_new_last_month=int(users_new_last_month),

            users_new_last_month_by_role=users_new_last_month_by_role,

            tasks_new_last_30_days=int(tasks_new_last_30_days),

            curriculum_catalog_tasks=curriculum_catalog_tasks_total(),

        )



    def _registrations_by_role_for_days(self, days: int) -> list[RegistrationDayBucket]:

        today = datetime.now(timezone.utc).date()

        start = today - timedelta(days=days - 1)

        day_keys = [start + timedelta(days=i) for i in range(days)]

        counts: dict[date, dict[str, int]] = {

            day: {UserType.STUDENT.value: 0, UserType.TEACHER.value: 0, UserType.ADMIN.value: 0}

            for day in day_keys

        }



        rows = self._session.execute(

            select(UserModel.created_at, UserRoleModel.role)

            .join(UserRoleModel, UserRoleModel.user_id == UserModel.id)

            .where(

                UserModel.is_deleted.is_(False),

                UserModel.created_at.is_not(None),

            )

        ).all()



        for created_at, role in rows:

            if created_at is None:

                continue

            day = created_at.astimezone(timezone.utc).date()

            if day not in counts:

                continue

            role_key = str(role)

            if role_key not in counts[day]:

                counts[day][role_key] = 0

            counts[day][role_key] += 1



        return [

            RegistrationDayBucket(

                student=counts[day][UserType.STUDENT.value],

                teacher=counts[day][UserType.TEACHER.value],

                admin=counts[day][UserType.ADMIN.value],

            )

            for day in day_keys

        ]


