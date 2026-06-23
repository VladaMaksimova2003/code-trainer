"""Curriculum v2 read API — LC → TC → patterns (YAML-backed)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.curriculum.schemas_v2 import (
    ActionMaskResponse,
    CurriculumSummaryResponse,
    CurriculumValidationResponse,
    ExercisePatternResponse,
    LearningConceptDetailResponse,
    LearningConceptResponse,
    TechnicalConceptInChapterResponse,
    TechnicalConceptPatternsResponse,
    TechnicalConceptSummaryResponse,
)
from api.curriculum.schemas_student import (
    CurriculumCollectionNavigationResponse,
    CurriculumCollectionsViewResponse,
    CurriculumGlobalNextResponse,
    PascalShowcaseNextResponse,
    PascalShowcaseStudentViewResponse,
    PascalShowcaseTasksListResponse,
)
from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import list_showcase_tasks
from domain.learning.curriculum.exceptions import CurriculumNotFoundError, CurriculumValidationError
from domain.learning.curriculum.models import ExercisePattern, LearningConcept, TechnicalConceptActionMask
from api.dependencies.auth import get_optional_current_user
from application.auth.dto import CurrentUserResult
from infrastructure.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()


def _service(language: str) -> CurriculumService:
    return CurriculumService(language)


def _lc_response(lc: LearningConcept) -> LearningConceptResponse:
    return LearningConceptResponse(
        id=lc.id,
        name_ru=lc.name_ru,
        tier=lc.tier,
        order=lc.order,
        description_ru=lc.description_ru,
    )


def _pattern_response(p: ExercisePattern) -> ExercisePatternResponse:
    return ExercisePatternResponse(
        id=p.id,
        action=p.action,
        description_ru=p.description_ru,
        grading=p.grading,
        legacy_adapter=p.legacy_adapter,
        source=p.source,
        target=p.target,
        transfer=p.transfer,
    )


def _mask_response(mask: TechnicalConceptActionMask) -> ActionMaskResponse:
    return ActionMaskResponse(
        technical_concept_id=mask.technical_concept_id,
        required_actions=list(mask.required_actions),
        optional_actions=list(mask.optional_actions),
        disabled_actions=list(mask.disabled_actions),
        active_actions=list(mask.active_actions()),
        required_patterns_by_action={
            action: list(mask.patterns_for_action(action, required_only=True))
            for action in mask.active_actions()
        },
        optional_patterns_by_action={
            action: [
                pid
                for pid in mask.patterns_for_action(action)
                if pid not in mask.patterns_for_action(action, required_only=True)
            ]
            for action in mask.active_actions()
        },
        disabled_patterns_by_action={
            action: list(mask.disabled_patterns_by_action.get(action, ()))
            for action in mask.disabled_patterns_by_action
        },
    )


def _handle_curriculum_error(exc: Exception) -> HTTPException:
    if isinstance(exc, CurriculumNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, CurriculumValidationError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(exc), "errors": exc.errors},
        )
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/collections", response_model=CurriculumCollectionsViewResponse)
async def get_curriculum_collections(
    language: str | None = None,
    light: bool = Query(default=False, description="Fast summaries without per-collection next-task resolution"),
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> CurriculumCollectionsViewResponse:
    from application.curriculum.collections.curriculum_next_service import build_curriculum_collections_view

    user_id = current_user.id if current_user else None
    return build_curriculum_collections_view(db, user_id, language=language, light=light)


@router.get("/next", response_model=CurriculumGlobalNextResponse)
async def get_curriculum_next(
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> CurriculumGlobalNextResponse:
    from application.curriculum.collections.curriculum_next_service import build_global_curriculum_next

    user_id = current_user.id if current_user else None
    return build_global_curriculum_next(db, user_id)


@router.get("/pascal/showcase/all-task-ids")
async def get_all_pascal_task_ids(
    db: Session = Depends(get_db),
) -> dict:
    """Return ordered list of all v3.1.1 Pascal task IDs across all chapters."""
    from application.curriculum.pascal.showcase.pascal_v311_registry import PASCAL_V311_SHOWCASE_COLLECTIONS
    from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import all_pascal_v311_showcase_specs
    from application.curriculum.pascal.showcase.pascal_showcase_next import order_collection_showcase_tasks
    from application.curriculum.showcase.showcase_task_index import run_with_showcase_task_index

    specs_by_chapter = all_pascal_v311_showcase_specs()

    def _collect() -> list[int]:
        task_ids: list[int] = []
        for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
            specs = specs_by_chapter.get(col.chapter_key, ())
            ordered = order_collection_showcase_tasks(db, col.chapter_key, specs)
            task_ids.extend(int(row["task_id"]) for row in ordered)
        return task_ids

    return {"task_ids": run_with_showcase_task_index(db, _collect)}


@router.get("/python/showcase/all-task-ids")
async def get_all_python_task_ids(
    db: Session = Depends(get_db),
) -> dict:
    """Return ordered list of all Python v1 task IDs across all chapters."""
    from application.curriculum.python.showcase.python_v311_registry import PYTHON_V311_SHOWCASE_COLLECTIONS
    from application.curriculum.python.showcase.python_v311_showcase_all_specs import all_python_v311_showcase_specs
    from application.curriculum.python.showcase.python_showcase_next import order_collection_showcase_tasks
    from application.curriculum.showcase.showcase_task_index import run_with_showcase_task_index

    specs_by_chapter = all_python_v311_showcase_specs()

    def _collect() -> list[int]:
        task_ids: list[int] = []
        for col in PYTHON_V311_SHOWCASE_COLLECTIONS:
            specs = specs_by_chapter.get(col.chapter_key, ())
            ordered = order_collection_showcase_tasks(db, col.chapter_key, specs)
            task_ids.extend(int(row["task_id"]) for row in ordered)
        return task_ids

    return {"task_ids": run_with_showcase_task_index(db, _collect)}


@router.get("/cpp/showcase/all-task-ids")
async def get_all_cpp_task_ids(
    db: Session = Depends(get_db),
) -> dict:
    """Return ordered list of all C++ v1 task IDs across seeded chapters."""
    from application.curriculum.cpp.showcase.cpp_v311_registry import CPP_V311_SHOWCASE_COLLECTIONS
    from application.curriculum.cpp.showcase.cpp_showcase_core import list_cpp_tasks_for_collection

    task_ids: list[int] = []
    for col in CPP_V311_SHOWCASE_COLLECTIONS:
        rows = list_cpp_tasks_for_collection(db, col.chapter_key)
        task_ids.extend(int(row["task_id"]) for row in rows)
    return {"task_ids": task_ids}


@router.get("/java/showcase/all-task-ids")
async def get_all_java_task_ids(
    db: Session = Depends(get_db),
) -> dict:
    """Return ordered list of all Java v1 task IDs across seeded chapters."""
    from application.curriculum.java.showcase.java_v311_registry import JAVA_V311_SHOWCASE_COLLECTIONS
    from application.curriculum.java.showcase.java_showcase_core import list_java_tasks_for_collection

    task_ids: list[int] = []
    for col in JAVA_V311_SHOWCASE_COLLECTIONS:
        rows = list_java_tasks_for_collection(db, col.chapter_key)
        task_ids.extend(int(row["task_id"]) for row in rows)
    return {"task_ids": task_ids}


@router.get("/csharp/showcase/all-task-ids")
async def get_all_csharp_task_ids(
    db: Session = Depends(get_db),
) -> dict:
    """Return ordered list of all C# v1 task IDs across seeded chapters."""
    from application.curriculum.csharp.showcase.csharp_v311_registry import CSHARP_V311_SHOWCASE_COLLECTIONS
    from application.curriculum.csharp.showcase.csharp_showcase_core import list_csharp_tasks_for_collection

    task_ids: list[int] = []
    for col in CSHARP_V311_SHOWCASE_COLLECTIONS:
        rows = list_csharp_tasks_for_collection(db, col.chapter_key)
        task_ids.extend(int(row["task_id"]) for row in rows)
    return {"task_ids": task_ids}


