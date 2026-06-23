from shared.enums import AssignmentType
from domain.services.assignment_strategies.base import AssignmentCreationContext, AssignmentCreationStrategy


class BuildFromBlocksStrategy(AssignmentCreationStrategy):
    assignment_type = AssignmentType.TASK_BUILD_FROM_BLOCKS

    def validate(self, context: AssignmentCreationContext) -> None:
        if not context.languages:
            raise ValueError("At least one programming language is required")
        code = (context.payload.get("original_code") or "").strip()
        if not code:
            raise ValueError("original_code is required for block assembly tasks")

    def expected_input_format(self) -> str:
        return "ordered code blocks assembled from predefined fragments"
