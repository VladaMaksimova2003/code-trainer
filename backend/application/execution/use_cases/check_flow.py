from __future__ import annotations

from application.execution.services.flow_validation_service import FlowValidationService
from application.execution.flow_dto import (
    CheckFlowDTO,
    CheckFlowResultDTO,
    FlowErrorDTO,
)


class CheckFlowUseCase:
    def __init__(self, validator: FlowValidationService):
        self._validator = validator

    def execute(
        self,
        data: CheckFlowDTO,
        flow_spec: dict,
        task: dict | None = None,
    ) -> CheckFlowResultDTO:
        raw_flow = [item.model_dump() for item in data.flow]
        raw_nodes = [item.model_dump() for item in data.nodes] if data.nodes else None
        raw_edges = [item.model_dump() for item in data.edges] if data.edges else None
        details = self._validator.validate_with_details(
            flow=raw_flow,
            flow_spec=flow_spec,
            task=task,
            nodes=raw_nodes,
            edges=raw_edges,
        )
        pending = bool(details.get("execution_job_id"))
        return CheckFlowResultDTO(
            success=len(details["errors"]) == 0 and not pending,
            errors=[FlowErrorDTO(**item) for item in details["errors"]],
            execution_results=details["execution_results"],
            test_cases=details["test_cases"],
            semantic_checked=details["semantic_checked"],
            execution_job_id=details.get("execution_job_id"),
            status=details.get("status"),
            debug=details.get("debug"),
        )
