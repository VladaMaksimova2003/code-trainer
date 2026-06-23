"""Dependency injection for admin use cases."""

from fastapi import Depends
from sqlalchemy.orm import Session

from api.dependencies.auth import SimpleUnitOfWork
from application.admin.assignments import (
    ActivateAssignmentVersionUseCase,
    ArchiveAssignmentUseCase,
    CreateAssignmentVersionUseCase,
    ListAssignmentVersionsUseCase,
    ListAssignmentsUseCase,
    SetAssignmentWorkflowStatusUseCase,
)
from application.admin.roles import (
    AssignRoleToUserUseCase,
    RemoveRoleFromUserUseCase,
)
from application.admin.statistics import GetSystemStatisticsUseCase
from application.admin.users import (
    DeleteUserUseCase,
    GetUserDetailUseCase,
    ListUsersUseCase,
    SetUserBlockedUseCase,
)
from infrastructure.db.session import get_db
from infrastructure.repositories.admin.admin_statistics import (
    SqlAlchemyAdminStatisticsRepository,
)
from infrastructure.repositories.tasks.admin_task import SqlAlchemyAdminTaskRepository
from infrastructure.repositories.admin.admin_user import SqlAlchemyAdminUserRepository
from infrastructure.repositories.users.user import SqlAlchemyUsersRepository
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository


def get_list_users_uc(db: Session = Depends(get_db)) -> ListUsersUseCase:
    return ListUsersUseCase(SqlAlchemyAdminUserRepository(db), SimpleUnitOfWork(db))


def get_user_detail_uc(db: Session = Depends(get_db)) -> GetUserDetailUseCase:
    return GetUserDetailUseCase(SqlAlchemyAdminUserRepository(db), SimpleUnitOfWork(db))


def get_set_user_blocked_uc(db: Session = Depends(get_db)) -> SetUserBlockedUseCase:
    return SetUserBlockedUseCase(SqlAlchemyAdminUserRepository(db), SimpleUnitOfWork(db))


def get_delete_user_uc(db: Session = Depends(get_db)) -> DeleteUserUseCase:
    return DeleteUserUseCase(SqlAlchemyAdminUserRepository(db), SimpleUnitOfWork(db))


def get_assign_role_uc(db: Session = Depends(get_db)) -> AssignRoleToUserUseCase:
    return AssignRoleToUserUseCase(
        SqlAlchemyUsersRepository(db),
        SqlAlchemyUserRoleRepository(db),
        SimpleUnitOfWork(db),
    )


def get_remove_role_uc(db: Session = Depends(get_db)) -> RemoveRoleFromUserUseCase:
    return RemoveRoleFromUserUseCase(SqlAlchemyUserRoleRepository(db), SimpleUnitOfWork(db))


def get_list_assignments_uc(db: Session = Depends(get_db)) -> ListAssignmentsUseCase:
    return ListAssignmentsUseCase(SqlAlchemyAdminTaskRepository(db), SimpleUnitOfWork(db))


def get_set_assignment_status_uc(
    db: Session = Depends(get_db),
) -> SetAssignmentWorkflowStatusUseCase:
    return SetAssignmentWorkflowStatusUseCase(
        SqlAlchemyAdminTaskRepository(db), SimpleUnitOfWork(db)
    )


def get_archive_assignment_uc(db: Session = Depends(get_db)) -> ArchiveAssignmentUseCase:
    return ArchiveAssignmentUseCase(SqlAlchemyAdminTaskRepository(db), SimpleUnitOfWork(db))


def get_list_versions_uc(db: Session = Depends(get_db)) -> ListAssignmentVersionsUseCase:
    return ListAssignmentVersionsUseCase(
        SqlAlchemyAdminTaskRepository(db), SimpleUnitOfWork(db)
    )


def get_create_version_uc(db: Session = Depends(get_db)) -> CreateAssignmentVersionUseCase:
    return CreateAssignmentVersionUseCase(
        SqlAlchemyAdminTaskRepository(db), SimpleUnitOfWork(db)
    )


def get_activate_version_uc(
    db: Session = Depends(get_db),
) -> ActivateAssignmentVersionUseCase:
    return ActivateAssignmentVersionUseCase(
        SqlAlchemyAdminTaskRepository(db), SimpleUnitOfWork(db)
    )


def get_statistics_uc(db: Session = Depends(get_db)) -> GetSystemStatisticsUseCase:
    return GetSystemStatisticsUseCase(
        SqlAlchemyAdminStatisticsRepository(db), SimpleUnitOfWork(db)
    )
