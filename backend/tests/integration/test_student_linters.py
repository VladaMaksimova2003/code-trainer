"""Docker integration smoke for all five student linters."""
from __future__ import annotations

import pytest

from infrastructure.execution.execution_guard import mark_worker_context
from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.language_loader import load_languages
from pathlib import Path

_LANGUAGES_DIR = Path(__file__).resolve().parents[2] / "languages"


@pytest.fixture(autouse=True)
def _setup() -> None:
    load_languages(_LANGUAGES_DIR)
    mark_worker_context()


@pytest.fixture
def core() -> ExecutionCore:
    instance = ExecutionCore()
    if not instance._docker.is_available():  # noqa: SLF001
        pytest.skip("Docker unavailable")
    return instance


@pytest.mark.integration
@pytest.mark.parametrize(
    ("language", "code", "needles"),
    [
        ("python", "print('x')\n", ("q000", "double quotes")),
        ("cpp", "int main(){undefined_x;return 0;}\n", ("undefined_x",)),
        ("java", "public class Main{public static void main(String[]a){undefined();}}\n", ("cannot find symbol", "undefined")),
        (
            "csharp",
            "class Program{static void Main(){foo();}}\n",
            ("foo", "does not exist", "CS0103"),
        ),
        ("pascal", "begin\n  writeln(n);\nend.\n", ("n", "identifier not found")),
    ],
)
def test_linter_reports_expected_issue(
    core: ExecutionCore, language: str, code: str, needles: tuple[str, ...]
) -> None:
    errors = core.lint(language, code)
    combined = "\n".join(errors).lower()
    assert errors, f"{language}: expected linter diagnostics, got {errors!r}"
    assert any(needle.lower() in combined for needle in needles), (
        f"{language}: {combined!r} missing any of {needles}"
    )
    for item in errors:
        assert item.startswith("Line "), f"{language}: unexpected format: {item!r}"
