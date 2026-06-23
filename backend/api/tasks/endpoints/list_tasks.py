"""GET /tasks — list and get single task."""
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from api.tasks.schemas.responses import PublicTaskDetailResponse, TaskOverviewResponse
from application.auth.dto import CurrentUserResult
from application.learning.skill_progress_service import normalize_curriculum_language
from application.curriculum.progress.student_curriculum_progress_service import (
    PROGRESS_STATUS_FAILED,
    PROGRESS_STATUS_PASSED,
    activate_batch_progress_cache,
    get_batch_progress_cache,
    reset_batch_progress_cache,
)
from application.tasks.services.content_access_service import ContentAccessService
from application.tasks.services.catalog.task_catalog_orchestrator import (
    get_task as get_task_from_db,
    list_tasks as list_tasks_from_db,
    list_task_overviews as list_task_overviews_from_db,
)
from application.tasks.use_cases.block_reorder.get import get_block_reorder_public_task
from api.dependencies.auth import get_optional_current_user
from domain.policies.rbac.rbac import normalize_role
from infrastructure.db.session import get_db
from infrastructure.db.models.learning.submission import Submission

router = APIRouter()


def _allowed_task_ids(db: Session, current: CurrentUserResult | None) -> set[int]:
    access = ContentAccessService(db)
    if current is None:
        return access.public_task_ids()
    roles = frozenset(normalize_role(r) for r in current.roles)
    return access.list_accessible_task_ids(current.id, roles)


def _ensure_task_access_or_404(
    db: Session,
    current: CurrentUserResult | None,
    task_id: int,
) -> None:
    access = ContentAccessService(db)
    roles = (
        frozenset(normalize_role(r) for r in current.roles)
        if current is not None
        else frozenset()
    )
    user_id = current.id if current is not None else None
    if not access.can_access_task(user_id, roles, task_id):
        raise HTTPException(status_code=404, detail="Task not found")


def _user_progress_by_task(db: Session, user_id: int | None, task_ids: list[int]) -> dict[int, dict]:
    if user_id is None or not task_ids:
        return {}
    rows = db.execute(
        select(
            Submission.task_id,
            func.count().label("submissions_count"),
            func.max(case((Submission.success.is_(True), 1), else_=0)).label("solved"),
        )
        .where(Submission.user_id == user_id, Submission.task_id.in_(task_ids))
        .group_by(Submission.task_id)
    ).all()
    progress: dict[int, dict] = {}
    for row in rows:
        progress[int(row.task_id)] = {
            "attempted": int(row.submissions_count or 0) > 0,
            "solved": bool(row.solved),
            "submissions_count": int(row.submissions_count or 0),
        }
    return progress


def _user_language_track_states(
    db: Session,
    user_id: int | None,
    tasks: list[dict],
    *,
    progress_cache: dict[tuple[int, str], str] | None = None,
) -> dict[int, dict[str, str]]:
    if user_id is None or not tasks:
        return {}

    task_ids = [int(task["id"]) for task in tasks]
    rows = db.execute(
        select(
            Submission.task_id,
            Submission.language,
            func.max(case((Submission.success.is_(True), 1), else_=0)).label("solved"),
            func.count().label("submissions_count"),
        )
        .where(Submission.user_id == user_id, Submission.task_id.in_(task_ids))
        .group_by(Submission.task_id, Submission.language)
    ).all()

    by_task: dict[int, dict[str, str]] = defaultdict(dict)
    for row in rows:
        lang = normalize_curriculum_language(row.language)
        if not lang:
            continue
        task_id = int(row.task_id)
        if bool(row.solved):
            by_task[task_id][lang] = "solved"
        elif int(row.submissions_count or 0) > 0:
            by_task[task_id].setdefault(lang, "attempted")

    if progress_cache:
        for task in tasks:
            task_id = int(task["id"])
            tracks = task.get("available_language_tracks") or []
            for track in tracks:
                lang = normalize_curriculum_language(str(track)) or str(track).strip().lower()
                status = progress_cache.get((task_id, lang))
                if status == PROGRESS_STATUS_PASSED:
                    by_task[task_id][lang] = "solved"
                elif status == PROGRESS_STATUS_FAILED:
                    if by_task[task_id].get(lang) != "solved":
                        by_task[task_id][lang] = "attempted"

    return {task_id: dict(states) for task_id, states in by_task.items()}


def _apply_language_track_states(task: dict, states: dict[int, dict[str, str]]) -> dict:
    track_states = states.get(int(task["id"]))
    if track_states:
        task["language_track_states"] = track_states
    return task


