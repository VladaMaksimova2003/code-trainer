#!/usr/bin/env python3
"""Live dev verification — Pascal showcase curriculum progress via API + worker."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import delete, select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.pascal.legacy.loops.loops_showcase_reference_solutions import REFERENCE_SOLUTIONS
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import list_showcase_tasks
from application.curriculum.student_curriculum_progress_service import (
    PROGRESS_STATUS_FAILED,
    PROGRESS_STATUS_NOT_STARTED,
    PROGRESS_STATUS_PASSED,
    StudentCurriculumProgressService,
)
from infrastructure.db.models.learning.student_curriculum_progress import (
    StudentCurriculumProgressModel,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.user.user import User
from infrastructure.db.session import SessionLocal
from infrastructure.external.security.password_hasher import PasswordHasherService
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository
from shared.enums import UserType

TEST_EMAIL = os.getenv("SHOWCASE_PROGRESS_TEST_EMAIL", "showcase.progress.live@test.local")
TEST_PASSWORD = os.getenv("SHOWCASE_PROGRESS_TEST_PASSWORD", "ProgressLive123!")
TEST_NAME = "Showcase Progress Live"

PASS_SLUG = "counted_loop_tr_python"
FAIL_SLUG = "pre_condition_imp_text"
WRONG_CODE = (
    "program Wrong;\n"
    "var n: integer;\n"
    "begin\n"
    "  readln(n);\n"
    "  writeln(0);\n"
    "end."
)

LC_TOTAL = 7
LC_ONE_PCT = round(100 / LC_TOTAL, 1)
LC_TWO_PCT = round(200 / LC_TOTAL, 1)


@dataclass
class StepResult:
    step: str
    action: str
    expected: str
    actual: str
    ok: bool


def _default_api_base() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def ensure_test_user(session) -> User:
    hasher = PasswordHasherService()
    roles_repo = SqlAlchemyUserRoleRepository(session)
    user = session.scalars(select(User).where(User.email == TEST_EMAIL)).first()
    if user is None:
        user = User(
            name=TEST_NAME,
            email=TEST_EMAIL,
            password=hasher.hash(TEST_PASSWORD),
            role=UserType.STUDENT.value,
        )
        session.add(user)
        session.flush()
    else:
        user.password = hasher.hash(TEST_PASSWORD)
    roles_repo.assign_role(user.id, UserType.STUDENT)
    session.commit()
    session.refresh(user)
    return user


def clear_user_progress(session, user_id: int, task_ids: list[int]) -> None:
    if not task_ids:
        return
    session.execute(
        delete(StudentCurriculumProgressModel).where(
            StudentCurriculumProgressModel.user_id == user_id,
            StudentCurriculumProgressModel.task_id.in_(task_ids),
        )
    )
    session.commit()


def login(api_base: str) -> str:
    with httpx.Client(base_url=api_base, timeout=60.0) as client:
        resp = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
        resp.raise_for_status()
        return resp.json()["access_token"]


def fetch_student_view(api_base: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(base_url=api_base, timeout=60.0) as client:
        resp = client.get("/curriculum/pascal/showcase/loops/student", headers=headers)
        resp.raise_for_status()
        return resp.json()


def submit_and_wait(
    api_base: str,
    token: str,
    task_id: int,
    code: str,
    *,
    language: str = "pascal",
    timeout_sec: float = 120.0,
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(base_url=api_base, timeout=60.0) as client:
        created = client.post(
            "/submissions/",
            headers=headers,
            json={"task_id": task_id, "language": language, "code": code},
        )
        created.raise_for_status()
        submission_id = created.json()["submission_id"]
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            detail = client.get(f"/submissions/{submission_id}", headers=headers)
            detail.raise_for_status()
            payload = detail.json()
            if payload.get("status") in {"done", "failed"}:
                return payload
            time.sleep(0.5)
        raise TimeoutError(f"Submission {submission_id} not terminal after {timeout_sec}s")


def _tasks_by_slug(view: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for tc in view.get("technical_concepts") or []:
        for task in tc.get("tasks") or []:
            slug = task.get("slug")
            if slug:
                out[slug] = task
    return out


def _progress_summary(view: dict[str, Any]) -> str:
    prog = view.get("progress") or {}
    return (
        f"LC {prog.get('passed_tasks', '?')}/{prog.get('total_tasks', '?')} "
        f"({prog.get('progress_percent', '?')}%)"
    )


def _task_status(view: dict[str, Any], slug: str) -> str:
    return _tasks_by_slug(view).get(slug, {}).get("progress_status", "missing")


def _tc_progress(view: dict[str, Any], tc_id: str) -> str:
    for tc in view.get("technical_concepts") or []:
        if tc.get("id") == tc_id:
            p = tc.get("progress") or {}
            return f"{p.get('passed_tasks', '?')}/{p.get('total_tasks', '?')} ({p.get('progress_percent', '?')}%)"
    return "missing"


def _attempts_count(session, user_id: int, task_id: int) -> int:
    row = StudentCurriculumProgressService(session).get_progress_for_task(user_id, task_id)
    return int(row.get("attempts_count") or 0)


def _compact_progress_json(view: dict[str, Any]) -> dict[str, Any]:
    by_slug = {
        slug: {
            "task_id": task.get("task_id"),
            "progress_status": task.get("progress_status"),
        }
        for slug, task in _tasks_by_slug(view).items()
    }
    return {
        "progress": view.get("progress"),
        "tasks": by_slug,
    }


def run_verification(*, api_base: str, json_only: bool = False) -> tuple[list[StepResult], dict[str, Any]]:
    load_models()
    session = SessionLocal()
    steps: list[StepResult] = []
    snapshots: dict[str, Any] = {}

    try:
        showcase = list_showcase_tasks(session)
        assert len(showcase) == LC_TOTAL, f"expected {LC_TOTAL} showcase tasks, got {len(showcase)}"
        slug_to_id = {row["slug"]: row["task_id"] for row in showcase}
        task_ids = list(slug_to_id.values())

        user = ensure_test_user(session)
        clear_user_progress(session, user.id, task_ids)

        token = login(api_base)

        # Step 0 — baseline
        view0 = fetch_student_view(api_base, token)
        snapshots["0_tasks"] = _compact_progress_json(view0)
        all_not_started = all(
            t.get("progress_status") == PROGRESS_STATUS_NOT_STARTED
            for t in _tasks_by_slug(view0).values()
        )
        lc_zero = (view0.get("progress") or {}).get("progress_percent") == 0.0
        expected0 = f"LC 0/{LC_TOTAL} (0%), all {PROGRESS_STATUS_NOT_STARTED}"
        actual0 = f"{_progress_summary(view0)}, all_not_started={all_not_started}"
        steps.append(
            StepResult("5", "GET student (baseline)", expected0, actual0, lc_zero and all_not_started)
        )

        # Step 6-7 — pass first task
        pass_code = REFERENCE_SOLUTIONS[PASS_SLUG]
        sub_pass = submit_and_wait(api_base, token, slug_to_id[PASS_SLUG], pass_code)
        view1 = fetch_student_view(api_base, token)
        snapshots["1_passed"] = _compact_progress_json(view1)
        pass_ok = (
            sub_pass.get("status") == "done"
            and sub_pass.get("success") is True
            and _task_status(view1, PASS_SLUG) == PROGRESS_STATUS_PASSED
            and (view1.get("progress") or {}).get("passed_tasks") == 1
            and (view1.get("progress") or {}).get("progress_percent") == LC_ONE_PCT
            and _tc_progress(view1, "counted_loop") == f"1/2 ({50.0}%)"
        )
        expected1 = (
            f"{PASS_SLUG} passed; LC 1/{LC_TOTAL} ({LC_ONE_PCT}%); "
            f"counted_loop 1/2 (50%)"
        )
        actual1 = (
            f"sub success={sub_pass.get('success')}; "
            f"{PASS_SLUG}={_task_status(view1, PASS_SLUG)}; "
            f"{_progress_summary(view1)}; counted_loop={_tc_progress(view1, 'counted_loop')}"
        )
        steps.append(StepResult("6-7", f"PASS {PASS_SLUG}", expected1, actual1, pass_ok))

        # Step 8-9 — fail second task
        sub_fail = submit_and_wait(api_base, token, slug_to_id[FAIL_SLUG], WRONG_CODE)
        view2 = fetch_student_view(api_base, token)
        snapshots["1_passed_1_failed"] = _compact_progress_json(view2)
        attempts = _attempts_count(session, user.id, slug_to_id[FAIL_SLUG])
        fail_ok = (
            sub_fail.get("status") == "done"
            and sub_fail.get("success") is False
            and _task_status(view2, FAIL_SLUG) == PROGRESS_STATUS_FAILED
            and (view2.get("progress") or {}).get("passed_tasks") == 1
            and attempts == 1
        )
        expected2 = (
            f"{FAIL_SLUG} failed; LC still 1/{LC_TOTAL}; attempts_count=1"
        )
        actual2 = (
            f"sub success={sub_fail.get('success')}; "
            f"{FAIL_SLUG}={_task_status(view2, FAIL_SLUG)}; "
            f"{_progress_summary(view2)}; attempts={attempts}"
        )
        steps.append(StepResult("8-9", f"FAIL {FAIL_SLUG}", expected2, actual2, fail_ok))

        # Step 10-11 — retry pass
        retry_code = REFERENCE_SOLUTIONS[FAIL_SLUG]
        sub_retry = submit_and_wait(api_base, token, slug_to_id[FAIL_SLUG], retry_code)
        view3 = fetch_student_view(api_base, token)
        snapshots["2_passed"] = _compact_progress_json(view3)
        attempts_after = _attempts_count(session, user.id, slug_to_id[FAIL_SLUG])
        retry_ok = (
            sub_retry.get("success") is True
            and _task_status(view3, FAIL_SLUG) == PROGRESS_STATUS_PASSED
            and (view3.get("progress") or {}).get("passed_tasks") == 2
            and (view3.get("progress") or {}).get("progress_percent") == LC_TWO_PCT
            and attempts_after == 2
        )
        expected3 = f"{FAIL_SLUG} passed; LC 2/{LC_TOTAL} ({LC_TWO_PCT}%); attempts=2"
        actual3 = (
            f"sub success={sub_retry.get('success')}; "
            f"{FAIL_SLUG}={_task_status(view3, FAIL_SLUG)}; "
            f"{_progress_summary(view3)}; attempts={attempts_after}"
        )
        steps.append(StepResult("10-11", f"RETRY PASS {FAIL_SLUG}", expected3, actual3, retry_ok))

        if not json_only:
            print(f"API base: {api_base}")
            print(f"Test user: {TEST_EMAIL} (id={user.id})")
            print()
            print("| step | action | expected progress | actual progress | result |")
            print("|------|--------|-------------------|-----------------|--------|")
            for s in steps:
                mark = "PASS" if s.ok else "FAIL"
                print(
                    f"| {s.step} | {s.action} | {s.expected} | {s.actual} | {mark} |"
                )
            print()
            print("Progress JSON snapshots:")
            for key, payload in snapshots.items():
                print(f"\n--- {key} ---")
                print(json.dumps(payload, ensure_ascii=False, indent=2))

        return steps, snapshots
    finally:
        session.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Live dev check for Pascal showcase progress")
    parser.add_argument("--api-base", default=_default_api_base(), help="API root URL")
    parser.add_argument("--json-only", action="store_true", help="Print snapshots only")
    args = parser.parse_args()

    try:
        steps, _ = run_verification(api_base=args.api_base.rstrip("/"), json_only=args.json_only)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0 if all(s.ok for s in steps) else 1


if __name__ == "__main__":
    raise SystemExit(main())

