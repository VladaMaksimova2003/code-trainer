#!/usr/bin/env python3
"""Delete ALL tasks, assignment sets (collections), and curriculum DB records.

Keeps users, groups, auth, support tickets (task_id cleared).

Usage (from backend/):
  python scripts/purge_all_tasks_and_curriculum.py --yes
  python scripts/purge_all_tasks_and_curriculum.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import delete, inspect, select, text, update
from sqlalchemy.orm import Session

from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from infrastructure.db.models.learning.curriculum_chapter_meta import CurriculumChapterMeta
from infrastructure.db.models.learning.student_curriculum_progress import StudentCurriculumProgressModel
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.learning.submission_comment import SubmissionComment
from infrastructure.db.models.support.in_app_notification import InAppNotification
from infrastructure.db.models.support.support_ticket import SupportTicket
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.session import SessionLocal
from scripts.reseed_v4_all import hard_delete_tasks_by_ids
from shared.config import Settings


def purge_all_tasks_and_curriculum(session: Session, *, dry_run: bool = False) -> dict:
    bind = session.get_bind()
    table_names = set(inspect(bind).get_table_names())
    report: dict = {"dry_run": dry_run, "counts": {}}

    task_ids = list(session.scalars(select(TaskModel.id)).all())
    report["task_ids_found"] = len(task_ids)

    if dry_run:
        report["counts"]["collections"] = len(session.scalars(select(Collection.id)).all())
        report["counts"]["curriculum_chapter_meta"] = len(
            session.scalars(select(CurriculumChapterMeta.id)).all()
        )
        report["counts"]["student_curriculum_progress"] = len(
            session.scalars(select(StudentCurriculumProgressModel.id)).all()
        )
        report["counts"]["task"] = len(task_ids)
        return report

    def _del(stmt) -> int:
        return session.execute(stmt).rowcount or 0

    if "student_curriculum_progress" in table_names:
        report["counts"]["student_curriculum_progress"] = _del(delete(StudentCurriculumProgressModel))

    if task_ids and "submission_comment" in table_names:
        submission_ids = list(session.scalars(select(Submission.id).where(Submission.task_id.in_(task_ids))).all())
        if submission_ids:
            report["counts"]["submission_comment"] = _del(
                delete(SubmissionComment).where(SubmissionComment.submission_id.in_(submission_ids))
            )

    task_delete = hard_delete_tasks_by_ids(session, task_ids, dry_run=False)
    report["counts"].update(task_delete.get("counts") or {})

    if "collections" in table_names:
        report["counts"]["collections"] = _del(delete(Collection))

    if "curriculum_chapter_meta" in table_names:
        report["counts"]["curriculum_chapter_meta"] = _del(delete(CurriculumChapterMeta))

    if "in_app_notification" in table_names:
        report["counts"]["in_app_notification_task_cleared"] = _del(
            update(InAppNotification).where(InAppNotification.task_id.is_not(None)).values(task_id=None)
        )

    if "support_ticket" in table_names:
        report["counts"]["support_ticket_task_cleared"] = _del(
            update(SupportTicket).where(SupportTicket.task_id.is_not(None)).values(task_id=None)
        )

    settings = Settings()
    if settings.db.dialect.startswith("postgres"):
        session.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('task', 'id'), 1, false) "
                "WHERE pg_get_serial_sequence('task', 'id') IS NOT NULL"
            )
        )
        report["task_id_sequence"] = "reset to 1"

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Purge all tasks, collections, curriculum metadata")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    settings = Settings()
    print(f"Target DB: {settings.db.host}:{settings.db.port}/{settings.db.name}")

    if not args.dry_run and not args.yes:
        typed = input("Type 'DELETE ALL TASKS' to continue: ").strip()
        if typed != "DELETE ALL TASKS":
            print("Aborted.")
            return 1

    load_models()
    session = SessionLocal()
    try:
        report = purge_all_tasks_and_curriculum(session, dry_run=args.dry_run)
        if not args.dry_run:
            session.commit()
            invalidate_showcase_task_index_cache()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    if not args.dry_run:
        print("Done. Database has no tasks, collections, or curriculum chapter meta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