def _apply_user_progress(task: dict, progress: dict[int, dict]) -> dict:
    item = progress.get(int(task["id"]), {})
    task["attempted"] = bool(item.get("attempted", False))
    task["solved"] = bool(item.get("solved", False))
    task["submissions_count"] = int(item.get("submissions_count", 0))
    task["completed"] = task["solved"]
    return task


def _matches_status_filter(task: dict, status: str | None) -> bool:
    normalized = str(status or "all").strip().lower()
    if not normalized or normalized == "all":
        return True
    solved = bool(task.get("solved"))
    attempted = bool(task.get("attempted"))
    if normalized == "solved":
        return solved
    if normalized == "attempted":
        return attempted and not solved
    if normalized == "todo":
        return not attempted and not solved
    return True


def _matches_filter_bundle(
    task: dict,
    *,
    search: str | None,
    task_type: str | None,
    difficulty: str | None,
    pattern: str | None,
    language: str | None,
    status: str | None,
    match_mode: str,
) -> bool:
    from application.tasks.services.catalog.task_overview import _matches_list_filters

    checks: list[bool] = []
    if search and str(search).strip():
        checks.append(
            _matches_list_filters(task, search=search)
        )
    if task_type and str(task_type).strip() and str(task_type) != "all":
        checks.append(
            _matches_list_filters(task, task_type=task_type)
        )
    if difficulty and str(difficulty).strip() and str(difficulty) != "all":
        checks.append(
            _matches_list_filters(task, difficulty=difficulty)
        )
    if pattern and str(pattern).strip():
        checks.append(
            _matches_list_filters(task, pattern=pattern)
        )
    if language and str(language).strip() and str(language) != "all":
        checks.append(
            _matches_list_filters(task, language=language)
        )
    if status and str(status).strip() and str(status) != "all":
        checks.append(_matches_status_filter(task, status))
    if not checks:
        return True
    if str(match_mode or "all").strip().lower() == "any":
        return any(checks)
    return all(checks)


def _task_ids_for_progress_status(
    db: Session,
    user_id: int,
    status: str,
    *,
    allowed_task_ids: set[int],
) -> set[int]:
    """Resolve task ids for status filter (match_mode=all only)."""
    normalized = str(status or "").strip().lower()
    if not normalized or normalized == "all" or not allowed_task_ids:
        return allowed_task_ids

    rows = db.execute(
        select(
            Submission.task_id,
            func.count().label("submissions_count"),
            func.max(case((Submission.success.is_(True), 1), else_=0)).label("solved"),
        )
        .where(
            Submission.user_id == user_id,
            Submission.task_id.in_(allowed_task_ids),
        )
        .group_by(Submission.task_id)
    ).all()
    solved = {int(row.task_id) for row in rows if bool(row.solved)}
    attempted = {int(row.task_id) for row in rows if int(row.submissions_count or 0) > 0}

    if normalized == "solved":
        return solved
    if normalized == "attempted":
        return attempted - solved
    if normalized == "todo":
        return allowed_task_ids - attempted
    return allowed_task_ids


def _overview_requires_full_scan(
    *,
    status: str | None,
    match_mode: str,
    search: str | None,
    task_type: str | None,
    difficulty: str | None,
    pattern: str | None,
    language: str | None,
    page_size: int | None,
) -> bool:
    if page_size is None or page_size <= 0:
        return True
    if str(match_mode or "all").strip().lower() != "any":
        return False
    active_filters = 0
    for value in (search, task_type, difficulty, pattern, language, status):
        normalized = str(value or "").strip().lower()
        if normalized and normalized != "all":
            active_filters += 1
    return active_filters > 1


