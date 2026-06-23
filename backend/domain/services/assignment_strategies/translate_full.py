from shared.enums import AssignmentType
from domain.services.assignment_strategies.base import AssignmentCreationContext, AssignmentCreationStrategy


class TranslateFullProgramStrategy(AssignmentCreationStrategy):
    assignment_type = AssignmentType.TASK_TRANSLATE_FULL_PROGRAM

    def validate(self, context: AssignmentCreationContext) -> None:
        if len(context.languages) < 2:
            raise ValueError(
                "Full program translation requires source and target languages"
            )
        code = (context.payload.get("source_code") or "").strip()
        if not code:
            raise ValueError("source_code is required")

    def expected_input_format(self) -> str:
        return "complete program preserving logic across languages"
