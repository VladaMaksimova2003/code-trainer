from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.analytics.schemas.responses import (
    StudentAnalyticsResponse,
    TeacherAnalyticsResponse,
    TeacherSubmissionDetailResponse,
    TeacherSubmissionsListResponse,
)
from api.analytics.schemas.submission_comments import (
    SubmissionCommentCreateRequest,
    SubmissionCommentListResponse,
    SubmissionCommentResponse,
    SubmissionCommentUpdateRequest,
)
from api.dependencies.authorization import require_permission
from application.learning import analytics_service
from application.learning.recommendations import get_student_recommendations
from application.learning import submission_comments_service as comments_service
from application.learning.submission_comments_service import (
    SubmissionCommentAccessError,
    SubmissionCommentNotFoundError,
)
from application.users import student_service
from application.learning.use_cases.groups.dashboard import (
    get_teacher_submission_detail as fetch_teacher_submission_detail,
)
from application.users.services.teacher_service import get_teacher_user_or_404
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db

router = APIRouter()


def _comment_http_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, SubmissionCommentNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, SubmissionCommentAccessError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    raise exc


@router.get("/student/analytics", response_model=StudentAnalyticsResponse)
def get_student_analytics(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
):
    try:
        student_service.ensure_student(user, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        ) from None
    return analytics_service.build_student_analytics(db, user)


@router.get("/student/recommendations")
def get_student_recommendations_endpoint(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
):
    try:
        student_service.ensure_student(user, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        ) from None
    return get_student_recommendations(db, user.id)


@router.get("/teacher/submissions", response_model=TeacherSubmissionsListResponse)
def get_teacher_submissions(
    task_id: int | None = None,
    student_id: int | None = None,
    group_id: int | None = None,
    catalog_id: int | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    teacher_id = user.id
    try:
        get_teacher_user_or_404(db, teacher_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        ) from None
    items = analytics_service.list_teacher_submissions(
        db,
        teacher_id,
        task_id=task_id,
        student_id=student_id,
        group_id=group_id,
        catalog_id=catalog_id,
        limit=limit,
    )
    return {"items": items, "count": len(items)}


@router.get(
    "/teacher/submissions/{submission_id}",
    response_model=TeacherSubmissionDetailResponse,
)
def get_teacher_submission_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    try:
        get_teacher_user_or_404(db, user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        ) from None
    detail = fetch_teacher_submission_detail(db, user.id, submission_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or access denied",
        )
    return detail


@router.get("/teacher/analytics", response_model=TeacherAnalyticsResponse)
def get_teacher_analytics(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    teacher_id = user.id
    try:
        get_teacher_user_or_404(db, teacher_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        ) from None
    return analytics_service.build_teacher_analytics(db, teacher_id)


@router.get(
    "/teacher/submissions/{submission_id}/comments",
    response_model=SubmissionCommentListResponse,
)
def list_teacher_submission_comments(
    submission_id: int,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    try:
        get_teacher_user_or_404(db, user.id)
        comments_service.assert_teacher_can_access_submission(db, user.id, submission_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found") from None
    except (SubmissionCommentNotFoundError, SubmissionCommentAccessError) as exc:
        raise _comment_http_errors(exc) from exc

    items = comments_service.list_submission_comments(db, submission_id)
    return {"items": items, "count": len(items)}


@router.post(
    "/teacher/submissions/{submission_id}/comments",
    response_model=SubmissionCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_teacher_submission_comment(
    submission_id: int,
    payload: SubmissionCommentCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    try:
        get_teacher_user_or_404(db, user.id)
        return comments_service.create_submission_comment(
            db,
            teacher_id=user.id,
            submission_id=submission_id,
            body=payload.body,
        )
    except ValueError as exc:
        if str(exc) == "Teacher not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found") from exc
        raise _comment_http_errors(exc) from exc
    except (SubmissionCommentNotFoundError, SubmissionCommentAccessError) as exc:
        raise _comment_http_errors(exc) from exc


@router.patch(
    "/teacher/submissions/{submission_id}/comments/{comment_id}",
    response_model=SubmissionCommentResponse,
)
def update_teacher_submission_comment(
    submission_id: int,
    comment_id: int,
    payload: SubmissionCommentUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    try:
        get_teacher_user_or_404(db, user.id)
        return comments_service.update_submission_comment(
            db,
            teacher_id=user.id,
            submission_id=submission_id,
            comment_id=comment_id,
            body=payload.body,
        )
    except ValueError as exc:
        if str(exc) == "Teacher not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found") from exc
        raise _comment_http_errors(exc) from exc
    except (SubmissionCommentNotFoundError, SubmissionCommentAccessError) as exc:
        raise _comment_http_errors(exc) from exc


@router.delete(
    "/teacher/submissions/{submission_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_teacher_submission_comment(
    submission_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
):
    try:
        get_teacher_user_or_404(db, user.id)
        comments_service.delete_submission_comment(
            db,
            teacher_id=user.id,
            submission_id=submission_id,
            comment_id=comment_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found") from exc
    except (SubmissionCommentNotFoundError, SubmissionCommentAccessError) as exc:
        raise _comment_http_errors(exc) from exc
    return None


@router.get(
    "/student/submissions/{submission_id}/comments",
    response_model=SubmissionCommentListResponse,
)
def list_student_submission_comments(
    submission_id: int,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
):
    try:
        student_service.ensure_student(user, db)
        comments_service.assert_student_can_view_submission(db, user.id, submission_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found") from None
    except SubmissionCommentAccessError as exc:
        raise _comment_http_errors(exc) from exc

    items = comments_service.list_submission_comments(db, submission_id)
    return {"items": items, "count": len(items)}
