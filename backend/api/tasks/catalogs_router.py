from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies.authorization import require_permission
from api.dependencies.catalogs import (
    get_catalog_assignment_service,
    get_catalog_service,
    get_task_service,
)
from api.mappers.catalogs import to_catalog_response, to_task_response
from application.tasks.use_cases.assign_task_to_chapter import assign_task_to_chapter
from application.tasks.use_cases.chapter_task_order import update_chapter_task_order
from application.tasks.use_cases.collection_chapter_order import update_collection_chapter_order
from api.tasks.catalog_schemas import (
    AssignTaskRequest,
    AssignCourseToCatalogRequest,
    AssignTaskChapterRequest,
    AssignTaskChapterResponse,
    CatalogResponse,
    ChapterResponse,
    ChapterTaskOrderRequest,
    CollectionChapterOrderRequest,
    CollectionMetaResponse,
    CreateCatalogRequest,
    CreateChapterRequest,
    CreateTeacherCourseRequest,
    CreateTaskInCatalogRequest,
    CreateTaskRequest,
    TaskResponse,
    TaskRetireResponse,
    TeacherCourseResponse,
    UpdateChapterRequest,
    UpdateCollectionMetaRequest,
    UpdatePlatformCourseMetaRequest,
    UpdateTeacherCourseRequest,
    PlatformCourseMetaResponse,
    UpdateTaskWorkflowRequest,
)
from application.tasks.services.catalog.catalog_assignment_service import CatalogAssignmentService
from application.tasks.services.catalog.catalog_service import CatalogService
from application.tasks.services.catalog.task_service import TaskService
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission
from shared.exceptions import (
    AccessDeniedToContentError,
    CatalogNotFoundError,
    TaskAlreadyAssignedError,
    TaskNotFoundError,
)
from infrastructure.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


def _task_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, TaskNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, AccessDeniedToContentError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, CatalogNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, TaskAlreadyAssignedError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    raise exc


def _is_admin(current: CurrentUserResult) -> bool:
    from domain.policies.rbac.rbac import normalize_role
    from shared.enums import UserType

    roles = frozenset(normalize_role(role) for role in current.roles)
    return UserType.ADMIN in roles


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    body: CreateTaskRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    task_service: TaskService = Depends(get_task_service),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    """FLOW A step 1: create standalone task (no catalog assignment)."""
    task = task_service.create_task(
        title=body.title,
        content=body.content,
        topic_id=body.topic_id,
        type_id=body.type_id,
        teacher_id=current.id,
    )
    catalog_ids = assignment_service.catalog_ids_for_task(task.id)
    return to_task_response(task, catalog_ids=catalog_ids)


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    assigned: bool | None = Query(default=None),
    current: CurrentUserResult = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    task_service: TaskService = Depends(get_task_service),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    tasks = task_service.list_tasks(current.id)
    result: list[TaskResponse] = []
    for task in tasks:
        catalog_ids = assignment_service.catalog_ids_for_task(task.id)
        is_assigned = bool(catalog_ids)
        if assigned is True and not is_assigned:
            continue
        if assigned is False and is_assigned:
            continue
        result.append(to_task_response(task, catalog_ids=catalog_ids))
    return result


