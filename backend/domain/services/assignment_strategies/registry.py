from __future__ import annotations

from shared.enums import AssignmentType
from domain.services.assignment_strategies.base import AssignmentCreationStrategy
from domain.services.assignment_strategies.build_from_blocks import BuildFromBlocksStrategy
from domain.services.assignment_strategies.flowchart_to_code import FlowchartToCodeStrategy
from domain.services.assignment_strategies.translate_full import TranslateFullProgramStrategy
from domain.services.assignment_strategies.translate_snippet import TranslateSnippetStrategy

_STRATEGIES: dict[AssignmentType, AssignmentCreationStrategy] = {
    AssignmentType.TASK_BUILD_FROM_BLOCKS: BuildFromBlocksStrategy(),
    AssignmentType.TASK_TRANSLATE_SNIPPET: TranslateSnippetStrategy(),
    AssignmentType.TASK_TRANSLATE_FULL_PROGRAM: TranslateFullProgramStrategy(),
    AssignmentType.TASK_FLOWCHART_TO_CODE: FlowchartToCodeStrategy(),
}


def get_assignment_strategy(assignment_type: AssignmentType) -> AssignmentCreationStrategy:
    strategy = _STRATEGIES.get(assignment_type)
    if strategy is None:
        raise ValueError(f"No creation strategy for assignment type: {assignment_type.value}")
    return strategy


def list_creatable_assignment_types() -> list[dict[str, str]]:
    return [
        {
            "id": t.value,
            "name": t.public_label(),
            "expected_input": get_assignment_strategy(t).expected_input_format(),
        }
        for t in AssignmentType.creatable_types()
    ]
