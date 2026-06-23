from __future__ import annotations

from typing import Any, Callable

from shared.enums import AssignmentType, DifficultyLevel
from domain.services.assignment_strategies.base import AssignmentCreationContext
from domain.services.assignment_strategies.registry import get_assignment_strategy
from shared.language import parse_language
from application.tasks.dto import CreateAssignmentCommand


class CreateAssignmentUseCase:
    """Orchestrates assignment creation via type-specific strategies and handlers."""

    def __init__(
        self,
        *,
        create_build_from_blocks: Callable[..., dict[str, Any]],
        create_translation: Callable[..., dict[str, Any]],
        create_flowchart: Callable[..., dict[str, Any]],
    ) -> None:
        self._create_build_from_blocks = create_build_from_blocks
        self._create_translation = create_translation
        self._create_flowchart = create_flowchart

    def execute(self, command: CreateAssignmentCommand) -> dict[str, Any]:
        if command.assignment_type not in AssignmentType.creatable_types():
            raise ValueError("Assignment type cannot be created via this API")

        languages = tuple(parse_language(lang) for lang in command.languages)
        if not languages:
            raise ValueError("At least one programming language is required")

        context = AssignmentCreationContext(
            teacher_id=command.teacher_id,
            title=command.title.strip(),
            description=command.description.strip(),
            difficulty=command.difficulty,
            languages=languages,
            payload=command.payload,
        )

        strategy = get_assignment_strategy(command.assignment_type)
        strategy.validate(context)

        difficulty_value = command.difficulty.value
        primary_language = languages[0]

        if command.assignment_type == AssignmentType.TASK_BUILD_FROM_BLOCKS:
            return self._create_build_from_blocks(
                title=context.title,
                description=context.description,
                difficulty=difficulty_value,
                original_code=context.payload.get("original_code", ""),
                template=context.payload.get("template"),
                language=primary_language,
                language_variants=context.payload.get("language_variants"),
                teacher_id=command.teacher_id,
                blocks=context.payload.get("blocks"),
                correct_order=context.payload.get("correct_order"),
                assignment_type=command.assignment_type.value,
                patterns=command.patterns,
                test_cases=command.test_cases,
            )

        if command.assignment_type.is_translation():
            return self._create_translation(
                title=context.title,
                description=context.description,
                difficulty=difficulty_value,
                source_code=context.payload.get("source_code", ""),
                source_language=languages[0],
                target_languages=list(languages[1:]),
                teacher_id=command.teacher_id,
                assignment_type=command.assignment_type.value,
                patterns=command.patterns,
                test_cases=command.test_cases,
            )

        if command.assignment_type == AssignmentType.TASK_FLOWCHART_TO_CODE:
            diagram = context.payload.get("diagram") or context.payload.get("flow_spec")
            return self._create_flowchart(
                title=context.title,
                description=context.description,
                difficulty=difficulty_value,
                diagram=diagram,
                flow_spec=context.payload.get("flow_spec"),
                reference_code=context.payload.get("reference_code"),
                expose_reference_code=bool(context.payload.get("expose_reference_code")),
                language=primary_language,
                teacher_id=command.teacher_id,
                assignment_type=command.assignment_type.value,
                patterns=command.patterns,
                test_cases=command.test_cases,
            )

        raise ValueError(f"Unsupported assignment type: {command.assignment_type.value}")
