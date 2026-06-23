"""Seed Pascal curriculum conditions showcase tasks + curriculum links."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.pascal.legacy.conditions.conditions_showcase_data import (
    LANGUAGE,
    LEARNING_CONCEPT_ID,
    SHOWCASE_GROUP,
    TITLE_PREFIX,
    ConditionsShowcaseTaskSpec,
    conditions_showcase_specs,
)
from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService
from application.tasks.services.assignment_creation_service import (
    create_build_from_blocks_handler,
    create_translation_handler,
)
from application.tasks.services.task_id_allocator import allocate_next_task_id
from application.tasks.services.task_patterns import apply_patterns_and_tests
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask as TranslationTaskModel


@dataclass
class SeedReport:
    created: list[str] = field(default_factory=list)
    linked: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "created": self.created,
            "linked": self.linked,
            "skipped": self.skipped,
            "errors": self.errors,
            "totals": {
                "created": len(self.created),
                "linked": len(self.linked),
                "skipped": len(self.skipped),
                "errors": len(self.errors),
            },
        }


def _showcase_meta(spec: ConditionsShowcaseTaskSpec) -> dict[str, str]:
    return {
        "group": SHOWCASE_GROUP,
        "slug": spec.slug,
        "learning_concept_id": LEARNING_CONCEPT_ID,
        "technical_concept_id": spec.technical_concept_id,
        "exercise_pattern_id": spec.exercise_pattern_id,
    }


def find_showcase_task_by_slug(session: Session, slug: str) -> TaskModel | None:
    rows = session.scalars(
        select(TaskModel).where(TaskModel.title.like(f"{TITLE_PREFIX}%"), TaskModel.is_delete.is_(False))
    ).all()
    for row in rows:
        examples = dict(row.code_examples or {})
        showcase = examples.get("curriculum_showcase") or {}
        if showcase.get("slug") == slug:
            return row
    return None


def _attach_showcase_meta(row: TaskModel, spec: ConditionsShowcaseTaskSpec) -> None:
    examples = dict(row.code_examples or {})
    examples["curriculum_showcase"] = _showcase_meta(spec)
    row.code_examples = examples


def _create_translation_to_pascal(
    session: Session,
    *,
    spec: ConditionsShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    result = create_translation_handler(
        session,
        assignment_type=spec.assignment_type,
        source_language=extra["source_language"],
        source_code=extra["source_code"],
        title=spec.title,
        description=spec.description,
        difficulty=spec.difficulty,
        teacher_id=teacher_id,
        test_cases=extra.get("test_cases"),
        patterns=[],
    )
    task_id = int(result["task_id"])
    row = session.get(TaskModel, task_id)
    if row is not None:
        _attach_showcase_meta(row, spec)
        session.flush()
    return task_id


def _create_block_reorder_pascal(
    session: Session,
    *,
    spec: ConditionsShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    result = create_build_from_blocks_handler(
        session,
        assignment_type=spec.assignment_type,
        language=extra["language"],
        original_code=extra["original_code"],
        template=extra.get("template"),
        blocks=extra.get("blocks"),
        correct_order=extra.get("correct_order"),
        title=spec.title,
        description=spec.description,
        difficulty=spec.difficulty,
        teacher_id=teacher_id,
        test_cases=extra.get("test_cases"),
        patterns=[],
    )
    task_id = int(result["task_id"])
    row = session.get(TaskModel, task_id)
    if row is not None:
        _attach_showcase_meta(row, spec)
        session.flush()
    return task_id


def _create_pascal_io_program(
    session: Session,
    *,
    spec: ConditionsShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    task_id = allocate_next_task_id(session)
    session.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=teacher_id,
            title=spec.title,
            description=spec.description,
            difficulty=spec.difficulty,
            task_type=spec.assignment_type,
            test_cases=[],
            code_examples={},
            flow_spec={"target_language": LANGUAGE},
        )
    )
    session.execute(
        sa.insert(TranslationTaskModel.__table__).values(
            task_id=task_id,
            source_code="",
            source_language="python",
        )
    )
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError("Failed to create Pascal IO showcase task")
    examples: dict[str, Any] = {}
    if extra.get("code_examples_pascal"):
        examples["pascal"] = extra["code_examples_pascal"]
    row.code_examples = examples
    _attach_showcase_meta(row, spec)
    apply_patterns_and_tests(row, patterns=[], test_cases=extra.get("test_cases"))
    session.flush()
    return task_id


def _create_pascal_debug_starter(
    session: Session,
    *,
    spec: ConditionsShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    task_id = allocate_next_task_id(session)
    starter = extra["starter_pascal"]
    session.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=teacher_id,
            title=spec.title,
            description=spec.description,
            difficulty=spec.difficulty,
            task_type=spec.assignment_type,
            test_cases=[],
            code_examples={"pascal": starter},
            flow_spec={"target_language": LANGUAGE},
        )
    )
    session.execute(
        sa.insert(TranslationTaskModel.__table__).values(
            task_id=task_id,
            source_code="",
            source_language="python",
        )
    )
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError("Failed to create Pascal debug showcase task")
    _attach_showcase_meta(row, spec)
    apply_patterns_and_tests(row, patterns=[], test_cases=extra.get("test_cases"))
    session.flush()
    return task_id


_BUILDERS = {
    "translation_to_pascal": _create_translation_to_pascal,
    "block_reorder_pascal": _create_block_reorder_pascal,
    "pascal_io_program": _create_pascal_io_program,
    "pascal_debug_starter": _create_pascal_debug_starter,
}


def _ensure_curriculum_link(
    session: Session,
    *,
    task_id: int,
    spec: ConditionsShowcaseTaskSpec,
    report: SeedReport,
) -> None:
    link_service = TaskCurriculumLinkService(session)
    existing_links = link_service.get_task_curriculum_links(task_id)
    for link in existing_links:
        if (
            link.exercise_pattern_id == spec.exercise_pattern_id
            and link.technical_concept_id == spec.technical_concept_id
            and link.is_primary
        ):
            report.skipped.append(f"link:{spec.slug}")
            return
    link_service.link_task_to_curriculum(
        task_id,
        LANGUAGE,
        spec.technical_concept_id,
        spec.exercise_pattern_id,
        is_primary=True,
    )
    report.linked.append(spec.slug)


def seed_pascal_conditions_showcase(
    session: Session,
    *,
    teacher_id: int | None = None,
) -> SeedReport:
    report = SeedReport()
    link_service = TaskCurriculumLinkService(session)

    for spec in conditions_showcase_specs():
        try:
            link_service.validate_task_curriculum_link(
                LANGUAGE,
                spec.technical_concept_id,
                spec.exercise_pattern_id,
            )
        except Exception as exc:
            report.errors.append(f"{spec.slug}: validation failed: {exc}")
            continue

        existing = find_showcase_task_by_slug(session, spec.slug)
        if existing is not None:
            if existing.title != spec.title or existing.description != spec.description:
                existing.title = spec.title
                existing.description = spec.description
                _attach_showcase_meta(existing, spec)
                session.flush()
            _ensure_curriculum_link(session, task_id=existing.id, spec=spec, report=report)
            report.skipped.append(f"task:{spec.slug}")
            continue

        builder = _BUILDERS.get(spec.builder_key)
        if builder is None:
            report.errors.append(f"{spec.slug}: unknown builder {spec.builder_key}")
            continue

        task_id = builder(session, spec=spec, teacher_id=teacher_id)
        report.created.append(spec.slug)
        _ensure_curriculum_link(session, task_id=task_id, spec=spec, report=report)

    return report


def list_showcase_tasks(session: Session, *, language: str = LANGUAGE) -> list[dict[str, Any]]:
    rows = session.scalars(
        select(TaskModel)
        .where(TaskModel.title.like(f"{TITLE_PREFIX}%"), TaskModel.is_delete.is_(False))
        .order_by(TaskModel.id.asc())
    ).all()
    link_service = TaskCurriculumLinkService(session)
    result: list[dict[str, Any]] = []
    for row in rows:
        examples = dict(row.code_examples or {})
        showcase = dict(examples.get("curriculum_showcase") or {})
        if showcase.get("group") != SHOWCASE_GROUP:
            continue
        metadata = link_service.get_task_curriculum_metadata(row.id)
        primary = metadata.get("primary_link")
        result.append(
            {
                "task_id": row.id,
                "title": row.title,
                "task_type": row.task_type,
                "difficulty": row.difficulty,
                "slug": showcase.get("slug"),
                "learning_concept_id": primary.get("learning_concept_id") if primary else None,
                "technical_concept_id": primary.get("technical_concept_id") if primary else None,
                "action": primary.get("action") if primary else None,
                "exercise_pattern_id": primary.get("exercise_pattern_id") if primary else None,
                "has_primary_link": primary is not None,
                "language": language,
            }
        )
    return result

