"""Unified Pascal showcase — task spec, seed, list."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.display.chapter_task_display_order import (
    default_display_order_from_showcase,
    effective_display_order,
)
from application.curriculum.pascal.catalog.pascal_v311_builder_mapping import (
    CANONICAL_CURRICULUM_PATTERN,
)
from application.curriculum.pascal.showcase.pascal_showcase_registry import (
    collection_by_key,
    effective_showcase_group,
    effective_title_prefix,
)
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    v311_collection_by_key,
    v311_showcase_group,
    v311_title_prefix,
)
from application.curriculum.showcase.showcase_task_index import get_showcase_task_index
from application.curriculum.task_curriculum_link_service import (
    TaskCurriculumLinkService,
    validate_task_curriculum_link_metadata,
)
from application.curriculum.display.pascal_concept_hints import patterns_for_tc
from application.curriculum.pascal.catalog.pascal_known_language import (
    code_examples_from_variants,
    default_source_code,
    default_source_language,
)
from application.tasks.services.assignment_creation_service import (
    create_build_from_blocks_handler,
    create_flowchart_handler,
    create_translation_handler,
)
from application.tasks.services.task_id_allocator import allocate_next_task_id
from application.tasks.services.task_patterns import apply_patterns_and_tests
from application.tasks.services.flowchart_diagram_storage import (
    diagram_has_content,
    merge_diagram_into_flow_spec,
)
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask as TranslationTaskModel

LANGUAGE = "pascal"


def _diagram_has_nodes(diagram: dict[str, Any] | None) -> bool:
    return diagram_has_content(diagram)


def _attach_showcase_diagram(
    session: Session,
    *,
    task_id: int,
    diagram: dict[str, Any] | None,
) -> None:
    if not _diagram_has_nodes(diagram):
        return
    row = session.get(TaskModel, task_id)
    if row is None:
        return
    row.flow_spec = merge_diagram_into_flow_spec(row.flow_spec, diagram)
    session.flush()

_BUILDER_ACTION = {
    "translation_to_pascal": "translate",
    "translation_snippet_to_pascal": "translate",
    "translation_python_to_pascal": "translate",
    "block_reorder_pascal": "assemble",
    "pascal_io_program": "implement",
    "pascal_debug_starter": "debug",
    "mcq_pascal_fragment": "implement",
    "flowchart_pascal": "implement",
}

_PATTERN_PRIORITY_BY_ACTION: dict[str, list[str]] = {
    "translate": [
        "tr_python_to_pascal_code",
        "tr_cpp_to_pascal_code",
        "tr_java_to_pascal_code",
        "tr_flowchart_to_pascal_code",
    ],
    "assemble": ["asm_blocks_to_code_pascal", "asm_flowchart_to_blocks"],
    "implement": ["imp_io_tests_pascal", "imp_text_spec_to_pascal"],
    "debug": ["dbg_pascal_code_fix", "dbg_pascal_logic_fix", "dbg_transfer_syntax_fix"],
    "analyze": ["ana_pascal_code_predict_output", "ana_pascal_code_to_text"],
}


def _is_v311_spec(spec: PascalShowcaseTaskSpec) -> bool:
    extra = spec.extra or {}
    return extra.get("curriculum_version") == "3.1.1"


def _collection_group_and_prefix(
    collection_key: str,
    *,
    curriculum_version: str | int = "2",
) -> tuple[str, str]:
    if str(curriculum_version) == "3.1.1":
        return v311_showcase_group(collection_key), v311_title_prefix(collection_key)
    return effective_showcase_group(collection_key), effective_title_prefix(collection_key)


def _curriculum_version_from_specs(specs: tuple[PascalShowcaseTaskSpec, ...]) -> str:
    if specs and _is_v311_spec(specs[0]):
        return "3.1.1"
    return "2"


def resolve_v311_link_pattern(spec: PascalShowcaseTaskSpec) -> str:
    desired_action = spec.primary_action or _BUILDER_ACTION.get(spec.builder_key, "implement")
    bundle = CurriculumService(LANGUAGE).get_bundle()
    mask = bundle.action_masks.get(spec.technical_concept_id)
    if mask is None:
        return CANONICAL_CURRICULUM_PATTERN.get(desired_action, "imp_text_spec_to_pascal")

    def pick_for_action(action: str) -> str | None:
        allowed = set(mask.patterns_for_action(action))
        for pattern_id in _PATTERN_PRIORITY_BY_ACTION.get(action, []):
            if pattern_id in allowed:
                return pattern_id
        if allowed:
            return sorted(allowed)[0]
        return None

    pattern = pick_for_action(desired_action)
    if pattern:
        return pattern
    for fallback_action in ("implement", "debug", "translate", "analyze", "assemble"):
        if fallback_action == desired_action:
            continue
        pattern = pick_for_action(fallback_action)
        if pattern:
            return pattern
    return CANONICAL_CURRICULUM_PATTERN.get("implement", "imp_text_spec_to_pascal")


def resolve_showcase_exercise_pattern(spec: PascalShowcaseTaskSpec) -> str:
    """Pick a curriculum-valid pattern for the spec."""
    if _is_v311_spec(spec):
        return resolve_v311_link_pattern(spec)
    desired_action = spec.primary_action or _BUILDER_ACTION.get(spec.builder_key)

    if spec.exercise_pattern_id:
        try:
            validate_task_curriculum_link_metadata(
                LANGUAGE,
                spec.technical_concept_id,
                spec.exercise_pattern_id,
            )
            return spec.exercise_pattern_id
        except Exception:
            pass

    if desired_action is None:
        return spec.exercise_pattern_id

    bundle = CurriculumService(LANGUAGE).get_bundle()
    mask = bundle.action_masks.get(spec.technical_concept_id)
    if mask is None:
        return spec.exercise_pattern_id

    allowed = set(mask.patterns_for_action(desired_action))
    for pattern_id in _PATTERN_PRIORITY_BY_ACTION.get(desired_action, []):
        if pattern_id in allowed:
            return pattern_id
    if allowed:
        return sorted(allowed)[0]
    return spec.exercise_pattern_id


def with_resolved_pattern(spec: PascalShowcaseTaskSpec) -> PascalShowcaseTaskSpec:
    pattern_id = resolve_showcase_exercise_pattern(spec)
    if pattern_id == spec.exercise_pattern_id:
        return spec
    from dataclasses import replace

    return replace(spec, exercise_pattern_id=pattern_id)


@dataclass(frozen=True)
class PascalShowcaseTaskSpec:
    collection_key: str
    slug: str
    title_suffix: str
    description: str
    difficulty: str
    technical_concept_id: str
    exercise_pattern_id: str
    assignment_type: str
    builder_key: str
    extra: dict[str, Any] | None = None
    slot_id: str | None = None
    primary_action: str | None = None
    secondary_actions: tuple[str, ...] = ()
    short_instruction: str | None = None

    @property
    def title(self) -> str:
        prefix = (
            v311_title_prefix(self.collection_key)
            if _is_v311_spec(self)
            else effective_title_prefix(self.collection_key)
        )
        return f"{prefix}{self.title_suffix}"


@dataclass
class SeedReport:
    collection_key: str | None = None
    created: list[str] = field(default_factory=list)
    linked: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "collection_key": self.collection_key,
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


def _concept_patterns(spec: PascalShowcaseTaskSpec) -> list[str]:
    extra = spec.extra or {}
    raw = extra.get("concept_patterns")
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    return patterns_for_tc(spec.technical_concept_id)


def _showcase_meta(spec: PascalShowcaseTaskSpec) -> dict[str, Any]:
    extra = spec.extra or {}
    is_v311 = _is_v311_spec(spec)
    curriculum_version = "3.1.1" if is_v311 else "2"
    group, _prefix = _collection_group_and_prefix(
        spec.collection_key, curriculum_version=curriculum_version
    )
    meta: dict[str, Any] = {
        "group": group,
        "collection_key": spec.collection_key,
        "slug": spec.slug,
        "technical_concept_id": spec.technical_concept_id,
        "exercise_pattern_id": spec.exercise_pattern_id,
        "curriculum_version": "3.1.1" if is_v311 else 2,
        "target_language": "pascal",
        "concept_patterns": _concept_patterns(spec),
    }
    if is_v311:
        col = v311_collection_by_key(spec.collection_key)
        slot_pattern = extra.get("slot_pattern_id")
        if slot_pattern:
            meta["slot_pattern_id"] = slot_pattern
        if extra.get("task_format"):
            meta["task_format"] = extra["task_format"]
        if extra.get("pascal_features"):
            meta["pascal_features"] = extra["pascal_features"]
        if extra.get("expected_concept_ids"):
            meta["expected_concept_ids"] = list(extra["expected_concept_ids"])
        if extra.get("educational_goal"):
            meta["educational_goal"] = extra["educational_goal"]
        if extra.get("is_preview"):
            meta["is_preview"] = True
    else:
        col = collection_by_key(spec.collection_key)
    if col is not None:
        meta["collection_id"] = col.collection_id
    if spec.slot_id:
        meta["slot_id"] = spec.slot_id
    if spec.primary_action:
        meta["primary_action"] = spec.primary_action
    if spec.secondary_actions:
        meta["secondary_actions"] = list(spec.secondary_actions)
    if spec.short_instruction:
        meta["short_instruction"] = spec.short_instruction
    flowchart_mode = extra.get("flowchart_mode")
    if flowchart_mode:
        meta["flowchart_mode"] = str(flowchart_mode)
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict) and variants:
        meta["known_language_variants"] = variants
    assemble_context = extra.get("assemble_context")
    if isinstance(assemble_context, dict) and assemble_context:
        meta["assemble_context"] = assemble_context
    if spec.primary_action == "analyze":
        tests = extra.get("test_cases") or []
        if tests and isinstance(tests[0], dict):
            expected = tests[0].get("output")
            if expected is not None:
                meta["expected_output"] = str(expected)
    slot_key = str(spec.slot_id or spec.slug or "").strip()
    if slot_key:
        meta["display_order"] = default_display_order_from_showcase(
            {"slug": slot_key, "slot_id": slot_key}
        )
    return meta


def find_showcase_task_by_slug(
    session: Session,
    slug: str,
    *,
    collection_key: str | None = None,
    curriculum_version: str | int = "2",
) -> TaskModel | None:
    from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

    expected_group: str | None = None
    if collection_key:
        expected_group, _prefix = _collection_group_and_prefix(
            collection_key, curriculum_version=curriculum_version
        )
    for row, showcase in iter_showcase_tasks(session):
        row_slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
        if row_slug != slug:
            continue
        if collection_key:
            group = str(showcase.get("group") or "")
            if expected_group != group:
                continue
        return row
    return None


def _attach_showcase_meta(row: TaskModel, spec: PascalShowcaseTaskSpec) -> None:
    from application.curriculum.mirror.pedagogical_task_store import attach_unified_showcase_meta

    attach_unified_showcase_meta(row, _showcase_meta(spec), "pascal")


def _create_translation_to_pascal(
    session: Session,
    *,
    spec: PascalShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict) and variants:
        source_language = default_source_language(variants)
        source_code = default_source_code(variants, lang=source_language)
        code_examples = code_examples_from_variants(variants)
    else:
        source_language = extra["source_language"]
        source_code = extra["source_code"]
        code_examples = {source_language: source_code} if source_code else {}
    patterns = _concept_patterns(spec)
    result = create_translation_handler(
        session,
        assignment_type=spec.assignment_type,
        source_language=source_language,
        source_code=source_code,
        title=spec.title,
        description=spec.description,
        difficulty=spec.difficulty,
        teacher_id=teacher_id,
        test_cases=extra.get("test_cases"),
        patterns=patterns,
    )
    task_id = int(result["task_id"])
    row = session.get(TaskModel, task_id)
    if row is not None:
        merged_examples = dict(row.code_examples or {})
        merged_examples.update(code_examples)
        starter = str(extra.get("starter_pascal") or "").strip()
        if starter:
            merged_examples["pascal"] = starter
        row.code_examples = merged_examples
        _attach_showcase_meta(row, spec)
        apply_patterns_and_tests(row, patterns=patterns, test_cases=extra.get("test_cases"))
        session.flush()
    return task_id


def _create_block_reorder_pascal(
    session: Session,
    *,
    spec: PascalShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    patterns = _concept_patterns(spec)
    variants = extra.get("known_language_variants")
    assemble_context = extra.get("assemble_context")
    result = create_build_from_blocks_handler(
        session,
        assignment_type=spec.assignment_type,
        language=extra["language"],
        original_code=extra["original_code"],
        template=extra.get("template"),
        blocks=extra.get("blocks"),
        correct_order=extra.get("correct_order"),
        language_variants=extra.get("language_variants"),
        title=spec.title,
        description=spec.description,
        difficulty=spec.difficulty,
        teacher_id=teacher_id,
        test_cases=extra.get("test_cases"),
        patterns=patterns,
    )
    task_id = int(result["task_id"])
    row = session.get(TaskModel, task_id)
    if row is not None:
        examples = dict(row.code_examples or {})
        if isinstance(variants, dict) and variants:
            examples.update(code_examples_from_variants(variants))
        elif isinstance(assemble_context, dict):
            for lang, code in assemble_context.items():
                if lang in {"python", "cpp", "java", "csharp"} and code:
                    examples[lang] = str(code)
        row.code_examples = examples
        _attach_showcase_meta(row, spec)
        apply_patterns_and_tests(row, patterns=patterns, test_cases=extra.get("test_cases"))
        _attach_showcase_diagram(session, task_id=task_id, diagram=extra.get("diagram"))
        session.flush()
    return task_id


def _apply_known_language_variants(examples: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict) and variants:
        merged = dict(examples)
        merged.update(code_examples_from_variants(variants))
        return merged
    return examples


def _create_pascal_io_program(
    session: Session,
    *,
    spec: PascalShowcaseTaskSpec,
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
    patterns = _concept_patterns(spec)
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError("Failed to create Pascal IO showcase task")
    examples: dict[str, Any] = {}
    if extra.get("code_examples_pascal"):
        examples["pascal"] = extra["code_examples_pascal"]
    examples = _apply_known_language_variants(examples, extra)
    row.code_examples = examples
    _attach_showcase_meta(row, spec)
    apply_patterns_and_tests(row, patterns=patterns, test_cases=extra.get("test_cases"))
    session.flush()
    return task_id


def _create_pascal_debug_starter(
    session: Session,
    *,
    spec: PascalShowcaseTaskSpec,
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
    patterns = _concept_patterns(spec)
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError("Failed to create Pascal debug showcase task")
    examples = dict(row.code_examples or {})
    examples = _apply_known_language_variants(examples, extra)
    row.code_examples = examples
    _attach_showcase_meta(row, spec)
    apply_patterns_and_tests(row, patterns=patterns, test_cases=extra.get("test_cases"))
    session.flush()
    return task_id


def _create_translation_snippet_to_pascal(
    session: Session,
    *,
    spec: PascalShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    return _create_translation_to_pascal(session, spec=spec, teacher_id=teacher_id)


def _create_mcq_pascal_fragment(
    session: Session,
    *,
    spec: PascalShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    options = list(extra.get("mcq_options") or [])
    if not options:
        raise ValueError(f"{spec.slug}: mcq_options required")
    correct_index = int(extra.get("correct_index", 0))
    if correct_index < 0 or correct_index >= len(options):
        raise ValueError(f"{spec.slug}: invalid correct_index")
    patterns = _concept_patterns(spec)
    reference = str(extra.get("reference_solution_pascal") or options[correct_index])
    task_id = allocate_next_task_id(session)
    flow_spec: dict[str, Any] = {
        "target_language": LANGUAGE,
        "mcq_mode": True,
        "correct_index": correct_index,
    }
    explanation = extra.get("explanation")
    if explanation:
        flow_spec["explanation"] = str(explanation)
    session.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=teacher_id,
            title=spec.title,
            description=spec.description,
            difficulty=spec.difficulty,
            task_type=spec.assignment_type,
            test_cases=[],
            code_examples={
                "pascal": "",
                "mcq_options": options,
                "mcq_correct_index": correct_index,
            },
            flow_spec=flow_spec,
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
        raise RuntimeError("Failed to create MCQ Pascal fragment task")
    examples = dict(row.code_examples or {})
    if reference:
        examples["pascal_reference"] = reference
    examples = _apply_known_language_variants(examples, extra)
    row.code_examples = examples
    _attach_showcase_meta(row, spec)
    apply_patterns_and_tests(row, patterns=patterns, test_cases=extra.get("test_cases"))
    session.flush()
    return task_id


def _create_flowchart_pascal(
    session: Session,
    *,
    spec: PascalShowcaseTaskSpec,
    teacher_id: int | None,
) -> int:
    extra = spec.extra or {}
    patterns = _concept_patterns(spec)
    result = create_flowchart_handler(
        session,
        assignment_type=spec.assignment_type,
        diagram=extra["diagram"],
        reference_code=extra.get("reference_code_pascal", ""),
        expose_reference_code=bool(extra.get("expose_reference_code")),
        language="pascal",
        title=spec.title,
        description=spec.description,
        difficulty=spec.difficulty,
        teacher_id=teacher_id,
        test_cases=extra.get("test_cases"),
        patterns=patterns,
        flow_spec=extra.get("flow_spec"),
    )
    task_id = int(result["task_id"])
    row = session.get(TaskModel, task_id)
    if row is not None:
        examples = dict(row.code_examples or {})
        examples = _apply_known_language_variants(examples, extra)
        row.code_examples = examples
        _attach_showcase_meta(row, spec)
        apply_patterns_and_tests(row, patterns=patterns, test_cases=extra.get("test_cases"))
        session.flush()
    return task_id


def _refresh_showcase_task_content(
    session: Session,
    row: TaskModel,
    spec: PascalShowcaseTaskSpec,
) -> None:
    """Update seeded task body when catalog content changes."""
    from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled
    from application.tasks.services.teacher_assembly_preservation import (
        should_skip_catalog_seed_refresh,
    )

    if not is_catalog_sync_enabled():
        return
    if should_skip_catalog_seed_refresh(row):
        return

    extra = spec.extra or {}
    patterns = _concept_patterns(spec)
    examples = dict(row.code_examples or {})
    row.code_examples = examples
    row.title = spec.title
    row.description = spec.description
    row.difficulty = spec.difficulty
    row.task_type = spec.assignment_type

    if spec.builder_key in {
        "translation_to_pascal",
        "translation_snippet_to_pascal",
        "translation_python_to_pascal",
    }:
        variants = extra.get("known_language_variants")
        if isinstance(variants, dict) and variants:
            code_examples = code_examples_from_variants(variants)
            source_language = default_source_language(variants)
            source_code = default_source_code(variants, lang=source_language)
        else:
            source_language = extra.get("source_language", "python")
            source_code = extra.get("source_code", "")
            code_examples = {source_language: source_code} if source_code else {}
        examples = dict(row.code_examples or {})
        for key in list(examples.keys()):
            if key in {"python", "cpp", "java", "csharp"}:
                examples.pop(key, None)
        examples.update(code_examples)
        starter = str(extra.get("starter_pascal") or "").strip()
        if starter:
            examples["pascal"] = starter
        row.code_examples = examples
        trans = session.execute(
            select(TranslationTaskModel).filter_by(task_id=row.id)
        ).scalar_one_or_none()
        if trans is not None:
            trans.source_language = source_language
            trans.source_code = source_code
    elif spec.builder_key == "block_reorder_pascal":
        examples = dict(row.code_examples or {})
        variants = extra.get("known_language_variants")
        assemble_context = extra.get("assemble_context")
        if isinstance(variants, dict) and variants:
            for key in list(examples.keys()):
                if key in {"python", "cpp", "java", "csharp"}:
                    examples.pop(key, None)
            examples.update(code_examples_from_variants(variants))
        elif isinstance(assemble_context, dict):
            for lang, code in assemble_context.items():
                if lang in {"python", "cpp", "java", "csharp"} and code:
                    examples[lang] = str(code)
        row.code_examples = examples
        br = row.block_reorder_task
        if br is not None:
            if extra.get("original_code"):
                br.original_code = extra["original_code"]
            if extra.get("template") is not None:
                br.template = extra.get("template")
            if extra.get("blocks") is not None:
                br.blocks = extra.get("blocks")
            if extra.get("correct_order") is not None:
                br.correct_order = extra.get("correct_order")
            if extra.get("language_variants") is not None:
                br.language_variants = extra.get("language_variants")
        _attach_showcase_diagram(session, task_id=row.id, diagram=extra.get("diagram"))
    elif spec.builder_key == "flowchart_pascal":
        from application.tasks.use_cases.flowchart.task import (
            _apply_reference_code,
            _merge_flow_spec,
        )

        diagram = extra.get("diagram")
        if _diagram_has_nodes(diagram):
            _attach_showcase_diagram(session, task_id=row.id, diagram=diagram)
        reference_code = str(extra.get("reference_code_pascal") or "").strip()
        expose_reference_code = bool(extra.get("expose_reference_code"))
        _apply_reference_code(
            row,
            language="pascal",
            reference_code=reference_code if expose_reference_code else "",
        )
        row.flow_spec = _merge_flow_spec(
            extra.get("flow_spec") if isinstance(extra.get("flow_spec"), dict) else None,
            language="pascal",
            reference_code=reference_code,
            expose_reference_code=expose_reference_code,
        )
        examples = dict(row.code_examples or {})
        for key in list(examples.keys()):
            if key in {"python", "cpp", "java", "csharp"}:
                examples.pop(key, None)
        examples = _apply_known_language_variants(examples, extra)
        row.code_examples = examples
    elif spec.builder_key == "pascal_io_program":
        examples = dict(row.code_examples or {})
        if extra.get("code_examples_pascal"):
            examples["pascal"] = extra["code_examples_pascal"]
        elif extra.get("starter_pascal"):
            examples["pascal"] = extra["starter_pascal"]
        for key in list(examples.keys()):
            if key in {"python", "cpp", "java", "csharp"}:
                examples.pop(key, None)
        examples = _apply_known_language_variants(examples, extra)
        row.code_examples = examples
    elif spec.builder_key == "pascal_debug_starter":
        examples = dict(row.code_examples or {})
        if extra.get("starter_pascal"):
            examples["pascal"] = extra["starter_pascal"]
        for key in list(examples.keys()):
            if key in {"python", "cpp", "java", "csharp"}:
                examples.pop(key, None)
        examples = _apply_known_language_variants(examples, extra)
        row.code_examples = examples
    elif spec.builder_key == "mcq_pascal_fragment":
        options = list(extra.get("mcq_options") or [])
        correct_index = int(extra.get("correct_index", 0))
        examples = dict(row.code_examples or {})
        examples["mcq_options"] = options
        examples["mcq_correct_index"] = correct_index
        examples["pascal"] = ""
        reference = str(extra.get("reference_solution_pascal") or "")
        if reference:
            examples["pascal_reference"] = reference
        for key in list(examples.keys()):
            if key in {"python", "cpp", "java", "csharp"}:
                examples.pop(key, None)
        examples = _apply_known_language_variants(examples, extra)
        row.code_examples = examples
        flow_spec = dict(row.flow_spec or {})
        flow_spec.update(
            {
                "target_language": LANGUAGE,
                "mcq_mode": True,
                "correct_index": correct_index,
            }
        )
        if extra.get("explanation"):
            flow_spec["explanation"] = str(extra["explanation"])
        row.flow_spec = flow_spec

    _attach_showcase_meta(row, spec)
    apply_patterns_and_tests(row, patterns=patterns, test_cases=extra.get("test_cases"))
    session.flush()


_BUILDERS = {
    "translation_to_pascal": _create_translation_to_pascal,
    "translation_snippet_to_pascal": _create_translation_snippet_to_pascal,
    "translation_python_to_pascal": _create_translation_to_pascal,
    "block_reorder_pascal": _create_block_reorder_pascal,
    "pascal_io_program": _create_pascal_io_program,
    "pascal_debug_starter": _create_pascal_debug_starter,
    "flowchart_pascal": _create_flowchart_pascal,
    "mcq_pascal_fragment": _create_mcq_pascal_fragment,
}


def _ensure_curriculum_link(
    session: Session,
    *,
    task_id: int,
    spec: PascalShowcaseTaskSpec,
    report: SeedReport,
) -> None:
    link_service = TaskCurriculumLinkService(session)
    links = link_service.get_task_curriculum_links(task_id)
    if any(link.exercise_pattern_id == spec.exercise_pattern_id for link in links):
        report.skipped.append(f"link:{spec.slug}")
        return
    primary = next((link for link in links if link.is_primary and link.language == LANGUAGE), None)
    if primary is None:
        primary = next((link for link in links if link.language == LANGUAGE), None)

    if primary is not None:
        if (
            primary.exercise_pattern_id == spec.exercise_pattern_id
            and primary.technical_concept_id == spec.technical_concept_id
        ):
            report.skipped.append(f"link:{spec.slug}")
            return
        for link in links:
            if (
                link.id != primary.id
                and link.language == LANGUAGE
                and link.exercise_pattern_id == spec.exercise_pattern_id
            ):
                link_service.delete_link(task_id, link.id)
        link_service.update_link(
            task_id,
            primary.id,
            technical_concept_id=spec.technical_concept_id,
            exercise_pattern_id=spec.exercise_pattern_id,
            language=LANGUAGE,
            is_primary=primary.is_primary,
        )
        report.linked.append(f"updated:{spec.slug}")
        return

    link_service.link_task_to_curriculum(
        task_id,
        LANGUAGE,
        spec.technical_concept_id,
        spec.exercise_pattern_id,
        is_primary=not any(link.is_primary for link in links),
    )
    report.linked.append(spec.slug)


def _retire_orphaned_showcase_tasks(
    session: Session,
    collection_key: str,
    active_slugs: set[str],
    report: SeedReport,
    *,
    curriculum_version: str | int = "2",
) -> None:
    group, prefix = _collection_group_and_prefix(
        collection_key, curriculum_version=curriculum_version
    )
    rows = session.scalars(
        select(TaskModel).where(
            TaskModel.title.like(f"{prefix}%"),
            TaskModel.is_delete.is_(False),
        )
    ).all()
    for row in rows:
        examples = dict(row.code_examples or {})
        showcase = dict(examples.get("curriculum_showcase") or {})
        if showcase.get("group") != group:
            continue
        slug = str(showcase.get("slug") or "")
        if slug and slug not in active_slugs:
            row.is_delete = True
            report.skipped.append(f"retired:{slug}")


def _attach_pascal_track_light(
    session: Session,
    row: TaskModel,
    spec: PascalShowcaseTaskSpec,
) -> None:
    """Attach Pascal track to an existing Universal Core row without removing sibling languages."""
    from sqlalchemy.orm.attributes import flag_modified

    extra = spec.extra or {}
    _attach_showcase_meta(row, spec)
    examples = dict(row.code_examples or {})
    starter = str(extra.get("starter_pascal") or "").strip()
    if starter:
        examples["pascal"] = starter
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict) and variants:
        merged = code_examples_from_variants(variants)
        if merged.get("pascal"):
            examples["pascal"] = str(merged["pascal"])
    row.code_examples = examples
    flag_modified(row, "code_examples")
    apply_patterns_and_tests(
        row,
        patterns=_concept_patterns(spec),
        test_cases=extra.get("test_cases"),
    )
    session.flush()


def seed_pascal_attach_unified_collection(
    session: Session,
    collection_key: str,
    specs: tuple[PascalShowcaseTaskSpec, ...],
    *,
    teacher_id: int | None = None,
) -> SeedReport:
    """Attach Pascal tracks to existing py_* Universal Core tasks (non-destructive)."""
    from application.curriculum.mirror.pedagogical_task_store import (
        resolve_unified_task_for_mirror_attach,
        track_slug,
    )

    report = SeedReport(collection_key=collection_key)
    link_service = TaskCurriculumLinkService(session)

    for raw_spec in specs:
        link_spec = with_resolved_pattern(raw_spec)
        slug = raw_spec.slug
        if raw_spec.collection_key != collection_key:
            report.errors.append(f"{slug}: wrong collection {raw_spec.collection_key}")
            continue
        try:
            link_service.validate_task_curriculum_link(
                LANGUAGE,
                link_spec.technical_concept_id,
                link_spec.exercise_pattern_id,
            )
        except Exception as exc:
            report.errors.append(f"{slug}: validation failed: {exc}")
            continue

        row = resolve_unified_task_for_mirror_attach(
            session,
            mirror_slug=slug,
            target_slug=slug,
        )
        if row is None:
            report.errors.append(f"{slug}: unified task missing")
            continue

        showcase = dict((row.code_examples or {}).get("curriculum_showcase") or {})
        if track_slug(showcase, LANGUAGE) == slug:
            _ensure_curriculum_link(session, task_id=row.id, spec=link_spec, report=report)
            report.skipped.append(f"attached:{slug}")
            continue

        if teacher_id is not None:
            row.teacher_id = teacher_id
        _attach_pascal_track_light(session, row, raw_spec)
        _ensure_curriculum_link(session, task_id=row.id, spec=link_spec, report=report)
        report.linked.append(slug)

    session.flush()
    return report


def seed_pascal_showcase_collection(
    session: Session,
    collection_key: str,
    specs: tuple[PascalShowcaseTaskSpec, ...],
    *,
    teacher_id: int | None = None,
) -> SeedReport:
    report = SeedReport(collection_key=collection_key)
    link_service = TaskCurriculumLinkService(session)
    active_slugs: set[str] = set()
    curriculum_version = _curriculum_version_from_specs(specs)

    for raw_spec in specs:
        link_spec = with_resolved_pattern(raw_spec)
        active_slugs.add(raw_spec.slug)
        if raw_spec.collection_key != collection_key:
            report.errors.append(f"{raw_spec.slug}: wrong collection {raw_spec.collection_key}")
            continue
        try:
            link_service.validate_task_curriculum_link(
                LANGUAGE,
                link_spec.technical_concept_id,
                link_spec.exercise_pattern_id,
            )
        except Exception as exc:
            report.errors.append(f"{raw_spec.slug}: validation failed: {exc}")
            continue

        existing = find_showcase_task_by_slug(
            session,
            raw_spec.slug,
            collection_key=collection_key,
            curriculum_version=curriculum_version,
        )
        from application.curriculum.mirror.pedagogical_task_store import (
            canonical_pedagogical_slot_id,
            find_task_by_pedagogical_slot,
        )

        ped_id = canonical_pedagogical_slot_id(
            slot_id=raw_spec.slot_id,
            slug=raw_spec.slug,
            language=LANGUAGE,
        )
        unified = find_task_by_pedagogical_slot(session, ped_id) if ped_id else None

        if existing is not None:
            if teacher_id is not None:
                existing.teacher_id = teacher_id
            from application.tasks.services.teacher_assembly_preservation import (
                should_skip_catalog_seed_refresh,
            )

            if not should_skip_catalog_seed_refresh(existing):
                _refresh_showcase_task_content(session, existing, raw_spec)
            _ensure_curriculum_link(session, task_id=existing.id, spec=link_spec, report=report)
            report.skipped.append(f"task:{raw_spec.slug}")
            continue

        if unified is not None:
            if teacher_id is not None:
                unified.teacher_id = teacher_id
            _attach_pascal_track_light(session, unified, raw_spec)
            _ensure_curriculum_link(session, task_id=unified.id, spec=link_spec, report=report)
            report.skipped.append(f"merged:{raw_spec.slug}")
            continue

        builder = _BUILDERS.get(raw_spec.builder_key)
        if builder is None:
            report.errors.append(f"{raw_spec.slug}: unknown builder {raw_spec.builder_key}")
            continue

        task_id = builder(session, spec=raw_spec, teacher_id=teacher_id)
        report.created.append(raw_spec.slug)
        _ensure_curriculum_link(session, task_id=task_id, spec=link_spec, report=report)

    _retire_orphaned_showcase_tasks(
        session, collection_key, active_slugs, report, curriculum_version=curriculum_version
    )
    session.flush()
    from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache

    invalidate_showcase_task_index_cache()
    return report


def seed_pascal_v311_showcase_collection(
    session: Session,
    collection_key: str,
    specs: tuple[PascalShowcaseTaskSpec, ...],
    *,
    teacher_id: int | None = None,
) -> SeedReport:
    """Seed Pascal Course v3.1.1 collection (alias for unified seed path)."""
    return seed_pascal_showcase_collection(
        session,
        collection_key,
        specs,
        teacher_id=teacher_id,
    )


def list_showcase_tasks_for_collection(
    session: Session,
    collection_key: str,
    *,
    curriculum_version: str | int = "2",
) -> list[dict[str, Any]]:
    version = str(curriculum_version)
    if version in {"3.1.1", "1.0"}:
        index = get_showcase_task_index()
        if index is not None:
            cached = index.list_for_collection(
                LANGUAGE,
                collection_key,
                curriculum_version=version,
            )
            if cached:
                return cached

    group, prefix = _collection_group_and_prefix(
        collection_key, curriculum_version=curriculum_version
    )
    from application.curriculum.mirror.pedagogical_task_store import (
        iter_showcase_tasks,
        showcase_matches_collection,
        track_slug,
    )

    link_service = TaskCurriculumLinkService(session)
    matched_rows: list[tuple[Any, dict[str, Any]]] = []

    if version in {"3.1.1", "1.0"}:
        for row, showcase in iter_showcase_tasks(session):
            if showcase_matches_collection(
                showcase,
                language=LANGUAGE,
                collection_key=collection_key,
                group=group,
            ):
                matched_rows.append((row, showcase))
        from application.curriculum.course_scope import filter_showcase_matches_in_scope
        from application.curriculum.showcase.showcase_row_dedupe import dedupe_showcase_task_rows

        matched_rows = filter_showcase_matches_in_scope(matched_rows)
        matched_rows = dedupe_showcase_task_rows(matched_rows, language=LANGUAGE)
    else:
        rows = session.scalars(
            select(TaskModel)
            .where(TaskModel.title.like(f"{prefix}%"), TaskModel.is_delete.is_(False))
            .order_by(TaskModel.id.asc())
        ).all()
        for row in rows:
            examples = dict(row.code_examples or {})
            showcase = dict(examples.get("curriculum_showcase") or {})
            if showcase.get("group") != group:
                continue
            matched_rows.append((row, showcase))

    primary_by_task = link_service.get_primary_links_by_task_ids(
        [row.id for row, _ in matched_rows],
        language=LANGUAGE,
    )
    result: list[dict[str, Any]] = []
    from application.curriculum.showcase.showcase_collection_tasks import (
        build_showcase_collection_task_row,
    )

    for row, showcase in matched_rows:
        primary = primary_by_task.get(row.id)
        result.append(
            build_showcase_collection_task_row(
                row=row,
                showcase=showcase,
                language=LANGUAGE,
                collection_key=collection_key,
                primary=primary,
            )
        )
    return result


def collection_spec_seed_index(
    specs: tuple[PascalShowcaseTaskSpec, ...],
) -> dict[str, int]:
    return {spec.slug: index for index, spec in enumerate(specs)}


