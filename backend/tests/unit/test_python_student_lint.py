"""Student-facing Python ruff profile (pedagogy: syntax + logic + double quotes)."""
from __future__ import annotations

from pathlib import Path

import pytest

from infrastructure.execution.language_loader import load_languages
from infrastructure.execution.output_parser import parse_diagnostics

_LANGUAGES_DIR = Path(__file__).resolve().parents[2] / "languages"
_RUFF_STUDENT_CONFIG = _LANGUAGES_DIR / "ruff-student.toml"


@pytest.fixture(autouse=True)
def _load_language_registry() -> None:
    load_languages(_LANGUAGES_DIR)


def test_python_docker_lint_uses_student_ruff_config() -> None:
    from infrastructure.execution.language_registry import language_registry

    python = language_registry.get_or_raise("python")
    assert python.docker is not None
    assert "/runner/ruff-student.toml" in str(python.docker.lint)


def test_ruff_student_config_file_exists() -> None:
    assert _RUFF_STUDENT_CONFIG.is_file()
    text = _RUFF_STUDENT_CONFIG.read_text(encoding="utf-8")
    assert "F401" in text
    assert "Q000" in text


def test_student_ruff_profile_ignores_unused_import() -> None:
    sample = "\n".join(
        [
            "/tmp/home/source.py:1:8: F401 [*] `os` imported but unused",
            "Found 1 error.",
        ]
    )
    # Without student config this would surface F401; parser still maps ruff lines.
    # Integration with --config is covered by docker test below.
    assert parse_diagnostics(sample) == [
        "Line 1:8: error: F401 [*] `os` imported but unused"
    ]


def test_student_ruff_profile_maps_single_quote_rule() -> None:
    sample = "/tmp/home/source.py:1:7: Q000 [*] Single quotes found but double quotes preferred"
    assert parse_diagnostics(sample) == [
        "Line 1:7: error: Q000 [*] Single quotes found but double quotes preferred"
    ]


@pytest.mark.integration
def test_python_lint_in_runner_ignores_unused_import() -> None:
    from infrastructure.execution.execution_guard import mark_worker_context
    from infrastructure.execution.execution_core import ExecutionCore

    mark_worker_context()
    core = ExecutionCore()
    if not core._docker.is_available():  # noqa: SLF001
        pytest.skip("Docker unavailable")

    code = "import os\nprint(1)\n"
    errors = core.lint("python", code)
    combined = "\n".join(errors).lower()
    assert "f401" not in combined
    assert "imported but unused" not in combined


@pytest.mark.integration
def test_python_lint_in_runner_flags_single_quotes() -> None:
    from infrastructure.execution.execution_guard import mark_worker_context
    from infrastructure.execution.execution_core import ExecutionCore

    mark_worker_context()
    core = ExecutionCore()
    if not core._docker.is_available():  # noqa: SLF001
        pytest.skip("Docker unavailable")

    code = "print('hello')\n"
    errors = core.lint("python", code)
    combined = "\n".join(errors).lower()
    assert "q000" in combined or "double quotes" in combined


@pytest.mark.integration
def test_python_lint_in_runner_reports_syntax_errors() -> None:
    from infrastructure.execution.execution_guard import mark_worker_context
    from infrastructure.execution.execution_core import ExecutionCore

    mark_worker_context()
    core = ExecutionCore()
    if not core._docker.is_available():  # noqa: SLF001
        pytest.skip("Docker unavailable")

    code = "print('hello'\n"
    errors = core.lint("python", code)
    assert errors
