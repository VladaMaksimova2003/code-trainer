"""Validate teacher-authored flowcharts before create/update."""
from __future__ import annotations

from typing import Any

from application.execution.services.flow_block_constructions import DEFAULT_ALLOWED_BLOCKS
from application.execution.services.flow_validation_service import FlowValidationService


def _diagram_has_content(diagram: dict[str, Any] | None) -> bool:
    if not isinstance(diagram, dict):
        return False
    nodes = diagram.get("nodes")
    if isinstance(nodes, list) and nodes:
        return True
    flow = diagram.get("flow")
    return isinstance(flow, list) and bool(flow)


def validate_teacher_flowchart(diagram: dict[str, Any] | None) -> None:
    if not _diagram_has_content(diagram):
        return

    nodes = diagram.get("nodes")
    errors = FlowValidationService().validate(
        flow=diagram.get("flow") if isinstance(diagram.get("flow"), list) else [],
        flow_spec={"allowed_blocks": list(DEFAULT_ALLOWED_BLOCKS)},
        nodes=nodes if isinstance(nodes, list) else None,
        edges=diagram.get("edges") if isinstance(diagram.get("edges"), list) else None,
    )
    if errors:
        raise ValueError(errors[0].get("text") or "Некорректная блок-схема")


def validate_flowchart_assignment(
    *,
    diagram: dict[str, Any] | None,
    reference_code: str | None,
    expose_reference_code: bool,
) -> None:
    has_diagram = _diagram_has_content(diagram)
    code = str(reference_code or "").strip()
    exposes_code = bool(expose_reference_code and code)

    if not has_diagram and not exposes_code:
        raise ValueError(
            "Добавьте эталонную блок-схему и/или эталонный код (с опцией показа студенту)."
        )

    if has_diagram:
        validate_teacher_flowchart(diagram)

    if expose_reference_code and not code:
        raise ValueError("Введите эталонный код или отключите показ кода студенту.")