def _build_task_overview_response(
    db: Session,
    current: CurrentUserResult | None,
    *,
    course: str | None = None,
    chapter: str | None = None,
    target_language: str | None = None,
    search: str | None = None,
    task_type: str | None = None,
    difficulty: str | None = None,
    pattern: str | None = None,
    language: str | None = None,
    status: str | None = None,
    match_mode: str = "all",
    page: int = 1,
    page_size: int | None = None,
) -> TaskOverviewResponse:
    allowed = _allowed_task_ids(db, current)
    user_id = current.id if current is not None else None
    batch_token = activate_batch_progress_cache(db, user_id)
    try:
        restrict_task_ids: set[int] | None = None
        if (
            user_id is not None
            and status
            and str(status).strip().lower() not in {"", "all"}
            and not _overview_requires_full_scan(
                status=status,
                match_mode=match_mode,
                search=search,
                task_type=task_type,
                difficulty=difficulty,
                pattern=pattern,
                language=language,
                page_size=page_size,
            )
        ):
            restrict_task_ids = _task_ids_for_progress_status(
                db,
                user_id,
                status,
                allowed_task_ids=allowed,
            )

        if _overview_requires_full_scan(
            status=status,
            match_mode=match_mode,
            search=search,
            task_type=task_type,
            difficulty=difficulty,
            pattern=pattern,
            language=language,
            page_size=page_size,
        ):
            payload = list_task_overviews_from_db(
                db,
                allowed_task_ids=allowed,
                course=course,
                chapter=chapter,
                target_language=target_language,
                search=search,
                task_type=task_type,
                difficulty=difficulty,
                pattern=pattern,
                language=language,
                page=1,
                page_size=None,
            )
            progress = _user_progress_by_task(db, user_id, [int(t["id"]) for t in payload["tasks"]])
            progress_cache = get_batch_progress_cache()
            language_states = _user_language_track_states(
                db,
                user_id,
                payload["tasks"],
                progress_cache=progress_cache,
            )
            enriched = [
                _apply_language_track_states(
                    _apply_user_progress(task, progress),
                    language_states,
                )
                for task in payload["tasks"]
            ]
            filtered = [
                task
                for task in enriched
                if _matches_filter_bundle(
                    task,
                    search=search,
                    task_type=task_type,
                    difficulty=difficulty,
                    pattern=pattern,
                    language=language,
                    status=status,
                    match_mode=match_mode,
                )
            ]
            total = len(filtered)
            safe_page = max(page, 1)
            if page_size is not None and page_size > 0:
                start = (safe_page - 1) * page_size
                tasks = filtered[start : start + page_size]
                response_page_size = page_size
            else:
                tasks = filtered
                safe_page = 1
                response_page_size = total
        else:
            payload = list_task_overviews_from_db(
                db,
                allowed_task_ids=allowed,
                course=course,
                chapter=chapter,
                target_language=target_language,
                search=search,
                task_type=task_type,
                difficulty=difficulty,
                pattern=pattern,
                language=language,
                restrict_task_ids=restrict_task_ids,
                page=page,
                page_size=page_size,
            )
            task_ids = [int(task["id"]) for task in payload["tasks"]]
            progress = _user_progress_by_task(db, user_id, task_ids)
            progress_cache = get_batch_progress_cache()
            language_states = _user_language_track_states(
                db,
                user_id,
                payload["tasks"],
                progress_cache=progress_cache,
            )
            tasks = [
                _apply_language_track_states(
                    _apply_user_progress(task, progress),
                    language_states,
                )
                for task in payload["tasks"]
            ]
            total = int(payload["total"])
            safe_page = int(payload.get("page") or max(page, 1))
            response_page_size = int(
                payload.get("page_size") or (page_size if page_size else total)
            )
    finally:
        reset_batch_progress_cache(batch_token)

    return TaskOverviewResponse(
        tasks=tasks,
        total=int(total),
        page=int(safe_page),
        page_size=int(response_page_size),
    )


_OVERVIEW_FILTER_PARAMS = dict(
    search=Query(default=None, description="Filter by title substring"),
    task_type=Query(default=None, alias="type", description="Filter by public task type"),
    difficulty=Query(default=None, description="Filter by difficulty"),
    pattern=Query(default=None, description="Filter by construction/pattern id"),
    language=Query(default=None, description="Filter by learning language id, e.g. python"),
    status=Query(default=None, description="Student progress filter: solved, attempted, todo"),
    match_mode=Query(default="all", description="Combine filters with all (AND) or any (OR)"),
)


@router.get("/overview", response_model=TaskOverviewResponse)
async def list_tasks_overview(
    db: Session = Depends(get_db),
    current: CurrentUserResult | None = Depends(get_optional_current_user),
    course: str | None = Query(default=None, description="Filter by course language, e.g. python or pascal"),
    chapter: str | None = Query(default=None, description="Filter by chapter key, e.g. loops or oop"),
    target_language: str | None = Query(
        default=None,
        description="Resolve chapter/slot fields for this learning language (pascal or python)",
    ),
    search: str | None = _OVERVIEW_FILTER_PARAMS["search"],
    task_type: str | None = _OVERVIEW_FILTER_PARAMS["task_type"],
    difficulty: str | None = _OVERVIEW_FILTER_PARAMS["difficulty"],
    pattern: str | None = _OVERVIEW_FILTER_PARAMS["pattern"],
    language: str | None = _OVERVIEW_FILTER_PARAMS["language"],
    status: str | None = _OVERVIEW_FILTER_PARAMS["status"],
    match_mode: str = _OVERVIEW_FILTER_PARAMS["match_mode"],
    page: int = Query(default=1, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=500),
) -> TaskOverviewResponse:
    """Lightweight task listing for student home — no heavy payload."""
    return _build_task_overview_response(
        db,
        current,
        course=course,
        chapter=chapter,
        target_language=target_language,
        search=search,
        task_type=task_type,
        difficulty=difficulty,
        pattern=pattern,
        language=language,
        status=status,
        match_mode=match_mode,
        page=page,
        page_size=page_size,
    )


