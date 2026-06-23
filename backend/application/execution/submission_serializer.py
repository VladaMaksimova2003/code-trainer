"""Serialize submission ORM rows for API responses."""
from __future__ import annotations

from infrastructure.db.models.learning.submission import Submission


def serialize_submission(submission: Submission) -> dict:
    compiler_errors = [
        {"type": e.error_type, "text": e.text}
        for e in submission.linter_errors
        if e.error_type == "COMPILER"
    ]
    linter_errors = [
        {"type": e.error_type, "text": e.text}
        for e in submission.linter_errors
        if e.error_type != "COMPILER"
    ]
    return {
        "id": submission.id,
        "submission_id": submission.id,
        "user_id": submission.user_id,
        "task_id": submission.task_id,
        "language": submission.language,
        "status": submission.status,
        "success": submission.success,
        "created_at": submission.created_at.isoformat() if submission.created_at else None,
        "updated_at": submission.updated_at.isoformat() if submission.updated_at else None,
        "compiler_errors": compiler_errors,
        "linter_errors": linter_errors,
        "pattern_errors": [
            {"type": e.error_type, "text": e.text} for e in submission.pattern_errors
        ],
        "test_results": [
            {
                "case": r.case_number,
                "status": r.status,
                "inputs": r.inputs,
                "expected": r.expected,
                "actual": r.actual,
                "message": r.message,
            }
            for r in submission.test_results
        ],
    }


def submission_to_solution_payload(submission: Submission) -> dict:
    """Map persisted submission to legacy solution-check response shape."""
    data = serialize_submission(submission)
    return {
        "task_id": data["task_id"],
        "submission_id": data["submission_id"],
        "success": bool(data["success"]),
        "compiler_errors": data["compiler_errors"],
        "linter_errors": data["linter_errors"],
        "pattern_errors": data["pattern_errors"],
        "test_results": data["test_results"],
        "status": data["status"],
    }
