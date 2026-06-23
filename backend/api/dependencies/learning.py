from fastapi import Depends
from sqlalchemy.orm import Session

from api.dependencies.auth import SimpleUnitOfWork
from application.tasks.services.content_access_service import ContentAccessService
from application.learning.use_cases.assignment_sets import (
    CreateAssignmentSetUseCase,
    GetAssignmentSetUseCase,
    ListAccessibleAssignmentSetsUseCase,
    ListTeacherAssignmentSetsUseCase,
    ManageAssignmentSetItemsUseCase,
    UpdateAssignmentSetUseCase,
)
from application.learning.use_cases.groups.groups import (
    CreateGroupUseCase,
    DeleteGroupUseCase,
    GenerateInvitationCodeUseCase,
    JoinGroupByInvitationUseCase,
    ListStudentGroupsUseCase,
    ListTeacherGroupsUseCase,
)
from application.learning.services.student_progress import ListTeacherStudentsProgressUseCase
from application.learning.services.teacher_search import (
    GetTeacherPublicProfileUseCase,
    SearchTeachersUseCase,
)
from infrastructure.db.session import get_db
from infrastructure.repositories.learning.assignment_set import (
    SqlAlchemyAssignmentSetRepository,
)
from infrastructure.repositories.learning.group import SqlAlchemyGroupRepository
from infrastructure.repositories.learning.invitation_code import (
    SqlAlchemyInvitationCodeRepository,
)
from infrastructure.repositories.learning.teacher_search import (
    SqlAlchemyTeacherSearchRepository,
)


def get_content_access(db: Session = Depends(get_db)) -> ContentAccessService:
    return ContentAccessService(db)


def get_create_group_uc(db: Session = Depends(get_db)) -> CreateGroupUseCase:
    return CreateGroupUseCase(SqlAlchemyGroupRepository(db), SimpleUnitOfWork(db))


def get_delete_group_uc(db: Session = Depends(get_db)) -> DeleteGroupUseCase:
    return DeleteGroupUseCase(SqlAlchemyGroupRepository(db), SimpleUnitOfWork(db))


def get_list_teacher_groups_uc(db: Session = Depends(get_db)) -> ListTeacherGroupsUseCase:
    return ListTeacherGroupsUseCase(SqlAlchemyGroupRepository(db))


def get_list_student_groups_uc(db: Session = Depends(get_db)) -> ListStudentGroupsUseCase:
    return ListStudentGroupsUseCase(SqlAlchemyGroupRepository(db))


def get_generate_invitation_uc(db: Session = Depends(get_db)) -> GenerateInvitationCodeUseCase:
    return GenerateInvitationCodeUseCase(
        SqlAlchemyGroupRepository(db),
        SqlAlchemyInvitationCodeRepository(db),
        SimpleUnitOfWork(db),
    )


def get_join_group_uc(db: Session = Depends(get_db)) -> JoinGroupByInvitationUseCase:
    return JoinGroupByInvitationUseCase(
        SqlAlchemyGroupRepository(db),
        SqlAlchemyInvitationCodeRepository(db),
        SimpleUnitOfWork(db),
    )


def get_create_assignment_set_uc(db: Session = Depends(get_db)) -> CreateAssignmentSetUseCase:
    return CreateAssignmentSetUseCase(
        SqlAlchemyAssignmentSetRepository(db),
        SqlAlchemyGroupRepository(db),
        SimpleUnitOfWork(db),
    )


def get_update_assignment_set_uc(db: Session = Depends(get_db)) -> UpdateAssignmentSetUseCase:
    return UpdateAssignmentSetUseCase(
        SqlAlchemyAssignmentSetRepository(db), SimpleUnitOfWork(db)
    )


def get_list_teacher_sets_uc(db: Session = Depends(get_db)) -> ListTeacherAssignmentSetsUseCase:
    return ListTeacherAssignmentSetsUseCase(SqlAlchemyAssignmentSetRepository(db))


def get_list_accessible_sets_uc(db: Session = Depends(get_db)) -> ListAccessibleAssignmentSetsUseCase:
    return ListAccessibleAssignmentSetsUseCase(
        ContentAccessService(db), SqlAlchemyAssignmentSetRepository(db)
    )


def get_assignment_set_uc(db: Session = Depends(get_db)) -> GetAssignmentSetUseCase:
    return GetAssignmentSetUseCase(
        SqlAlchemyAssignmentSetRepository(db), ContentAccessService(db)
    )


def get_manage_set_items_uc(db: Session = Depends(get_db)) -> ManageAssignmentSetItemsUseCase:
    return ManageAssignmentSetItemsUseCase(
        SqlAlchemyAssignmentSetRepository(db), SimpleUnitOfWork(db)
    )


def get_search_teachers_uc(db: Session = Depends(get_db)) -> SearchTeachersUseCase:
    return SearchTeachersUseCase(SqlAlchemyTeacherSearchRepository(db))


def get_teacher_public_profile_uc(db: Session = Depends(get_db)) -> GetTeacherPublicProfileUseCase:
    return GetTeacherPublicProfileUseCase(
        SqlAlchemyTeacherSearchRepository(db),
        SqlAlchemyAssignmentSetRepository(db),
    )


def get_teacher_students_progress_uc(
    db: Session = Depends(get_db),
) -> ListTeacherStudentsProgressUseCase:
    return ListTeacherStudentsProgressUseCase(db, ContentAccessService(db))
