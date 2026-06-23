"""Flowchart diagram payload stored on task.flow_spec (nodes/edges/flow)."""

from __future__ import annotations

from typing import Any

_DIAGRAM_KEYS = ("nodes", "edges", "flow")


def empty_diagram() -> dict[str, Any]:
    return {"nodes": [], "edges": [], "flow": []}


def diagram_has_content(diagram: dict[str, Any] | None) -> bool:
    if not isinstance(diagram, dict):
        return False
    nodes = diagram.get("nodes")
    return isinstance(nodes, list) and len(nodes) > 0


def extract_diagram_from_flow_spec(flow_spec: dict[str, Any] | None) -> dict[str, Any]:
    spec = flow_spec if isinstance(flow_spec, dict) else {}
    if spec.get("nodes") or spec.get("edges") or spec.get("flow"):
        return {
            "nodes": spec.get("nodes") or [],
            "edges": spec.get("edges") or [],
            "flow": spec.get("flow") or [],
        }
    return empty_diagram()


def merge_diagram_into_flow_spec(
    flow_spec: dict[str, Any] | None,
    diagram: dict[str, Any] | None,
) -> dict[str, Any]:
    spec = dict(flow_spec or {})
    if not isinstance(diagram, dict):
        return spec
    for key in _DIAGRAM_KEYS:
        if key in diagram:
            spec[key] = diagram[key]
    return spec


def flow_spec_without_diagram_keys(flow_spec: dict[str, Any] | None) -> dict[str, Any]:
    spec = dict(flow_spec or {})
    return {key: value for key, value in spec.items() if key not in _DIAGRAM_KEYS}
