"""Shared pytest hooks and marker auto-tagging."""

from __future__ import annotations

from pathlib import Path

import pytest

# Filename fragments for course/showcase regression suites (slow, content-heavy).
_CURRICULUM_NAME_FRAGMENTS = (
    "course_v311",
    "showcase",
    "curriculum_v2",
    "chapter_task_display",
    "python_course",
    "curriculum_next",
    "curriculum_collection",
    "curriculum_chapter",
    "curriculum_slot",
    "pascal_full",
    "pascal_conditions",
    "pascal_loops",
    "pascal_flowchart",
    "cpp_showcase",
    "seed_teacher",
    "test_curriculum.py",
)


def _is_curriculum_test(path: Path) -> bool:
    name = path.name
    if name == "test_curriculum.py":
        return True
    return any(fragment in name for fragment in _CURRICULUM_NAME_FRAGMENTS)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        path = Path(str(item.fspath))
        rel = path.as_posix()

        if "/integration/" in rel or rel.startswith("integration/"):
            item.add_marker(pytest.mark.integration)

        if "/unit/curriculum/" in rel or _is_curriculum_test(path):
            item.add_marker(pytest.mark.curriculum)

        if "docker" in item.name or "warm_runner" in rel or "execution" in rel:
            if "warm_runner_security" in rel or "docker_executor" in rel:
                item.add_marker(pytest.mark.docker)
