"""Block-reorder: wrong order returns immediately; tests run only when structure matches."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from application.execution.block_reorder_validation import (
    enqueue_block_reorder_execution,
    validate_block_reorder_structural,
)
from worker import execution_handlers


class _FakeRelation:
    blocks = ["a", "b"]
    language = "python"
    template = None


class _FakeEntity:
    template = None
    language = "python"
    blocks = ["a", "b"]

    def _get_variant(self, language):
        return {"blocks": self.blocks, "correct_order": [0, 1], "template": None}

    def validate_answer(self, order, language=None):
        return list(order) == [0, 1]

    def validate_partial(self, order, language=None):
        return [True, True] if list(order) == [0, 1] else [False, False]

    def build_code(self, order, language=None, indents=None):
        return "\n".join(self.blocks[i] for i in order)

    @staticmethod
    def _template_has_slots(template):
        return False


class _FakeTask:
    id = 2
    task_type = "task_build_from_blocks"
    test_cases = [{"inputs": "1", "output": "1"}]
    block_reorder_task = _FakeRelation()


@pytest.fixture
def fake_db(monkeypatch):
    task = _FakeTask()
    entity = _FakeEntity()

    monkeypatch.setattr(
        "application.execution.block_reorder_validation.build_entity_from_db",
        lambda task, relation: entity,
    )
    monkeypatch.setattr(
        "application.execution.block_reorder_validation.is_build_from_blocks_task_type",
        lambda task_type: True,
    )

    class _Query:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return task

    class _Db:
        def query(self, model):
            return _Query()

    return _Db()


def test_validate_wrong_blocks_skips_execution(fake_db):
    result = validate_block_reorder_structural(
        fake_db,
        task_id=2,
        order=[1, 0],
        assembled_code="b\na",
    )

    assert result is not None
    assert result["structural_correct"] is False
    assert result["needs_execution"] is False
    assert "тесты не запускались" in result["message"].lower()


def test_enqueue_skips_job_when_structural_wrong(fake_db, monkeypatch):
    structural = validate_block_reorder_structural(
        fake_db,
        task_id=2,
        order=[1, 0],
        assembled_code="b\na",
    )
    submits: list[dict] = []

    class _FakeJobService:
        def submit(self, **kwargs):
            submits.append(kwargs)
            return {"job_id": "job-1", "status": "QUEUED"}

    monkeypatch.setattr(
        "application.execution.block_reorder_validation.ExecutionJobService",
        _FakeJobService,
    )

    result = enqueue_block_reorder_execution(structural, user_id="u1")

    assert submits == []
    assert result["execution_job_id"] is None
    assert result["status"] == "NOT_REQUIRED"
    assert result["correct"] is False


def test_worker_handler_runs_tests_when_structural_wrong(monkeypatch):
    run_calls: list[tuple] = []

    monkeypatch.setattr(
        "worker.execution_handlers._core.run_tests",
        lambda lang, code, cases: run_calls.append((lang, code, cases)) or [],
    )
    monkeypatch.setattr(
        "application.execution.pipeline_runner.WorkerPipelineRunner._run_expected_concept_checks",
        lambda self, db, task_id, code, lang: [],
    )

    job = SimpleNamespace(
        payload={
            "structural": {
                "structural_correct": False,
                "message": "Incorrect block assembly",
                "task_id": 2,
            },
            "mode": "tests",
        },
        test_cases=[{"inputs": "1", "output": "1"}],
        code="broken",
        language_id="cpp",
        task_id=2,
    )

    result = execution_handlers.handle_block_reorder_validate(job)

    assert len(run_calls) == 1
    assert result["correct"] is False
