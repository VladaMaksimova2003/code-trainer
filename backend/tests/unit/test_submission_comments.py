"""Unit tests for submission comment validation."""

import pytest

from application.learning.submission_comments_service import (
    MAX_COMMENT_LENGTH,
    _normalize_body,
    serialize_comment,
)
from infrastructure.db.models.learning.submission_comment import SubmissionComment
from infrastructure.db.models.user.user import User


def test_normalize_body_strips_and_accepts():
    assert _normalize_body("  hello  ") == "hello"


def test_normalize_body_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        _normalize_body("   ")


def test_normalize_body_rejects_too_long():
    with pytest.raises(ValueError, match=str(MAX_COMMENT_LENGTH)):
        _normalize_body("x" * (MAX_COMMENT_LENGTH + 1))


def test_serialize_comment_includes_teacher_name():
    teacher = User(name="Anna", email="a@t.local", password="hash", role="teacher")
    comment = SubmissionComment(
        submission_id=1,
        teacher_id=2,
        body="Nice work",
    )
    comment.id = 10
    comment.teacher = teacher
    payload = serialize_comment(comment)
    assert payload["teacher_name"] == "Anna"
    assert payload["body"] == "Nice work"
    assert payload["submission_id"] == 1
