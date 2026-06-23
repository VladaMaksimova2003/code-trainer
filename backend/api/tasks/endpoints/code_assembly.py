"""Code-assembly task endpoints (create, read, update, validate)."""
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from application.auth.dto import CurrentUserResult
from application.tasks.services.block_reorder_helpers import build_shuffled_blocks
from application.tasks.use_cases.block_reorder.create import create_block_reorder_task
from application.tasks.use_cases.block_reorder.get import (
    get_block_reorder_authoring_payload,
    get_block_reorder_public_task,
)
from application.tasks.use_cases.block_reorder.validate import validate_block_reorder_solution
from application.tasks.services.task_patterns import apply_patterns_and_tests
from application.tasks.services.task_editor_type_migration import ensure_task_supports_assignment_type
from application.tasks.services.teacher_assembly_preservation import mark_teacher_assembly_override
from application.tasks.services.teacher_editor_activity_sync import sync_teacher_editor_activity_metadata
from application.users.services.teacher_activity_service import record_teacher_activity
from api.tasks.schemas.requests import BlockReorderCreateRequest, BlockReorderSolutionRequest
from api.dependencies.authorization import require_permission
from domain.policies.permissions.permissions import Permission
from domain.policies.rbac.role import normalized_role_key
from infrastructure.db.session import get_db
from infrastructure.db.models.task import BlockReorderTask as BlockReorderTaskModel, Task as TaskModel

router = APIRouter(prefix="/code-assembly")


@router.post("")
async def create_code_assembly(
    request: BlockReorderCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.CREATE_ASSIGNMENTS)
    ),
):
    """Create a code assembly task (shared model with block reorder)."""
    created = create_block_reorder_task(
        db, title=request.title, description=request.description,
        difficulty=request.difficulty, original_code=request.original_code,
        template=request.template, language=request.language,
        language_variants=request.language_variants, teacher_id=current_user.id,
        blocks=request.blocks, correct_order=request.correct_order,
        test_cases=request.test_cases,
    )
    created["type"] = "code_assembly"
    created["task_type"] = "code_assembly"
    return created


@router.get("/{task_id}")
async def get_code_assembly(task_id: int, db: Session = Depends(get_db)):
    task = get_block_reorder_public_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Code assembly task not found")
    task["type"] = "code_assembly"
    task["task_type"] = "code_assembly"
    return task


@router.get("/{task_id}/author")
async def get_code_assembly_author(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.EDIT_ASSIGNMENTS)
    ),
):
    task_row = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task_row or task_row.is_delete:
        raise HTTPException(status_code=404, detail="Task not found")
    roles = frozenset(normalized_role_key(r) for r in current_user.roles)
    if "TEACHER" in roles and "ADMIN" not in roles:
        if task_row.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view authoring data for your own tasks.")
    payload = get_block_reorder_authoring_payload(db, task_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Code assembly task not found")
    return payload


@router.put("/{task_id}")
async def update_code_assembly(
    task_id: int,
    request: BlockReorderCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.EDIT_ASSIGNMENTS)
    ),
):
    task_row = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task_row or task_row.is_delete:
        raise HTTPException(status_code=404, detail="Code assembly task not found")
    roles = frozenset(normalized_role_key(r) for r in current_user.roles)
    if "TEACHER" in roles and "ADMIN" not in roles:
        if task_row.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only edit your own tasks.")
    effective_teacher_id = task_row.teacher_id or current_user.id
    if request.task_type:
        ensure_task_supports_assignment_type(
            db,
            task_row,
            request.task_type,
            language=request.language,
            source_code=request.original_code,
        )
        db.refresh(task_row)
    existing = get_block_reorder_public_task(db, task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Code assembly task not found")
    task_row.title = request.title
    task_row.description = request.description
    task_row.difficulty = request.difficulty
    task_row.test_cases = request.test_cases
    if request.task_type:
        task_row.task_type = request.task_type
    apply_patterns_and_tests(
        task_row,
        patterns=request.patterns,
        patterns_by_language=request.patterns_by_language,
        test_cases=request.test_cases,
    )
    sync_teacher_editor_activity_metadata(
        task_row,
        task_type=request.task_type or task_row.task_type,
        is_debug_task=False,
    )
    relation = (
        db.query(BlockReorderTaskModel)
        .filter(BlockReorderTaskModel.task_id == task_id)
        .first()
    )
    if not relation:
        raise HTTPException(status_code=404, detail="Code assembly task relation not found")
    from application.tasks.use_cases.block_reorder.get import _merge_teacher_language_variant

    code_changed = relation.original_code != request.original_code
    relation.original_code = request.original_code
    relation.language = request.language
    assembly_provided = (
        request.template is not None
        or request.blocks is not None
        or request.correct_order is not None
        or request.language_variants is not None
    )
    if assembly_provided:
        if request.template is not None:
            relation.template = request.template
        if request.blocks is not None:
            relation.blocks = request.blocks
        if request.correct_order is not None:
            relation.correct_order = request.correct_order
    elif code_changed:
        generated_blocks, generated_order = build_shuffled_blocks(request.original_code)
        relation.template = None
        relation.blocks = generated_blocks
        relation.correct_order = generated_order

    if request.language_variants is not None:
        merged: dict[str, Any] = {}
        for lang, raw in dict(relation.language_variants or {}).items():
            merged[str(lang).lower()] = dict(raw) if isinstance(raw, dict) else raw
        for lang, raw in request.language_variants.items():
            lang_key = str(lang).lower()
            if isinstance(raw, dict):
                merged[lang_key] = {**dict(merged.get(lang_key) or {}), **dict(raw)}
            else:
                merged[lang_key] = raw
        relation.language_variants = merged
        lang_key = str(request.language or relation.language or "python").lower()
        variant = merged.get(lang_key)
        if isinstance(variant, dict):
            if variant.get("template") is not None:
                relation.template = variant.get("template")
            if variant.get("blocks") is not None:
                relation.blocks = list(variant.get("blocks") or [])
            if variant.get("correct_order") is not None:
                relation.correct_order = list(variant.get("correct_order") or [])
    else:
        _merge_teacher_language_variant(
            relation,
            language=request.language,
            original_code=request.original_code,
            template=relation.template,
            blocks=list(relation.blocks or []),
            correct_order=list(relation.correct_order or []),
        )
    mark_teacher_assembly_override(task_row)
    from application.curriculum.display.chapter_task_display_order import (
        sync_showcase_order_fields_across_mirror_group,
    )

    sync_showcase_order_fields_across_mirror_group(db, task_row)
    from application.tasks.services.task_version_service import record_task_version_after_edit

    db.flush()
    record_task_version_after_edit(db, task_id)
    db.commit()
    record_teacher_activity(db, effective_teacher_id, "edited_task")
    updated = get_block_reorder_public_task(db, task_id)
    updated["type"] = "code_assembly"
    updated["task_type"] = "code_assembly"
    return updated


@router.post("/{task_id}/validate")
async def validate_code_assembly(
    task_id: int,
    request: BlockReorderSolutionRequest,
    db: Session = Depends(get_db),
):
    result = validate_block_reorder_solution(
        db, task_id, request.order, request.language, request.indents,
        assembled_code=request.assembled_code,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Code assembly task not found")
    result["task_type"] = "code_assembly"
    return result
