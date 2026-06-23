from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session

from application.tasks.services.flowchart_authoring import validate_flowchart_assignment
from application.tasks.services.flowchart_diagram_storage import merge_diagram_into_flow_spec
from application.tasks.services.task_id_allocator import allocate_next_task_id
from application.tasks.use_cases.block_reorder.create import create_block_reorder_task
from shared.enums import AssignmentType
from shared.enums import Difficulty, TaskType
from shared.language import parse_language
from domain.entities.tasks.translation_task import TranslationTask
from application.tasks.services.task_patterns import apply_patterns_and_tests
from infrastructure.db.models.task import (
    Task as TaskModel,
    TranslationTask as TranslationTaskModel,
)


def create_build_from_blocks_handler(db: Session, **kwargs: Any) -> dict[str, Any]:
    assignment_type = kwargs.pop("assignment_type", AssignmentType.TASK_BUILD_FROM_BLOCKS.value)
    result = create_block_reorder_task(
        db,
        title=kwargs["title"],
        description=kwargs["description"],
        difficulty=kwargs["difficulty"],
        original_code=kwargs["original_code"],
        template=kwargs.get("template"),
        language=kwargs["language"],
        language_variants=kwargs.get("language_variants"),
        teacher_id=kwargs["teacher_id"],
        blocks=kwargs.get("blocks"),
        correct_order=kwargs.get("correct_order"),
        assignment_type=assignment_type,
        test_cases=kwargs.get("test_cases"),
    )
    task_id = result.get("task_id") or result.get("id")
    if task_id:
        row = db.get(TaskModel, task_id)
        if row is not None:
            apply_patterns_and_tests(
                row,
                patterns=kwargs.get("patterns"),
                test_cases=kwargs.get("test_cases"),
            )
            db.commit()
    result["assignment_type"] = assignment_type
    result["type"] = assignment_type
    return result


def create_translation_handler(db: Session, **kwargs: Any) -> dict[str, Any]:
    assignment_type = kwargs.pop("assignment_type", AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value)
    source_language = parse_language(kwargs["source_language"])
    task = TranslationTask.create(
        teacher_id=kwargs["teacher_id"],
        title=kwargs["title"],
        description=kwargs["description"],
        difficulty=Difficulty(kwargs["difficulty"]),
        task_type=TaskType.TRANSLATION,
        source_language=source_language,
        source_code=kwargs["source_code"],
    )
    source_code = str(kwargs.get("source_code") or "").strip()
    task_id = allocate_next_task_id(db)
    db.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=task.teacher_id,
            title=task.title,
            description=task.description,
            difficulty=task.difficulty.value,
            task_type=assignment_type,
            test_cases=[],
            code_examples={source_language: source_code} if source_code else {},
            flow_spec={},
        )
    )
    db.execute(
        sa.insert(TranslationTaskModel.__table__).values(
            task_id=task_id,
            source_code=task.source_code,
            source_language=source_language,
        )
    )
    task_model = db.get(TaskModel, task_id)
    if task_model is None:
        raise RuntimeError("Failed to create translation task row")
    apply_patterns_and_tests(
        task_model,
        patterns=kwargs.get("patterns"),
        test_cases=kwargs.get("test_cases"),
    )
    db.commit()
    db.refresh(task_model)
    return {
        "task_id": task_model.id,
        "id": task_model.id,
        "assignment_type": assignment_type,
        "type": assignment_type,
        "languages": [source_language, *kwargs.get("target_languages", [])],
    }


def create_flowchart_handler(db: Session, **kwargs: Any) -> dict[str, Any]:
    assignment_type = kwargs.pop("assignment_type", AssignmentType.TASK_FLOWCHART_TO_CODE.value)
    diagram = kwargs["diagram"]
    diagram_payload = diagram if isinstance(diagram, dict) else {"spec": diagram}
    reference_code = str(kwargs.get("reference_code") or "").strip()
    expose_reference_code = bool(kwargs.get("expose_reference_code"))
    language = str(kwargs.get("language") or kwargs.get("primary_language") or "python")
    validate_flowchart_assignment(
        diagram=diagram_payload,
        reference_code=reference_code,
        expose_reference_code=expose_reference_code,
    )
    from application.tasks.use_cases.flowchart.task import _merge_flow_spec

    flow_spec = merge_diagram_into_flow_spec(
        _merge_flow_spec(
            kwargs.get("flow_spec") if isinstance(kwargs.get("flow_spec"), dict) else None,
            language=language,
            reference_code=reference_code,
            expose_reference_code=expose_reference_code,
        ),
        diagram_payload,
    )
    task_id = allocate_next_task_id(db)
    db.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=kwargs["teacher_id"],
            title=kwargs["title"],
            description=kwargs["description"],
            difficulty=Difficulty(kwargs["difficulty"]).value,
            task_type=assignment_type,
            test_cases=[],
            code_examples={},
            flow_spec=flow_spec,
        )
    )
    task_model = db.get(TaskModel, task_id)
    if task_model is None:
        raise RuntimeError("Failed to create flowchart task row")
    if reference_code:
        examples = dict(task_model.code_examples or {})
        examples[str(language).lower()] = reference_code
        task_model.code_examples = examples
    apply_patterns_and_tests(
        task_model,
        patterns=kwargs.get("patterns"),
        test_cases=kwargs.get("test_cases"),
    )
    db.commit()
    db.refresh(task_model)
    return {
        "task_id": task_model.id,
        "id": task_model.id,
        "assignment_type": assignment_type,
        "type": "blocks",
        "task_type": assignment_type,
    }
