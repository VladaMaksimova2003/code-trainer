from types import SimpleNamespace

from application.learning.submission_analytics import task_constructions


def test_task_constructions_reads_code_examples_patterns():
    task = SimpleNamespace(
        id=99,
        constructions=[],
        code_examples={"patterns": ["for_loop", "if_statement", "io"]},
    )
    tags = task_constructions(None, task)
    assert "loop" in tags
    assert "condition" in tags
    assert "io" in tags