@router.get("/")
async def list_tasks(
    db: Session = Depends(get_db),
    current: CurrentUserResult | None = Depends(get_optional_current_user),
    light: bool = Query(default=False, description="Return lightweight overview rows only"),
    course: str | None = Query(default=None),
    chapter: str | None = Query(default=None),
    target_language: str | None = Query(default=None),
    search: str | None = _OVERVIEW_FILTER_PARAMS["search"],
    task_type: str | None = _OVERVIEW_FILTER_PARAMS["task_type"],
    difficulty: str | None = _OVERVIEW_FILTER_PARAMS["difficulty"],
    pattern: str | None = _OVERVIEW_FILTER_PARAMS["pattern"],
    language: str | None = _OVERVIEW_FILTER_PARAMS["language"],
    status: str | None = _OVERVIEW_FILTER_PARAMS["status"],
    match_mode: str = _OVERVIEW_FILTER_PARAMS["match_mode"],
    page: int = Query(default=1, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=500),
):
    """List tasks accessible to the current user."""
    if light:
        return _build_task_overview_response(
            db,
            current,
            course=course,
            chapter=chapter,
            target_language=target_language,
            search=search,
            task_type=task_type,
            difficulty=difficulty,
            pattern=pattern,
            language=language,
            status=status,
            match_mode=match_mode,
            page=page,
            page_size=page_size,
        )

    allowed = _allowed_task_ids(db, current)
    tasks = [
        {
            "id": t["id"],
            "title": t["title"],
            "description": t["description"],
            "difficulty": t["difficulty"],
            "type": t["type"],
            "solution_description": t.get("solution_description"),
            "algorithm_hint": t.get("algorithm_hint"),
            "constructions": t.get("constructions", []),
            "code_examples": t.get("code_examples"),
            "test_cases": t.get("test_cases"),
            "blocks": t.get("blocks", []),
            "language": t.get("language") or t.get("source_language"),
            "source_language": t.get("source_language"),
            "template": t.get("template"),
            "constructions": t.get("constructions", []),
            "construction_hints": t.get("construction_hints", {}),
            "task_type": t.get("task_type", t.get("type")),
        }
        for t in list_tasks_from_db(db, allowed_task_ids=allowed)
    ]
    progress = _user_progress_by_task(
        db,
        current.id if current is not None else None,
        [int(task["id"]) for task in tasks],
    )
    tasks = [_apply_user_progress(task, progress) for task in tasks]
    return {"tasks": tasks}


@router.get("/types")
async def get_task_types():
    """List available task types."""
    from application.tasks.services.catalog.task_catalog_orchestrator import list_task_types
    return {"types": list_task_types()}


@router.get("/{task_id}", response_model=PublicTaskDetailResponse)
async def get_task(
    task_id: int,
    learning_language: str | None = Query(default=None, alias="learning_language"),
    source_language: str | None = Query(default=None, alias="source_language"),
    db: Session = Depends(get_db),
    current: CurrentUserResult | None = Depends(get_optional_current_user),
):
    """Get a single task by ID."""
    _ensure_task_access_or_404(db, current, task_id)

    progress = _user_progress_by_task(
        db, current.id if current is not None else None, [task_id]
    )
    block_reorder_task = get_block_reorder_public_task(db, task_id)
    if block_reorder_task:
        from application.curriculum.display.curriculum_labels import attach_curriculum_display_to_task

        return _apply_user_progress(
            attach_curriculum_display_to_task(
                db,
                task_id,
                block_reorder_task,
                learning_language=learning_language,
                source_language=source_language,
            ),
            progress,
        )

    task = get_task_from_db(
        db,
        task_id,
        allowed_task_ids=None,
        learning_language=learning_language,
        source_language=source_language,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _apply_user_progress(task, progress)
