"""Unit tests for support tickets."""

import pytest

from application.support.support_service import (
    MAX_BODY_LENGTH,
    SupportTicketValidationError,
    _normalize_body,
    _normalize_subject,
    _parse_category,
    _resolve_routing,
)
from application.support.templates import get_support_templates
from shared.enums import SupportTicketCategory, SupportTicketTarget


def test_normalize_body_accepts_nonempty():
    assert _normalize_body("x") == "x"


def test_normalize_body_rejects_empty():
    with pytest.raises(SupportTicketValidationError, match="empty"):
        _normalize_body("")
    with pytest.raises(SupportTicketValidationError, match="empty"):
        _normalize_body("   ")


def test_normalize_body_rejects_long():
    with pytest.raises(SupportTicketValidationError, match=str(MAX_BODY_LENGTH)):
        _normalize_body("x" * (MAX_BODY_LENGTH + 1))


def test_parse_category():
    assert _parse_category("task_content") == SupportTicketCategory.TASK_CONTENT
    with pytest.raises(SupportTicketValidationError):
        _parse_category("unknown")


def test_resolve_routing_task_to_teacher():
    class FakeTask:
        teacher_id = 42

    target, assignee = _resolve_routing(SupportTicketCategory.TASK_CONTENT, FakeTask())
    assert target == SupportTicketTarget.TEACHER
    assert assignee == 42


def test_resolve_routing_technical_to_admin():
    target, assignee = _resolve_routing(SupportTicketCategory.TECHNICAL, None)
    assert target == SupportTicketTarget.ADMIN
    assert assignee is None


def test_resolve_routing_task_without_teacher_to_admin():
    class FakeTask:
        teacher_id = None

    target, assignee = _resolve_routing(SupportTicketCategory.TASK_CONTENT, FakeTask())
    assert target == SupportTicketTarget.ADMIN
    assert assignee is None


def test_normalize_subject_with_task():
    class FakeTask:
        title = "Loops"

    subject = _normalize_subject(None, SupportTicketCategory.TASK_CONTENT, FakeTask())
    assert "Loops" in subject


def test_templates_task_context_student():
    payload = get_support_templates(role="student", context="task")
    ids = [item["id"] for item in payload["categories"]]
    assert "task_content" in ids
    assert "autograder" in ids
    assert "technical" in ids


def test_templates_teacher_general():
    payload = get_support_templates(role="teacher", context="general")
    ids = [item["id"] for item in payload["categories"]]
    assert "technical" in ids
    assert "task_content" not in ids
