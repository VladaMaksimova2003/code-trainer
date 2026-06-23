"""Submission comments — teacher feedback on student homework."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, joinedload

from application.learning.submission_analytics import teacher_group_student_ids
from application.support import notifications_service
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.learning.submission_comment import SubmissionComment
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user import User
from shared.enums import NotificationKind

MAX_COMMENT_LENGTH = 4096


class SubmissionCommentAccessError(PermissionError):
    pass


class SubmissionCommentNotFoundError(LookupError):
    pass


def _normalize_body(body: str) -> str:
    text = (body or "").strip()
    if not text:
        raise ValueError("Comment body cannot be empty.")
    if len(text) > MAX_COMMENT_LENGTH:
        raise ValueError(f"Comment body must be at most {MAX_COMMENT_LENGTH} characters.")
    return text


def _get_submission(db: Session, submission_id: int) -> Submission | None:
    return db.get(Submission, submission_id)


def assert_teacher_can_access_submission(
    db: Session,
    teacher_id: int,
    submission_id: int,
) -> Submission:
    submission = _get_submission(db, submission_id)
    if submission is None or submission.user_id is None:
        raise SubmissionCommentNotFoundError("Submission not found")

    allowed_students = teacher_group_student_ids(db, teacher_id)
    if submission.user_id not in allowed_students:
        raise SubmissionCommentAccessError("Student is not in your groups")

    task = db.get(TaskModel, submission.task_id)
    if task is None or task.teacher_id != teacher_id:
        raise SubmissionCommentAccessError("Task does not belong to this teacher")

    return submission


def assert_student_can_view_submission(
    db: Session,
    student_id: int,
    submission_id: int,
) -> Submission:
    submission = _get_submission(db, submission_id)
    if submission is None or submission.user_id != student_id:
        raise SubmissionCommentAccessError("You do not have access to this submission")
    return submission


def serialize_comment(comment: SubmissionComment) -> dict[str, Any]:
    teacher_name = comment.teacher.name if comment.teacher else None
    return {
        "id": comment.id,
        "submission_id": comment.submission_id,
        "teacher_id": comment.teacher_id,
        "teacher_name": teacher_name,
        "body": comment.body,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
    }


def list_submission_comments(
    db: Session,
    submission_id: int,
) -> list[dict[str, Any]]:
    rows = (
        db.query(SubmissionComment)
        .options(joinedload(SubmissionComment.teacher))
        .filter(SubmissionComment.submission_id == submission_id)
        .order_by(SubmissionComment.created_at.asc())
        .all()
    )
    return [serialize_comment(row) for row in rows]


def create_submission_comment(
    db: Session,
    *,
    teacher_id: int,
    submission_id: int,
    body: str,
) -> dict[str, Any]:
    submission = assert_teacher_can_access_submission(db, teacher_id, submission_id)
    normalized_body = _normalize_body(body)
    comment = SubmissionComment(
        submission_id=submission_id,
        teacher_id=teacher_id,
        body=normalized_body,
    )
    db.add(comment)

    if submission.user_id is not None:
        teacher = db.get(User, teacher_id)
        task = db.get(TaskModel, submission.task_id)
        teacher_name = (teacher.name or "Преподаватель").strip()
        task_title = (task.title if task else f"задача #{submission.task_id}").strip()
        notifications_service.create_notification(
            db,
            user_id=int(submission.user_id),
            kind=NotificationKind.COMMENT,
            title=f"{teacher_name} · {task_title}",
            body=normalized_body,
            task_id=int(submission.task_id),
            submission_id=int(submission_id),
        )

    db.commit()
    db.refresh(comment)
    comment.teacher = db.get(User, teacher_id)
    return serialize_comment(comment)


def update_submission_comment(
    db: Session,
    *,
    teacher_id: int,
    submission_id: int,
    comment_id: int,
    body: str,
) -> dict[str, Any]:
    assert_teacher_can_access_submission(db, teacher_id, submission_id)
    comment = (
        db.query(SubmissionComment)
        .options(joinedload(SubmissionComment.teacher))
        .filter(
            SubmissionComment.id == comment_id,
            SubmissionComment.submission_id == submission_id,
        )
        .one_or_none()
    )
    if comment is None:
        raise SubmissionCommentNotFoundError("Comment not found")
    if comment.teacher_id != teacher_id:
        raise SubmissionCommentAccessError("You can only edit your own comments")

    comment.body = _normalize_body(body)
    db.commit()
    db.refresh(comment)
    return serialize_comment(comment)


def delete_submission_comment(
    db: Session,
    *,
    teacher_id: int,
    submission_id: int,
    comment_id: int,
) -> None:
    assert_teacher_can_access_submission(db, teacher_id, submission_id)
    comment = (
        db.query(SubmissionComment)
        .filter(
            SubmissionComment.id == comment_id,
            SubmissionComment.submission_id == submission_id,
        )
        .one_or_none()
    )
    if comment is None:
        raise SubmissionCommentNotFoundError("Comment not found")
    if comment.teacher_id != teacher_id:
        raise SubmissionCommentAccessError("You can only delete your own comments")
    db.delete(comment)
    db.commit()