@router.get(
    "/collections/{collection_id}/navigation",
    response_model=CurriculumCollectionNavigationResponse,
)
async def get_collection_navigation(
    collection_id: str,
    task_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> CurriculumCollectionNavigationResponse:
    from application.curriculum.collections.curriculum_collection_navigation import (
        build_collection_navigation_by_collection_id,
    )

    payload = build_collection_navigation_by_collection_id(
        db,
        collection_id=collection_id,
        task_id=task_id,
    )
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection navigation not found for this task",
        )
    return payload


@router.get(
    "/pascal/showcase/{route_suffix}/next",
    response_model=PascalShowcaseNextResponse,
)
async def get_pascal_showcase_next(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseNextResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key
    from application.curriculum.pascal.showcase.pascal_v311_registry import v311_collection_by_key
    from application.curriculum.pascal.showcase.pascal_showcase_next import (
        build_pascal_showcase_collection_next,
        build_pascal_v311_showcase_collection_next,
    )

    chapter_key = route_suffix_to_chapter_key(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    if v311_collection_by_key(chapter_key) is not None:
        return build_pascal_v311_showcase_collection_next(db, chapter_key, user_id)
    return build_pascal_showcase_collection_next(db, chapter_key, user_id)


@router.get(
    "/pascal/showcase/{route_suffix}/student",
    response_model=PascalShowcaseStudentViewResponse,
)
async def get_pascal_showcase_student(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseStudentViewResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key
    from application.curriculum.pascal.showcase.pascal_showcase_student import build_pascal_showcase_student_view

    chapter_key = route_suffix_to_chapter_key(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    return build_pascal_showcase_student_view(db, chapter_key, user_id=user_id)


@router.get(
    "/pascal/showcase/{route_suffix}",
    response_model=PascalShowcaseTasksListResponse,
)
async def get_pascal_showcase_tasks(route_suffix: str, db: Session = Depends(get_db)) -> PascalShowcaseTasksListResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key
    from application.curriculum.pascal.showcase.pascal_showcase_core import list_showcase_tasks_for_collection
    from application.curriculum.pascal.showcase.pascal_v311_registry import v311_collection_by_key

    chapter_key = route_suffix_to_chapter_key(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    col = v311_collection_by_key(chapter_key)
    curriculum_version = "3.1.1" if col is not None else "2"
    return {
        "collection_key": chapter_key,
        "learning_concept_id": col.yaml_chapter_id if col else chapter_key,
        "language": "pascal",
        "tasks": list_showcase_tasks_for_collection(db, chapter_key, curriculum_version=curriculum_version),
    }


@router.get(
    "/python/showcase/{route_suffix}/next",
    response_model=PascalShowcaseNextResponse,
)
async def get_python_showcase_next(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseNextResponse:
    from application.curriculum.chapters.curriculum_chapter_meta_service import chapter_key_for_route_suffix
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_python
    from application.curriculum.python.showcase.python_v311_registry import v311_collection_by_key
    from application.curriculum.python.showcase.python_showcase_next import (
        build_python_v311_showcase_collection_next,
    )

    chapter_key = chapter_key_for_route_suffix(
        db,
        "python",
        route_suffix,
        registry_lookup=route_suffix_to_chapter_key_python,
    )
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    if v311_collection_by_key(chapter_key) is not None or chapter_key == route_suffix:
        return build_python_v311_showcase_collection_next(db, chapter_key, user_id)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")


@router.get(
    "/python/showcase/{route_suffix}/student",
    response_model=PascalShowcaseStudentViewResponse,
)
async def get_python_showcase_student(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseStudentViewResponse:
    from application.curriculum.chapters.curriculum_chapter_meta_service import chapter_key_for_route_suffix
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_python
    from application.curriculum.python.showcase.python_showcase_student import build_python_showcase_student_view

    chapter_key = chapter_key_for_route_suffix(
        db,
        "python",
        route_suffix,
        registry_lookup=route_suffix_to_chapter_key_python,
    )
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    return build_python_showcase_student_view(db, chapter_key, user_id=user_id)


@router.get(
    "/python/showcase/{route_suffix}",
    response_model=PascalShowcaseTasksListResponse,
)
async def get_python_showcase_tasks(route_suffix: str, db: Session = Depends(get_db)) -> PascalShowcaseTasksListResponse:
    from application.curriculum.chapters.curriculum_chapter_meta_service import chapter_key_for_route_suffix
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_python
    from application.curriculum.python.showcase.python_showcase_core import list_showcase_tasks_for_collection
    from application.curriculum.python.showcase.python_v311_registry import v311_collection_by_key

    chapter_key = chapter_key_for_route_suffix(
        db,
        "python",
        route_suffix,
        registry_lookup=route_suffix_to_chapter_key_python,
    )
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    col = v311_collection_by_key(chapter_key)
    return {
        "collection_key": chapter_key,
        "learning_concept_id": col.yaml_chapter_id if col else chapter_key,
        "language": "python",
        "tasks": list_showcase_tasks_for_collection(db, chapter_key, curriculum_version="1.0"),
    }


@router.get(
    "/cpp/showcase/{route_suffix}/next",
    response_model=PascalShowcaseNextResponse,
)
async def get_cpp_showcase_next(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseNextResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_cpp
    from application.curriculum.cpp.showcase.cpp_v311_registry import v311_collection_by_key
    from application.curriculum.cpp.showcase.cpp_showcase_next import build_cpp_v311_showcase_collection_next

    chapter_key = route_suffix_to_chapter_key_cpp(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    if v311_collection_by_key(chapter_key) is not None:
        return build_cpp_v311_showcase_collection_next(db, chapter_key, user_id)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")


@router.get(
    "/cpp/showcase/{route_suffix}/student",
    response_model=PascalShowcaseStudentViewResponse,
)
async def get_cpp_showcase_student(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseStudentViewResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_cpp
    from application.curriculum.cpp.showcase.cpp_showcase_student import build_cpp_showcase_student_view

    chapter_key = route_suffix_to_chapter_key_cpp(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    return build_cpp_showcase_student_view(db, chapter_key, user_id=user_id)


@router.get(
    "/cpp/showcase/{route_suffix}",
    response_model=PascalShowcaseTasksListResponse,
)
async def get_cpp_showcase_tasks(route_suffix: str, db: Session = Depends(get_db)) -> PascalShowcaseTasksListResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_cpp
    from application.curriculum.cpp.showcase.cpp_showcase_core import list_cpp_tasks_for_collection
    from application.curriculum.cpp.showcase.cpp_v311_registry import v311_collection_by_key

    chapter_key = route_suffix_to_chapter_key_cpp(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    col = v311_collection_by_key(chapter_key)
    return {
        "collection_key": chapter_key,
        "learning_concept_id": col.yaml_chapter_id if col else chapter_key,
        "language": "cpp",
        "tasks": list_cpp_tasks_for_collection(db, chapter_key),
    }


@router.get(
    "/csharp/showcase/{route_suffix}/next",
    response_model=PascalShowcaseNextResponse,
)
async def get_csharp_showcase_next(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseNextResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_csharp
    from application.curriculum.csharp.showcase.csharp_v311_registry import v311_collection_by_key
    from application.curriculum.csharp.showcase.csharp_showcase_next import build_csharp_v311_showcase_collection_next

    chapter_key = route_suffix_to_chapter_key_csharp(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    if v311_collection_by_key(chapter_key) is not None:
        return build_csharp_v311_showcase_collection_next(db, chapter_key, user_id)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")


@router.get(
    "/csharp/showcase/{route_suffix}/student",
    response_model=PascalShowcaseStudentViewResponse,
)
async def get_csharp_showcase_student(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseStudentViewResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_csharp
    from application.curriculum.csharp.showcase.csharp_showcase_student import build_csharp_showcase_student_view

    chapter_key = route_suffix_to_chapter_key_csharp(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    return build_csharp_showcase_student_view(db, chapter_key, user_id=user_id)


@router.get(
    "/csharp/showcase/{route_suffix}",
    response_model=PascalShowcaseTasksListResponse,
)
async def get_csharp_showcase_tasks(route_suffix: str, db: Session = Depends(get_db)) -> PascalShowcaseTasksListResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_csharp
    from application.curriculum.csharp.showcase.csharp_showcase_core import list_csharp_tasks_for_collection
    from application.curriculum.csharp.showcase.csharp_v311_registry import v311_collection_by_key

    chapter_key = route_suffix_to_chapter_key_csharp(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    col = v311_collection_by_key(chapter_key)
    return {
        "collection_key": chapter_key,
        "learning_concept_id": col.yaml_chapter_id if col else chapter_key,
        "language": "csharp",
        "tasks": list_csharp_tasks_for_collection(db, chapter_key),
    }


@router.get(
    "/java/showcase/{route_suffix}/next",
    response_model=PascalShowcaseNextResponse,
)
async def get_java_showcase_next(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseNextResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_java
    from application.curriculum.java.showcase.java_v311_registry import v311_collection_by_key
    from application.curriculum.java.showcase.java_showcase_next import build_java_v311_showcase_collection_next

    chapter_key = route_suffix_to_chapter_key_java(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    if v311_collection_by_key(chapter_key) is not None:
        return build_java_v311_showcase_collection_next(db, chapter_key, user_id)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")


@router.get(
    "/java/showcase/{route_suffix}/student",
    response_model=PascalShowcaseStudentViewResponse,
)
async def get_java_showcase_student(
    route_suffix: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseStudentViewResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_java
    from application.curriculum.java.showcase.java_showcase_student import build_java_showcase_student_view

    chapter_key = route_suffix_to_chapter_key_java(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    user_id = current_user.id if current_user else None
    return build_java_showcase_student_view(db, chapter_key, user_id=user_id)


@router.get(
    "/java/showcase/{route_suffix}",
    response_model=PascalShowcaseTasksListResponse,
)
async def get_java_showcase_tasks(route_suffix: str, db: Session = Depends(get_db)) -> PascalShowcaseTasksListResponse:
    from application.curriculum.collections.curriculum_collections_registry import route_suffix_to_chapter_key_java
    from application.curriculum.java.showcase.java_showcase_core import list_java_tasks_for_collection
    from application.curriculum.java.showcase.java_v311_registry import v311_collection_by_key

    chapter_key = route_suffix_to_chapter_key_java(route_suffix)
    if chapter_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown showcase collection")
    col = v311_collection_by_key(chapter_key)
    return {
        "collection_key": chapter_key,
        "learning_concept_id": col.yaml_chapter_id if col else chapter_key,
        "language": "java",
        "tasks": list_java_tasks_for_collection(db, chapter_key),
    }


@router.get(
    "/pascal/showcase/conditions/next",
    response_model=PascalShowcaseNextResponse,
)
async def get_pascal_conditions_showcase_next(
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseNextResponse:
    from application.curriculum.collections.curriculum_next_service import build_pascal_conditions_showcase_next

    user_id = current_user.id if current_user else None
    return build_pascal_conditions_showcase_next(db, user_id)


@router.get(
    "/pascal/showcase/conditions/student",
    response_model=PascalShowcaseStudentViewResponse,
)
async def get_pascal_conditions_showcase_student(
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseStudentViewResponse:
    from application.curriculum.pascal.legacy.conditions.conditions_showcase_student import build_pascal_conditions_showcase_student_view

    user_id = current_user.id if current_user else None
    return build_pascal_conditions_showcase_student_view(db, user_id=user_id)


@router.get(
    "/pascal/showcase/conditions",
    response_model=PascalShowcaseTasksListResponse,
)
async def get_pascal_conditions_showcase_tasks(db: Session = Depends(get_db)) -> PascalShowcaseTasksListResponse:
    from application.curriculum.pascal.legacy.conditions.conditions_showcase_seeder import list_showcase_tasks as list_conditions_tasks

    return {
        "learning_concept_id": "conditions",
        "language": "pascal",
        "tasks": list_conditions_tasks(db),
    }


@router.get(
    "/pascal/showcase/loops/next",
    response_model=PascalShowcaseNextResponse,
)
async def get_pascal_loops_showcase_next(
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseNextResponse:
    from application.curriculum.collections.curriculum_next_service import build_pascal_loops_showcase_next

    user_id = current_user.id if current_user else None
    return build_pascal_loops_showcase_next(db, user_id)


@router.get(
    "/pascal/showcase/loops/student",
    response_model=PascalShowcaseStudentViewResponse,
)
async def get_pascal_loops_showcase_student(
    db: Session = Depends(get_db),
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
) -> PascalShowcaseStudentViewResponse:
    from application.curriculum.pascal.legacy.loops.loops_showcase_student import build_pascal_loops_showcase_student_view

    user_id = current_user.id if current_user else None
    return build_pascal_loops_showcase_student_view(db, user_id=user_id)


@router.get(
    "/pascal/showcase/loops",
    response_model=PascalShowcaseTasksListResponse,
)
async def get_pascal_loops_showcase_tasks(db: Session = Depends(get_db)) -> PascalShowcaseTasksListResponse:
    return {
        "learning_concept_id": "loops",
        "language": "pascal",
        "tasks": list_showcase_tasks(db),
    }


@router.get("/{language}", response_model=CurriculumSummaryResponse)
async def get_curriculum(language: str) -> CurriculumSummaryResponse:
    try:
        payload = _service(language).get_curriculum_summary(language)
        return CurriculumSummaryResponse(**payload)
    except (CurriculumNotFoundError, CurriculumValidationError) as exc:
        raise _handle_curriculum_error(exc) from exc


@router.get("/{language}/concepts", response_model=list[LearningConceptResponse])
async def list_learning_concepts(language: str) -> list[LearningConceptResponse]:
    try:
        items = _service(language).get_learning_concepts(language)
        return [_lc_response(lc) for lc in items]
    except (CurriculumNotFoundError, CurriculumValidationError) as exc:
        raise _handle_curriculum_error(exc) from exc


@router.get(
    "/{language}/concepts/{learning_concept_id}",
    response_model=LearningConceptDetailResponse,
)
async def get_learning_concept(
    language: str,
    learning_concept_id: str,
) -> LearningConceptDetailResponse:
    try:
        svc = _service(language)
        payload = svc.get_learning_concept_detail(language, learning_concept_id)
        lc = svc.get_bundle().learning_concept_by_id(learning_concept_id)
        if lc is None:
            raise CurriculumNotFoundError(f"Unknown learning concept: {learning_concept_id}")
        return LearningConceptDetailResponse(
            learning_concept=_lc_response(lc),
            prerequisites=payload["prerequisites"],
            study_order_tc=payload["study_order_tc"],
            technical_concepts=[
                TechnicalConceptInChapterResponse(**tc) for tc in payload["technical_concepts"]
            ],
        )
    except (CurriculumNotFoundError, CurriculumValidationError) as exc:
        raise _handle_curriculum_error(exc) from exc


@router.get(
    "/{language}/technical-concepts/{technical_concept_id}/patterns",
    response_model=TechnicalConceptPatternsResponse,
)
async def get_technical_concept_patterns(
    language: str,
    technical_concept_id: str,
    action: str | None = Query(default=None),
) -> TechnicalConceptPatternsResponse:
    try:
        svc = _service(language)
        mask = svc.get_action_mask(language, technical_concept_id)
        patterns = svc.get_exercise_patterns(language, technical_concept_id, action)
        patterns_by_action: dict[str, list[ExercisePatternResponse]] = {}
        for act in mask.active_actions():
            patterns_by_action[act] = [
                _pattern_response(p)
                for p in svc.get_exercise_patterns(language, technical_concept_id, act)
            ]
        return TechnicalConceptPatternsResponse(
            technical_concept_id=technical_concept_id,
            action_mask=_mask_response(mask),
            patterns=[_pattern_response(p) for p in patterns],
            patterns_by_action=patterns_by_action,
        )
    except (CurriculumNotFoundError, CurriculumValidationError) as exc:
        raise _handle_curriculum_error(exc) from exc


@router.get("/{language}/validate", response_model=CurriculumValidationResponse)
async def validate_curriculum(language: str) -> CurriculumValidationResponse:
    try:
        payload = _service(language).validate_curriculum(language)
        return CurriculumValidationResponse(**payload)
    except CurriculumNotFoundError as exc:
        raise _handle_curriculum_error(exc) from exc


