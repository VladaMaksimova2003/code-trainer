"""Unit tests for teacher task test-case gate before chapter placement."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from application.tasks.use_cases import validate_task_test_cases as module


def test_validate_requires_test_cases():
    row = SimpleNamespace(
        id=1,
        is_delete=False,
        test_cases=[],
        task_type="translation",
        code_examples={"python": "print(1)"},
        block_reorder_task=None,
        translation_task=None,
        flow_spec={},
    )
    db = MagicMock()
    db.get.return_value = row

    with pytest.raises(ValueError, match="тестовые случаи"):
        module.validate_task_test_cases_for_placement(
            db,
            task_id=1,
            placement_language="python",
            user_id="7",
        )


def test_validate_debug_uses_fixed_code_not_buggy(monkeypatch):
    row = SimpleNamespace(
        id=5,
        is_delete=False,
        test_cases=[{"inputs": "1", "output": "1"}],
        task_type="translation",
        code_examples={
            "python": "print('fixed')",
            "buggy_python": "print('buggy')",
            "curriculum_showcase": {
                "primary_action": "debug",
                "task_format": "исправление",
            },
        },
        block_reorder_task=None,
        translation_task=None,
        flow_spec={},
    )
    db = MagicMock()
    db.get.return_value = row

    submitted: dict[str, str] = {}

    class FakeJobService:
        def submit(self, **kwargs):
            submitted["code"] = kwargs["code"]
            return {"job_id": "job-1", "status": "QUEUED"}

        def get_result(self, job_id: str):
            return {
                "status": "SUCCESS",
                "validation": {
                    "correct": True,
                    "execution_results": [
                        {"case": 1, "status": "PASSED", "inputs": "1", "expected": "1", "actual": "1"}
                    ],
                },
            }

    monkeypatch.setattr(module, "ExecutionJobService", FakeJobService)

    module.validate_task_test_cases_for_placement(
        db,
        task_id=5,
        placement_language="python",
        user_id="7",
    )

    assert submitted["code"] == "print('fixed')"


def test_validate_reports_failed_test_case(monkeypatch):
    row = SimpleNamespace(
        id=6,
        is_delete=False,
        test_cases=[{"inputs": "", "output": "42"}],
        task_type="translation",
        code_examples={"python": "print(0)"},
        block_reorder_task=None,
        translation_task=None,
        flow_spec={},
    )
    db = MagicMock()
    db.get.return_value = row

    class FakeJobService:
        def submit(self, **_kwargs):
            return {"job_id": "job-2", "status": "QUEUED"}

        def get_result(self, job_id: str):
            return {
                "status": "SUCCESS",
                "validation": {
                    "correct": False,
                    "execution_results": [
                        {
                            "case": 1,
                            "status": "FAILED",
                            "inputs": "",
                            "expected": "42",
                            "actual": "0",
                            "message": "Wrong output",
                        }
                    ],
                },
            }

    monkeypatch.setattr(module, "ExecutionJobService", FakeJobService)

    with pytest.raises(ValueError, match="Тест 1"):
        module.validate_task_test_cases_for_placement(
            db,
            task_id=6,
            placement_language="python",
            user_id="7",
        )
