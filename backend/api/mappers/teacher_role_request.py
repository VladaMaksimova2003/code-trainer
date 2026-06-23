from api.auth.teacher_role_schemas import TeacherRoleRequestResponse
from domain.entities.users.teacher_role_request import TeacherRoleRequest


def to_teacher_role_request_response(
    entity: TeacherRoleRequest,
) -> TeacherRoleRequestResponse:
    return TeacherRoleRequestResponse(
        id=entity.id,
        user_id=entity.user_id,
        user_name=entity.user_name,
        user_email=entity.user_email,
        status=entity.status.value,
        message=entity.message,
        created_at=entity.created_at,
        reviewed_at=entity.reviewed_at,
        reviewed_by_id=entity.reviewed_by_id,
    )
