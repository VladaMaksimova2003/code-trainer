"""Unit-test fixtures shared across backend/tests/unit."""

from __future__ import annotations

import os
from contextlib import ExitStack
from unittest.mock import patch

import pytest

from shared.config import CurriculumSettings, Settings

_CATALOG_SYNC_PATCH_TARGETS = (
    "application.curriculum.catalog_sync_policy.is_catalog_sync_enabled",
)


@pytest.fixture(autouse=True)
def _enable_catalog_sync_for_unit_tests():
    """Showcase/curriculum unit tests assume catalog file sync is enabled."""
    with ExitStack() as stack:
        for target in _CATALOG_SYNC_PATCH_TARGETS:
            stack.enter_context(patch(target, return_value=True))
        stack.enter_context(
            patch(
                "application.curriculum.catalog_sync_policy.get_settings",
                return_value=Settings(curriculum=CurriculumSettings(catalog_sync_enabled=True)),
            )
        )
        yield


@pytest.fixture(autouse=True)
def _allow_worker_execution_in_pipeline_tests(request: pytest.FixtureRequest):
    """Pipeline runner unit tests execute code in-process."""
    if "test_pipeline_runner_submission" not in request.node.nodeid:
        yield
        return
    previous = os.environ.get("EXECUTION_WORKER")
    os.environ["EXECUTION_WORKER"] = "1"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("EXECUTION_WORKER", None)
        else:
            os.environ["EXECUTION_WORKER"] = previous