@router.put("/tasks/chapter-order")
def update_tasks_chapter_order(
    body: ChapterTaskOrderRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    try:
        ordered = update_chapter_task_order(
            db,
            teacher_id=current.id,
            chapter_key=body.chapter_key,
            task_ids=body.task_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"chapter_key": body.chapter_key, "task_ids": ordered}


@router.put("/tasks/collection-chapter-order")
def update_tasks_collection_chapter_order(
    body: CollectionChapterOrderRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    try:
        ordered = update_collection_chapter_order(
            db,
            teacher_id=current.id,
            chapter_keys=body.chapter_keys,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"chapter_keys": ordered}


@router.get("/chapters", response_model=list[ChapterResponse])
def list_curriculum_chapters(
    language: str | None = Query(default=None),
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        chapter_record_to_dict,
        list_chapters,
    )

    return [
        ChapterResponse(**chapter_record_to_dict(item))
        for item in list_chapters(db, language=language)
    ]


@router.post("/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_curriculum_chapter(
    body: CreateChapterRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        chapter_record_to_dict,
        count_tasks_for_chapter,
        create_chapter,
        list_chapters,
    )

    try:
        row = create_chapter(
            db,
            teacher_id=current.id,
            language=body.language.strip().lower(),
            title=body.title,
            description=body.description,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    record = next(
        (item for item in list_chapters(db, language=body.language.strip().lower()) if item.chapter_key == row.chapter_key),
        None,
    )
    if record is None:
        record_data = {
            "language": row.language,
            "chapter_key": row.chapter_key,
            "title": row.title,
            "description": row.description,
            "sort_order": row.sort_order,
            "is_custom": row.is_custom,
            "task_count": count_tasks_for_chapter(db, row.chapter_key),
            "registry_title": None,
            "updated_at": row.updated_at,
        }
        return ChapterResponse(**record_data)
    return ChapterResponse(**chapter_record_to_dict(record))


@router.put("/chapters/{chapter_key}", response_model=ChapterResponse)
def update_curriculum_chapter(
    chapter_key: str,
    body: UpdateChapterRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        chapter_record_to_dict,
        list_chapters,
        upsert_chapter,
    )

    try:
        upsert_chapter(
            db,
            teacher_id=current.id,
            language=body.language.strip().lower(),
            chapter_key=chapter_key,
            title=body.title,
            description=body.description,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    record = next(
        (item for item in list_chapters(db, language=body.language.strip().lower() or None) if item.chapter_key == chapter_key),
        None,
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return ChapterResponse(**chapter_record_to_dict(record))


@router.get("/collections", response_model=list[CollectionMetaResponse])
def list_curriculum_collections_meta(
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import list_collection_meta

    return [CollectionMetaResponse(**item) for item in list_collection_meta(db)]


@router.put("/collections/{language}", response_model=CollectionMetaResponse)
def update_curriculum_collection_meta(
    language: str,
    body: UpdateCollectionMetaRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        list_collection_meta,
        upsert_collection_meta,
    )

    lang = language.strip().lower()
    try:
        upsert_collection_meta(
            db,
            teacher_id=current.id,
            language=lang,
            title=body.title,
            description=body.description,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    record = next((item for item in list_collection_meta(db) if item["language"] == lang), None)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return CollectionMetaResponse(**record)


@router.get("/platform-course", response_model=PlatformCourseMetaResponse)
def get_platform_course_meta(
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import get_platform_course_meta

    return PlatformCourseMetaResponse(**get_platform_course_meta(db))


@router.put("/platform-course", response_model=PlatformCourseMetaResponse)
def update_platform_course_meta(
    body: UpdatePlatformCourseMetaRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        get_platform_course_meta,
        upsert_platform_course_meta,
    )

    try:
        upsert_platform_course_meta(
            db,
            teacher_id=current.id,
            title=body.title,
            description=body.description,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PlatformCourseMetaResponse(**get_platform_course_meta(db))


@router.get("/courses", response_model=list[TeacherCourseResponse])
def list_teacher_courses(
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_courses_meta_service import list_teacher_courses

    return [TeacherCourseResponse(**item) for item in list_teacher_courses(db, teacher_id=current.id)]


@router.post("/courses", response_model=TeacherCourseResponse, status_code=status.HTTP_201_CREATED)
def create_teacher_course(
    body: CreateTeacherCourseRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_courses_meta_service import create_teacher_course

    try:
        row = create_teacher_course(
            db,
            teacher_id=current.id,
            title=body.title,
            description=body.description,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TeacherCourseResponse(**row)


@router.put("/courses/{course_id}", response_model=TeacherCourseResponse)
def update_teacher_course(
    course_id: int,
    body: UpdateTeacherCourseRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_courses_meta_service import update_teacher_course
    from shared.exceptions import AccessDeniedToContentError

    try:
        row = update_teacher_course(
            db,
            teacher_id=current.id,
            course_id=course_id,
            title=body.title,
            description=body.description,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AccessDeniedToContentError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TeacherCourseResponse(**row)


@router.get("/{catalog_id}/courses", response_model=list[TeacherCourseResponse])
def list_catalog_courses(
    catalog_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_courses_meta_service import list_catalog_courses
    from shared.exceptions import CatalogNotFoundError

    try:
        rows = list_catalog_courses(db, teacher_id=current.id, catalog_id=catalog_id)
    except CatalogNotFoundError as exc:
        raise _task_http_error(exc) from exc
    return [TeacherCourseResponse(**item) for item in rows]


@router.post("/{catalog_id}/courses", status_code=status.HTTP_204_NO_CONTENT)
def add_course_to_catalog(
    catalog_id: int,
    body: AssignCourseToCatalogRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_courses_meta_service import add_course_to_catalog
    from shared.exceptions import AccessDeniedToContentError, CatalogNotFoundError

    try:
        add_course_to_catalog(
            db,
            teacher_id=current.id,
            catalog_id=catalog_id,
            course_id=body.course_id,
        )
        db.commit()
    except (CatalogNotFoundError, AccessDeniedToContentError) as exc:
        db.rollback()
        raise _task_http_error(exc) from exc


@router.delete("/{catalog_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_course_from_catalog(
    catalog_id: int,
    course_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_courses_meta_service import remove_course_from_catalog
    from shared.exceptions import AccessDeniedToContentError, CatalogNotFoundError

    try:
        remove_course_from_catalog(
            db,
            teacher_id=current.id,
            catalog_id=catalog_id,
            course_id=course_id,
        )
        db.commit()
    except (CatalogNotFoundError, AccessDeniedToContentError) as exc:
        db.rollback()
        raise _task_http_error(exc) from exc


@router.post(
    "/tasks/{task_id}/chapter-placement",
    response_model=AssignTaskChapterResponse,
    status_code=status.HTTP_200_OK,
)
def assign_task_chapter_placement(
    task_id: int,
    body: AssignTaskChapterRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    try:
        result = assign_task_to_chapter(
            db,
            teacher_id=current.id,
            task_id=task_id,
            language=body.language,
            chapter_key=body.chapter_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AssignTaskChapterResponse(**result)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    task_service: TaskService = Depends(get_task_service),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    try:
        task = task_service.get_task(task_id)
        catalog_ids = assignment_service.catalog_ids_for_task(task.id)
        return to_task_response(task, catalog_ids=catalog_ids)
    except TaskNotFoundError as exc:
        raise _task_http_error(exc) from exc


@router.delete("/tasks/{task_id}", response_model=TaskRetireResponse)
def delete_task(
    task_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_task_lifecycle import retire_task

    try:
        result = retire_task(
            db,
            task_id=task_id,
            teacher_id=current.id,
            is_admin=_is_admin(current),
        )
        db.commit()
    except (TaskNotFoundError, AccessDeniedToContentError) as exc:
        db.rollback()
        raise _task_http_error(exc) from exc
    return TaskRetireResponse(
        action=result.action,
        task_id=result.task_id,
        submissions_count=result.submissions_count,
    )


@router.put("/tasks/{task_id}/workflow", response_model=TaskRetireResponse)
def update_task_workflow(
    task_id: int,
    body: UpdateTaskWorkflowRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.tasks.services.catalog.teacher_task_lifecycle import (
        count_task_submissions,
        set_teacher_task_workflow_status,
    )
    from shared.enums import AssignmentWorkflowStatus

    try:
        status = AssignmentWorkflowStatus(body.status.strip().lower())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workflow status") from exc

    try:
        set_teacher_task_workflow_status(
            db,
            task_id=task_id,
            teacher_id=current.id,
            status=status,
            is_admin=_is_admin(current),
        )
        db.commit()
    except (TaskNotFoundError, AccessDeniedToContentError) as exc:
        db.rollback()
        raise _task_http_error(exc) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return TaskRetireResponse(
        action="archived" if status == AssignmentWorkflowStatus.ARCHIVED else "active",
        task_id=task_id,
        submissions_count=count_task_submissions(db, task_id),
    )


@router.delete("/chapters/{chapter_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curriculum_chapter(
    chapter_key: str,
    language: str | None = Query(default=None, max_length=32),
    current: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    db: Session = Depends(get_db),
):
    from application.curriculum.chapters.curriculum_chapter_meta_service import delete_custom_chapter

    try:
        delete_custom_chapter(db, chapter_key=chapter_key, language=language)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("", response_model=CatalogResponse, status_code=status.HTTP_201_CREATED)
def create_catalog(
    body: CreateCatalogRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    catalog = catalog_service.create_catalog(
        title=body.title,
        description=body.description,
        teacher_id=current.id,
        visibility=body.visibility,
        group_id=body.group_id,
    )
    return to_catalog_response(catalog)


@router.get("/mine", response_model=list[CatalogResponse])
def list_my_catalogs(
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    catalog_service: CatalogService = Depends(get_catalog_service),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    catalogs = catalog_service.list_catalogs(current.id)
    return [
        to_catalog_response(
            catalog,
            task_count=len(assignment_service.get_tasks_by_catalog(catalog.id)),
        )
        for catalog in catalogs
    ]


@router.get("/{catalog_id}", response_model=CatalogResponse)
def get_catalog(
    catalog_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    catalog_service: CatalogService = Depends(get_catalog_service),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    try:
        catalog = catalog_service.get_catalog(catalog_id)
        task_count = len(assignment_service.get_tasks_by_catalog(catalog.id))
        return to_catalog_response(catalog, task_count=task_count)
    except CatalogNotFoundError as exc:
        raise _task_http_error(exc) from exc


@router.delete("/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_catalog(
    catalog_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    try:
        catalog_service.delete_catalog(catalog_id)
    except CatalogNotFoundError as exc:
        raise _task_http_error(exc) from exc


@router.get("/{catalog_id}/tasks", response_model=list[TaskResponse])
def get_catalog_tasks(
    catalog_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    try:
        tasks = assignment_service.get_tasks_by_catalog(catalog_id)
        return [
            to_task_response(task, catalog_ids=[catalog_id]) for task in tasks
        ]
    except CatalogNotFoundError as exc:
        raise _task_http_error(exc) from exc


@router.post("/{catalog_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_in_catalog(
    catalog_id: int,
    body: CreateTaskInCatalogRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.CREATE_ASSIGNMENTS)),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    """FLOW B: create task inside catalog context (create + assign)."""
    try:
        task = assignment_service.create_task_in_catalog_context(
            catalog_id=catalog_id,
            title=body.title,
            content=body.content,
            topic_id=body.topic_id,
            type_id=body.type_id,
            teacher_id=current.id,
        )
        return to_task_response(task, catalog_ids=[catalog_id])
    except CatalogNotFoundError as exc:
        raise _task_http_error(exc) from exc


@router.post("/{catalog_id}/assignments", status_code=status.HTTP_204_NO_CONTENT)
def assign_existing_task(
    catalog_id: int,
    body: AssignTaskRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    """FLOW A step 2: assign an existing task to a catalog."""
    try:
        assignment_service.assign_task_to_catalog(body.task_id, catalog_id)
    except (TaskNotFoundError, CatalogNotFoundError, TaskAlreadyAssignedError) as exc:
        raise _task_http_error(exc) from exc


@router.delete("/{catalog_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task_from_catalog(
    catalog_id: int,
    task_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    assignment_service: CatalogAssignmentService = Depends(get_catalog_assignment_service),
):
    try:
        assignment_service.remove_task_from_catalog(task_id, catalog_id)
    except TaskNotFoundError as exc:
        raise _task_http_error(exc) from exc
