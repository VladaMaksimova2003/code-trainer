from shared.enums import AssignmentType
from domain.services.assignment_strategies.base import AssignmentCreationContext, AssignmentCreationStrategy


class TranslateSnippetStrategy(AssignmentCreationStrategy):
    assignment_type = AssignmentType.TASK_TRANSLATE_SNIPPET

    def validate(self, context: AssignmentCreationContext) -> None:
        if len(context.languages) < 2:
            raise ValueError(
                "Snippet translation requires source and target languages"
            )
        code = (context.payload.get("source_code") or "").strip()
        if not code:
            raise ValueError("source_code is required")
        if len(code.splitlines()) > 30:
            raise ValueError("Snippet translation must be a short code fragment")

    def expected_input_format(self) -> str:
        return "short source snippet translated to target language"
