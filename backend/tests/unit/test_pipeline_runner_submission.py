"""Worker pipeline submission checks (compile + tests)."""

from __future__ import annotations

from application.execution.pipeline_runner import WorkerPipelineRunner


def test_run_submission_runs_tests_for_psk_01_style_program():
    runner = WorkerPipelineRunner()
    code = (
        "program Demo;\n"
        "begin\n"
        "   writeln('step 1');\n"
        "end.\n"
    )
    result = runner.run_submission(103, code, "pascal")

    assert result["pattern_errors"] == []
    assert result["compiler_errors"] == []
    assert len(result["test_results"]) >= 1
    assert all(item["status"] == "FAILED" for item in result["test_results"])


def test_run_lint_only_reports_syntax_error():
    runner = WorkerPipelineRunner()
    code = (
        "program Demo;\n"
        "begin\n"
        "  x = 1;\n"
        "end.\n"
    )
    result = runner.run_lint_only(103, code, "pascal")

    assert result["linter_errors"], result


def test_run_full_delegates_to_run_submission(monkeypatch):
    runner = WorkerPipelineRunner()
    captured: dict[str, object] = {}

    def fake_run_submission(task_id, code, language):
        captured["args"] = (task_id, code, language)
        return {
            "success": False,
            "pattern_errors": [{"type": "TRANSFER_PITFALL", "transfer_type": "FCC"}],
            "test_results": [{"case": 1, "status": "FAILED"}],
        }

    monkeypatch.setattr(runner, "run_submission", fake_run_submission)
    result = runner.run_full(4, "program T; begin end.", "pascal")

    assert captured["args"] == (4, "program T; begin end.", "pascal")
    assert result["pattern_errors"][0]["type"] == "TRANSFER_PITFALL"
