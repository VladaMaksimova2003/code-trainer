from api.learning.schemas import (
    AssignmentSetItemResponse,
    AssignmentSetResponse,
    GroupResponse,
    InvitationCodeResponse,
    StudentProgressItemResponse,
    TeacherSearchResultResponse,
)
from shared.interfaces.repositories.learning.teacher_search import TeacherSearchResult
from domain.entities.tasks.assignment_set import AssignmentSet
from domain.entities.learning.group import Group
from domain.entities.users.invitation_code import InvitationCode


def to_group(g: Group) -> GroupResponse:
    return GroupResponse(
        id=g.id,
        name=g.name,
        teacher_id=g.teacher_id,
        created_at=g.created_at,
    )


def to_invitation(inv: InvitationCode) -> InvitationCodeResponse:
    return InvitationCodeResponse(
        id=inv.id,
        code=inv.code,
        group_id=inv.group_id,
        max_uses=inv.max_uses,
        use_count=inv.use_count,
        expires_at=inv.expires_at,
        is_active=inv.is_active,
    )


def to_assignment_set(
    s: AssignmentSet,
    *,
    total_tasks: int | None = None,
    solved_count: int | None = None,
) -> AssignmentSetResponse:
    item_count = len(s.items)
    resolved_total = item_count if total_tasks is None else total_tasks
    resolved_solved = 0 if solved_count is None else solved_count
    return AssignmentSetResponse(
        id=s.id,
        name=s.name,
        description=s.description,
        teacher_id=s.teacher_id,
        visibility=s.visibility.value,
        group_id=s.group_id,
        is_archived=s.is_archived,
        items=[
            AssignmentSetItemResponse(
                task_id=i.task_id,
                sort_order=i.sort_order,
                topic=i.topic,
            )
            for i in s.items
        ],
        total_tasks=resolved_total,
        solved_count=resolved_solved,
        created_at=s.created_at,
        deadline_at=s.deadline_at,
    )


def to_teacher_search(r: TeacherSearchResult) -> TeacherSearchResultResponse:
    return TeacherSearchResultResponse(
        user_id=r.user_id,
        full_name=r.full_name,
        bio=r.bio,
        languages=r.languages,
        specialization=r.specialization,
        assignment_count=r.assignment_count,
        assignment_set_count=r.assignment_set_count,
    )


def to_student_progress(row: dict) -> StudentProgressItemResponse:
    return StudentProgressItemResponse(
        student_id=row["student_id"],
        total_submissions=row["total_submissions"],
        successful_submissions=row["successful_submissions"],
    )
