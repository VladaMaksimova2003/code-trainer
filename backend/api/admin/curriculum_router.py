"""Admin curriculum v2: debug view + task curriculum links."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.admin.task_curriculum_schemas import (
    TaskCurriculumLinkCreateRequest,
    TaskCurriculumLinkResponse,
    TaskCurriculumLinkUpdateRequest,
    TaskCurriculumLinkValidateRequest,
    TaskCurriculumLinkValidateResponse,
    TaskCurriculumMetadataResponse,
)
from api.dependencies.authorization import require_permission
from application.auth.dto import CurrentUserResult
from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import list_showcase_tasks
from application.curriculum.task_curriculum_link_service import (
    TaskCurriculumLinkService,
    validate_task_curriculum_link_metadata,
)
from domain.learning.curriculum.exceptions import CurriculumNotFoundError, CurriculumValidationError
from domain.learning.curriculum.task_link import TaskCurriculumLink
from domain.learning.curriculum.task_link_exceptions import (
    TaskCurriculumLinkNotFoundError,
    TaskCurriculumLinkValidationError,
)
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db
from shared.exceptions import TaskNotFoundError

router = APIRouter(prefix="/curriculum", tags=["admin-curriculum"])


def _link_response(link: TaskCurriculumLink) -> TaskCurriculumLinkResponse:
    return TaskCurriculumLinkResponse(
        id=link.id,
        task_id=link.task_id,
        language=link.language,
        learning_concept_id=link.learning_concept_id,
        technical_concept_id=link.technical_concept_id,
        exercise_pattern_id=link.exercise_pattern_id,
        action=link.action,
        is_primary=link.is_primary,
        created_at=link.created_at.isoformat() if link.created_at else None,
    )


def _task_link_service(db: Session) -> TaskCurriculumLinkService:
    return TaskCurriculumLinkService(db)


def _handle_link_error(exc: Exception) -> HTTPException:
    if isinstance(exc, TaskNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, TaskCurriculumLinkNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, TaskCurriculumLinkValidationError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, CurriculumNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# --- Task curriculum links (must be before /{language}/... routes) ---


@router.get("/showcase/pascal/conditions")
async def list_pascal_conditions_showcase_tasks(
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
) -> dict:
    from application.curriculum.pascal.legacy.conditions.conditions_showcase_seeder import list_showcase_tasks as list_conditions_tasks

    return {
        "learning_concept_id": "conditions",
        "language": "pascal",
        "tasks": list_conditions_tasks(db),
    }


@router.get("/showcase/pascal/loops")
async def list_pascal_loops_showcase_tasks(
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "learning_concept_id": "loops",
        "language": "pascal",
        "tasks": list_showcase_tasks(db),
    }


@router.post(
    "/tasks/validate-link",
    response_model=TaskCurriculumLinkValidateResponse,
)
async def validate_task_curriculum_link(
    body: TaskCurriculumLinkValidateRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
) -> TaskCurriculumLinkValidateResponse:
    try:
        payload = validate_task_curriculum_link_metadata(
            body.language,
            body.technical_concept_id,
            body.exercise_pattern_id,
        )
        return TaskCurriculumLinkValidateResponse(**payload)
    except TaskCurriculumLinkValidationError as exc:
        raise _handle_link_error(exc) from exc


@router.get(
    "/tasks/{task_id}/links",
    response_model=TaskCurriculumMetadataResponse,
)
async def get_task_curriculum_links(
    task_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
) -> TaskCurriculumMetadataResponse:
    try:
        payload = _task_link_service(db).get_task_curriculum_metadata(task_id)
        return TaskCurriculumMetadataResponse(
            task_id=payload["task_id"],
            has_curriculum_link=payload["has_curriculum_link"],
            primary_link=(
                TaskCurriculumLinkResponse(**payload["primary_link"])
                if payload["primary_link"]
                else None
            ),
            links=[TaskCurriculumLinkResponse(**item) for item in payload["links"]],
        )
    except (TaskNotFoundError, TaskCurriculumLinkValidationError) as exc:
        raise _handle_link_error(exc) from exc


@router.post(
    "/tasks/{task_id}/links",
    response_model=TaskCurriculumLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_curriculum_link(
    task_id: int,
    body: TaskCurriculumLinkCreateRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
) -> TaskCurriculumLinkResponse:
    try:
        link = _task_link_service(db).link_task_to_curriculum(
            task_id,
            body.language,
            body.technical_concept_id,
            body.exercise_pattern_id,
            is_primary=body.is_primary,
        )
        db.commit()
        return _link_response(link)
    except (
        TaskNotFoundError,
        TaskCurriculumLinkValidationError,
        TaskCurriculumLinkNotFoundError,
    ) as exc:
        db.rollback()
        raise _handle_link_error(exc) from exc


@router.patch(
    "/tasks/{task_id}/links/{link_id}",
    response_model=TaskCurriculumLinkResponse,
)
async def update_task_curriculum_link(
    task_id: int,
    link_id: int,
    body: TaskCurriculumLinkUpdateRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
) -> TaskCurriculumLinkResponse:
    try:
        link = _task_link_service(db).update_link(
            task_id,
            link_id,
            is_primary=body.is_primary,
            technical_concept_id=body.technical_concept_id,
            exercise_pattern_id=body.exercise_pattern_id,
            language=body.language,
        )
        db.commit()
        return _link_response(link)
    except (
        TaskNotFoundError,
        TaskCurriculumLinkValidationError,
        TaskCurriculumLinkNotFoundError,
    ) as exc:
        db.rollback()
        raise _handle_link_error(exc) from exc


@router.delete(
    "/tasks/{task_id}/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task_curriculum_link(
    task_id: int,
    link_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
) -> None:
    try:
        _task_link_service(db).delete_link(task_id, link_id)
        db.commit()
    except (TaskNotFoundError, TaskCurriculumLinkNotFoundError) as exc:
        db.rollback()
        raise _handle_link_error(exc) from exc


# --- Curriculum debug ---


@router.get("/{language}/debug")
async def get_curriculum_debug(
    language: str,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> dict:
    try:
        return CurriculumService(language).get_debug_view(language)
    except CurriculumNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CurriculumValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(exc), "errors": exc.errors},
        ) from exc


@router.get("/{language}/validate")
async def validate_curriculum_admin(
    language: str,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> dict:
    try:
        return CurriculumService(language).validate_curriculum(language)
    except CurriculumNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

