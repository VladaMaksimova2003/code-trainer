"""POST /tasks/assignments — create assignments."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from application.auth.dto import CurrentUserResult
from application.tasks.services.assignment_creation_service import (
    create_build_from_blocks_handler,
    create_flowchart_handler,
    create_translation_handler,
)
from application.tasks.use_cases.create_assignment import CreateAssignmentUseCase
from application.tasks.dto import CreateAssignmentCommand
from api.tasks.schemas.requests import CreateAssignmentRequest
from api.tasks.schemas.responses import AssignmentCreatedResponse
from api.dependencies.authorization import require_permission
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db
from infrastructure.db.models.task.collection import collection_task_association_table
from shared.enums import AssignmentType, DifficultyLevel

router = APIRouter()


def _create_assignment_use_case(db: Session) -> CreateAssignmentUseCase:
    return CreateAssignmentUseCase(
        create_build_from_blocks=lambda **kw: create_build_from_blocks_handler(db, **kw),
        create_translation=lambda **kw: create_translation_handler(db, **kw),
        create_flowchart=lambda **kw: create_flowchart_handler(db, **kw),
    )


@router.post("", response_model=AssignmentCreatedResponse)
@router.post("/", response_model=AssignmentCreatedResponse, include_in_schema=False)
async def create_assignment(
    request: CreateAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.CREATE_ASSIGNMENTS)
    ),
):
    """Create an assignment with explicit type, difficulty, and languages."""
    try:
        result = _create_assignment_use_case(db).execute(
            CreateAssignmentCommand(
                teacher_id=current_user.id,
                assignment_type=AssignmentType.parse(request.assignment_type),
                difficulty=DifficultyLevel.parse(request.difficulty),
                languages=request.languages,
                title=request.title,
                description=request.description,
                payload=request.payload,
                patterns=request.patterns,
                test_cases=request.test_cases,
            )
        )
        task_id = int(result.get("task_id") or result.get("id"))
        catalog_id = request.payload.get("catalog_id")
        if catalog_id not in (None, "", 0, "0"):
            try:
                db.execute(
                    collection_task_association_table.insert().values(
                        collection_id=int(catalog_id),
                        task_id=task_id,
                        sort_order=0,
                    )
                )
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Не удалось добавить задачу в каталог: каталог не найден или задача уже в нём.",
                ) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create assignment: {exc}",
        ) from exc

    return AssignmentCreatedResponse(
        task_id=int(result.get("task_id") or result.get("id")),
        assignment_type=result.get("assignment_type", request.assignment_type),
        type=result.get("type", request.assignment_type),
        languages=result.get("languages"),
    )
