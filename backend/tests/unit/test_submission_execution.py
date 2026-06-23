"""Unit tests for submission-first execution flow."""

from application.execution.submission_serializer import submission_to_solution_payload


def test_submission_to_solution_payload_maps_fields():
    class _Result:
        case_number = 1
        status = "PASSED"
        inputs = "1"
        expected = "1"
        actual = "1"
        message = "ok"

    class _Submission:
        id = 42
        user_id = 7
        task_id = 10
        language = "python"
        status = "done"
        success = True
        created_at = None
        updated_at = None
        linter_errors = []
        pattern_errors = []
        test_results = [_Result()]

    payload = submission_to_solution_payload(_Submission())
    assert payload["submission_id"] == 42
    assert payload["task_id"] == 10
    assert payload["success"] is True
    assert payload["status"] == "done"
    assert len(payload["test_results"]) == 1


def test_submission_dedup_keys_are_unique_per_submission():
    op = "process_submission"
    assert f"submission:{1}:{op}" != f"submission:{2}:{op}"
