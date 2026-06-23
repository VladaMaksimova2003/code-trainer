"""Hook curriculum progress after submission reaches a terminal state."""

from __future__ import annotations


def record_curriculum_progress_safe(
    *,
    user_id: int | None,
    submission_id: int,
    task_id: int,
    passed: bool,
    learning_language: str | None = None,
) -> None:
    """Best-effort side effect; must not break submission persistence."""
    if user_id is None:
        return
    try:
        from infrastructure.db.models.task.registry import load_models
        from infrastructure.db.session import SessionLocal
        from application.curriculum.progress.student_curriculum_progress_service import (
            StudentCurriculumProgressService,
        )

        load_models()
        db = SessionLocal()
        try:
            StudentCurriculumProgressService(db).record_submission_result(
                int(user_id),
                int(submission_id),
                int(task_id),
                passed=passed,
                learning_language=learning_language,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    except Exception as exc:
        print(f"[curriculum_progress] skipped: {exc}")


def record_curriculum_progress_in_session(
    db,
    *,
    user_id: int | None,
    submission_id: int,
    task_id: int,
    passed: bool,
    learning_language: str | None = None,
) -> None:
    """Same as above but reuses an open SQLAlchemy session (API path)."""
    if user_id is None:
        return
    from application.curriculum.progress.student_curriculum_progress_service import (
        StudentCurriculumProgressService,
    )

    StudentCurriculumProgressService(db).record_submission_result(
        int(user_id),
        int(submission_id),
        int(task_id),
        passed=passed,
        learning_language=learning_language,
    )
