from application.tasks.services.flowchart_authoring import validate_flowchart_assignment
from shared.enums import AssignmentType
from domain.services.assignment_strategies.base import AssignmentCreationContext, AssignmentCreationStrategy


class FlowchartToCodeStrategy(AssignmentCreationStrategy):
    assignment_type = AssignmentType.TASK_FLOWCHART_TO_CODE

    def validate(self, context: AssignmentCreationContext) -> None:
        if not context.languages:
            raise ValueError("At least one programming language is required")
        diagram = context.payload.get("diagram") or context.payload.get("flow_spec")
        validate_flowchart_assignment(
            diagram=diagram if isinstance(diagram, dict) else {},
            reference_code=str(context.payload.get("reference_code") or ""),
            expose_reference_code=bool(context.payload.get("expose_reference_code")),
        )

    def expected_input_format(self) -> str:
        return "flowchart / flow specification converted to executable code"
