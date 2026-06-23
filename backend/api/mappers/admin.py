from api.admin.schemas import (
    AdminAssignmentListItemResponse,
    AdminAssignmentVersionResponse,
    AdminUserDetailResponse,
    AdminUserListItemResponse,
    RegistrationDayBucketResponse,
    SystemStatisticsResponse,
)
from shared.interfaces.repositories.admin.admin_task import (
    AdminAssignmentListItem,
    AdminAssignmentVersionItem,
)
from shared.interfaces.repositories.admin.admin_user import (
    AdminUserDetail,
    AdminUserListItem,
)
from shared.interfaces.repositories.admin.admin_statistics import SystemStatistics


def to_user_list_item(item: AdminUserListItem) -> AdminUserListItemResponse:
    return AdminUserListItemResponse(
        id=item.id,
        name=item.name,
        email=item.email,
        roles=item.roles,
        is_blocked=item.is_blocked,
        is_deleted=item.is_deleted,
        created_at=item.created_at,
    )


def to_user_detail(item: AdminUserDetail) -> AdminUserDetailResponse:
    return AdminUserDetailResponse(
        id=item.id,
        name=item.name,
        email=item.email,
        roles=item.roles,
        is_blocked=item.is_blocked,
        is_deleted=item.is_deleted,
        created_at=item.created_at,
        total_submissions=item.total_submissions,
        successful_submissions=item.successful_submissions,
        solved_tasks_count=item.solved_tasks_count,
        last_login_at=item.last_login_at,
        created_tasks_count=item.created_tasks_count,
        created_catalogs_count=item.created_catalogs_count,
        groups_count=item.groups_count,
        about=item.about,
        success_rate=item.success_rate,
        streak_days=item.streak_days,
        member_groups_count=item.member_groups_count,
        member_group_names=item.member_group_names or [],
    )


def to_assignment_item(item: AdminAssignmentListItem) -> AdminAssignmentListItemResponse:
    return AdminAssignmentListItemResponse(
        id=item.id,
        title=item.title,
        task_type=item.task_type,
        difficulty=item.difficulty,
        teacher_id=item.teacher_id,
        version=item.version,
        workflow_status=item.workflow_status,
        is_delete=item.is_delete,
        collection_title=item.collection_title,
        chapter_title=item.chapter_title,
        chapter_key=item.chapter_key,
        language=item.language,
        chapter_slug=item.chapter_slug,
        teacher_name=item.teacher_name,
        teacher_email=item.teacher_email,
        teacher_is_deleted=item.teacher_is_deleted,
    )


def to_version_item(item: AdminAssignmentVersionItem) -> AdminAssignmentVersionResponse:
    return AdminAssignmentVersionResponse(
        id=item.id,
        task_id=item.task_id,
        version_number=item.version_number,
        title=item.title,
        is_active=item.is_active,
        created_at=item.created_at,
    )


def to_statistics(stats: SystemStatistics) -> SystemStatisticsResponse:
    registrations_by_period = {
        period: [
            RegistrationDayBucketResponse(
                student=bucket.student,
                teacher=bucket.teacher,
                admin=bucket.admin,
            )
            for bucket in buckets
        ]
        for period, buckets in stats.registrations_by_period.items()
    }
    return SystemStatisticsResponse(
        users_total=stats.users_total,
        users_by_role=stats.users_by_role,
        assignments_total=stats.assignments_total,
        curriculum_catalog_tasks=stats.curriculum_catalog_tasks,
        assignments_by_status=stats.assignments_by_status,
        submissions_total=stats.submissions_total,
        submissions_successful=stats.submissions_successful,
        solved_assignments_count=stats.solved_assignments_count,
        teacher_requests_pending=stats.teacher_requests_pending,
        registrations_by_period=registrations_by_period,
        users_new_last_month=stats.users_new_last_month,
        users_new_last_month_by_role=dict(stats.users_new_last_month_by_role),
        tasks_new_last_30_days=stats.tasks_new_last_30_days,
    )
