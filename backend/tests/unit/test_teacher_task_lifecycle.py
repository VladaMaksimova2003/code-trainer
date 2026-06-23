from __future__ import annotations

from types import SimpleNamespace

import pytest

from application.tasks.services.catalog.teacher_task_lifecycle import retire_task
from shared.enums import AssignmentWorkflowStatus
from shared.exceptions import AccessDeniedToContentError, TaskNotFoundError


class FakeRelationRepo:
    def __init__(self) -> None:
        self.removed: list[int] = []

    def remove_all_for_task(self, task_id: int) -> None:
        self.removed.append(task_id)


class FakeSession:
    def __init__(self, task, submissions_count: int = 0) -> None:
        self.task = task
        self.submissions_count = submissions_count
        self.deleted = False
        self._relation_repo = FakeRelationRepo()

    def get(self, _model, task_id: int):
        if self.task is None or self.task.id != task_id:
            return None
        return self.task

    def scalar(self, _stmt):
        return self.submissions_count

    def flush(self) -> None:
        return None


@pytest.fixture(autouse=True)
def patch_relation_repo(monkeypatch):
    def factory(session):
        if not hasattr(session, "_relation_repo"):
            session._relation_repo = FakeRelationRepo()
        return session._relation_repo

    monkeypatch.setattr(
        "infrastructure.repositories.tasks.task_catalog.SqlAlchemyCatalogTaskRelationRepository",
        factory,
    )


def test_retire_task_deletes_when_no_submissions():
    task = SimpleNamespace(
        id=7,
        teacher_id=3,
        is_delete=False,
        workflow_status=AssignmentWorkflowStatus.ACTIVE.value,
    )
    session = FakeSession(task, submissions_count=0)

    result = retire_task(session, task_id=7, teacher_id=3)

    assert result.action == "deleted"
    assert result.submissions_count == 0
    assert task.is_delete is True
    assert session._relation_repo.removed == [7]


def test_retire_task_archives_when_submissions_exist():
    task = SimpleNamespace(
        id=8,
        teacher_id=3,
        is_delete=False,
        workflow_status=AssignmentWorkflowStatus.ACTIVE.value,
    )
    session = FakeSession(task, submissions_count=4)

    result = retire_task(session, task_id=8, teacher_id=3)

    assert result.action == "archived"
    assert result.submissions_count == 4
    assert task.is_delete is False
    assert task.workflow_status == AssignmentWorkflowStatus.ARCHIVED.value
    assert session._relation_repo.removed == []


def test_retire_task_rejects_foreign_teacher():
    task = SimpleNamespace(
        id=9,
        teacher_id=99,
        is_delete=False,
        workflow_status=AssignmentWorkflowStatus.ACTIVE.value,
    )
    session = FakeSession(task, submissions_count=0)

    with pytest.raises(AccessDeniedToContentError):
        retire_task(session, task_id=9, teacher_id=3)


def test_retire_task_not_found():
    session = FakeSession(None, submissions_count=0)

    with pytest.raises(TaskNotFoundError):
        retire_task(session, task_id=404, teacher_id=3)
