"""Spec factory helpers for pedagogical slots (curriculum v2)."""

from __future__ import annotations

from application.curriculum.pascal.catalog.pascal_pedagogical_slot import PedagogicalSlotSpec
from application.curriculum.pascal.showcase.pascal_showcase_core import PascalShowcaseTaskSpec
from shared.enums import AssignmentType


def _first_line(text: str) -> str:
    return (text or "").strip().split("\n")[0].strip()


def task_spec_to_slot(
    spec: PascalShowcaseTaskSpec,
    *,
    slot_id: str,
    primary_action: str,
    secondary_actions: tuple[str, ...] = (),
    short_instruction: str | None = None,
) -> PedagogicalSlotSpec:
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=spec.collection_key,
        target_tc=spec.technical_concept_id,
        primary_action=primary_action,
        secondary_actions=secondary_actions,
        title_suffix=spec.title_suffix,
        short_instruction=short_instruction or _first_line(spec.description),
        description=spec.description,
        difficulty=spec.difficulty,
        exercise_pattern_id=spec.exercise_pattern_id,
        assignment_type=spec.assignment_type,
        builder_key=spec.builder_key,
        extra=spec.extra,
        slug=spec.slug,
    )


def io_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    primary_action: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    test_cases: list[dict[str, str]],
    reference_solution_pascal: str,
    secondary_actions: tuple[str, ...] = (),
    exercise_pattern_id: str = "imp_text_spec_to_pascal",
) -> PedagogicalSlotSpec:
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action=primary_action,
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id=exercise_pattern_id,
        assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        builder_key="pascal_io_program",
        extra={
            "test_cases": test_cases,
            "reference_solution_pascal": reference_solution_pascal,
        },
    )


def translate_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    source_language: str,
    source_code: str,
    test_cases: list[dict[str, str]],
    reference_solution_pascal: str,
    secondary_actions: tuple[str, ...] = ("recognize",),
    exercise_pattern_id: str = "tr_python_to_pascal_code",
) -> PedagogicalSlotSpec:
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action="translate",
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id=exercise_pattern_id,
        assignment_type=AssignmentType.TASK_TRANSLATE_SNIPPET.value,
        builder_key="translation_to_pascal",
        extra={
            "source_language": source_language,
            "source_code": source_code,
            "test_cases": test_cases,
            "reference_solution_pascal": reference_solution_pascal,
        },
    )


def debug_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    starter_pascal: str,
    test_cases: list[dict[str, str]],
    reference_solution_pascal: str,
    secondary_actions: tuple[str, ...] = (),
    exercise_pattern_id: str = "dbg_pascal_code_fix",
) -> PedagogicalSlotSpec:
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action="debug",
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id=exercise_pattern_id,
        assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        builder_key="pascal_debug_starter",
        extra={
            "starter_pascal": starter_pascal,
            "test_cases": test_cases,
            "reference_solution_pascal": reference_solution_pascal,
        },
    )


def analyze_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    code_examples_pascal: str,
    expected_output: str,
    secondary_actions: tuple[str, ...] = ("recognize",),
) -> PedagogicalSlotSpec:
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action="analyze",
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id="ana_pascal_code_predict_output",
        assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        builder_key="pascal_io_program",
        extra={
            "code_examples_pascal": code_examples_pascal,
            "test_cases": [{"inputs": "", "output": expected_output}],
            "reference_solution_pascal": _analyze_reference(code_examples_pascal, expected_output),
        },
    )


def assemble_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    original_code: str,
    template: str,
    blocks: list[str],
    correct_order: list[int],
    test_cases: list[dict[str, str]],
    secondary_actions: tuple[str, ...] = ("recognize",),
    known_language_variants: dict | None = None,
) -> PedagogicalSlotSpec:
    extra: dict = {
        "language": "pascal",
        "original_code": original_code,
        "template": template,
        "blocks": blocks,
        "correct_order": correct_order,
        "test_cases": test_cases,
    }
    if known_language_variants:
        extra["known_language_variants"] = known_language_variants
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action="assemble",
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id="asm_blocks_to_code_pascal",
        assignment_type=AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
        builder_key="block_reorder_pascal",
        extra=extra,
    )


def flowchart_to_code_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    diagram: dict,
    reference_solution_pascal: str,
    test_cases: list[dict[str, str]],
    slug: str | None = None,
    secondary_actions: tuple[str, ...] = ("recognize",),
) -> PedagogicalSlotSpec:
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action="implement",
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id="tr_flowchart_to_pascal_code",
        assignment_type=AssignmentType.TASK_FLOWCHART_TO_CODE.value,
        builder_key="flowchart_pascal",
        slug=slug,
        extra={
            "diagram": diagram,
            "reference_code_pascal": reference_solution_pascal,
            "expose_reference_code": False,
            "test_cases": test_cases,
            "flowchart_mode": "flowchart_to_code",
        },
    )


def code_to_flowchart_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    reference_code_pascal: str,
    flow_spec: dict,
    slug: str | None = None,
    secondary_actions: tuple[str, ...] = ("recognize",),
) -> PedagogicalSlotSpec:
    from application.curriculum.pascal.catalog.pascal_flowchart_diagrams import empty_diagram

    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action="implement",
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id="imp_flowchart_to_pascal",
        assignment_type=AssignmentType.TASK_FLOWCHART_TO_CODE.value,
        builder_key="flowchart_pascal",
        slug=slug,
        extra={
            "diagram": empty_diagram(),
            "reference_code_pascal": reference_code_pascal,
            "expose_reference_code": True,
            "flow_spec": flow_spec,
            "flowchart_mode": "code_to_flowchart",
            "test_cases": [],
        },
    )


def flowchart_to_blocks_slot(
    *,
    slot_id: str,
    collection_key: str,
    target_tc: str,
    title_suffix: str,
    short_instruction: str,
    description: str,
    difficulty: str,
    diagram: dict,
    original_code: str,
    template: str,
    blocks: list[str],
    correct_order: list[int],
    test_cases: list[dict[str, str]],
    slug: str | None = None,
    secondary_actions: tuple[str, ...] = ("recognize",),
) -> PedagogicalSlotSpec:
    return PedagogicalSlotSpec(
        slot_id=slot_id,
        collection_key=collection_key,
        target_tc=target_tc,
        primary_action="assemble",
        secondary_actions=secondary_actions,
        title_suffix=title_suffix,
        short_instruction=short_instruction,
        description=description,
        difficulty=difficulty,
        exercise_pattern_id="asm_flowchart_to_blocks",
        assignment_type=AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
        builder_key="block_reorder_pascal",
        slug=slug,
        extra={
            "language": "pascal",
            "diagram": diagram,
            "original_code": original_code,
            "template": template,
            "blocks": blocks,
            "correct_order": correct_order,
            "test_cases": test_cases,
            "flowchart_mode": "flowchart_to_blocks",
        },
    )


def _analyze_reference(code: str, expected: str) -> str:
    """Wrap studied fragment as a valid Pascal program that prints the expected output."""
    del expected  # output is already produced by the studied fragment
    body = code.strip()
    if not body.endswith("."):
        body = f"{body}\nend."
    first_line = body.split("\n", 1)[0].strip().lower()
    if first_line.startswith("program "):
        return body
    header = "program AnalyzeRef;"
    stripped = body.lstrip()
    if stripped.lower().startswith(
        ("var ", "type ", "function ", "procedure ", "const ", "label ")
    ):
        return f"{header}\n{body}"
    if stripped.lower().startswith("begin"):
        return f"{header}\n{body}"
    return f"{header}\nbegin\n{body}\nend."


