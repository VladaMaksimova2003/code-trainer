"""Task-specific flowchart diagram payloads for Pascal curriculum flowchart slots."""

from __future__ import annotations

from typing import Any


def _node(node_id: str, node_type: str, text: str, *, x: float, y: float) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "text": text,
        "position": {"x": x, "y": y},
    }


def _edge(edge_id: str, source: str, target: str) -> dict[str, Any]:
    return {"id": edge_id, "source": source, "target": target}


def _diagram(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    return {"nodes": nodes, "edges": edges, "flow": []}


def empty_diagram() -> dict[str, Any]:
    return {"nodes": [], "edges": [], "flow": []}


def diagram_if_n_pos() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=240, y=40),
        _node("2", "input", "readln(n)", x=240, y=140),
        _node("3", "decision", "n > 0 ?", x=240, y=260),
        _node("4", "output", "writeln('pos')", x=80, y=400),
        _node("5", "output", "writeln('nonpos')", x=400, y=400),
        _node("6", "end", "Конец", x=240, y=520),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "3", "5"),
        _edge("e5", "4", "6"),
        _edge("e6", "5", "6"),
    ]
    return _diagram(nodes, edges)


def diagram_if_parity() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=240, y=40),
        _node("2", "input", "readln(n)", x=240, y=140),
        _node("3", "decision", "n mod 2 = 0 ?", x=240, y=260),
        _node("4", "output", "writeln('even')", x=80, y=400),
        _node("5", "output", "writeln('odd')", x=400, y=400),
        _node("6", "end", "Конец", x=240, y=520),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "3", "5"),
        _edge("e5", "4", "6"),
        _edge("e6", "5", "6"),
    ]
    return _diagram(nodes, edges)


def diagram_grade_chain() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=260, y=30),
        _node("2", "input", "readln(score)", x=260, y=120),
        _node("3", "decision", "score >= 90 ?", x=260, y=220),
        _node("4", "output", "writeln('A')", x=40, y=340),
        _node("5", "decision", "score >= 70 ?", x=260, y=340),
        _node("6", "output", "writeln('B')", x=140, y=460),
        _node("7", "output", "writeln('C')", x=400, y=460),
        _node("8", "end", "Конец", x=260, y=560),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "3", "5"),
        _edge("e5", "5", "6"),
        _edge("e6", "5", "7"),
        _edge("e7", "4", "8"),
        _edge("e8", "6", "8"),
        _edge("e9", "7", "8"),
    ]
    return _diagram(nodes, edges)


def diagram_for_sum_n() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=240, y=40),
        _node("2", "input", "readln(n)", x=240, y=130),
        _node("3", "process", "s := 0", x=240, y=220),
        _node("4", "loop", "i := 1 to n", x=240, y=310),
        _node("5", "process", "s := s + i", x=240, y=400),
        _node("6", "output", "writeln(s)", x=240, y=490),
        _node("7", "end", "Конец", x=240, y=580),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "4", "5"),
        _edge("e5", "5", "4"),
        _edge("e6", "4", "6"),
        _edge("e7", "6", "7"),
    ]
    return _diagram(nodes, edges)


def diagram_while_countdown() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=240, y=40),
        _node("2", "input", "readln(n)", x=240, y=130),
        _node("3", "loop", "n > 0 ?", x=240, y=220),
        _node("4", "output", "writeln(n)", x=240, y=310),
        _node("5", "process", "n := n - 1", x=240, y=400),
        _node("6", "end", "Конец", x=240, y=490),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "4", "5"),
        _edge("e5", "5", "3"),
        _edge("e6", "3", "6"),
    ]
    return _diagram(nodes, edges)


def diagram_nested_sum_products() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=280, y=30),
        _node("2", "input", "readln(n, m)", x=280, y=110),
        _node("3", "process", "s := 0", x=280, y=190),
        _node("4", "loop", "i := 1 to n", x=280, y=270),
        _node("5", "loop", "j := 1 to m", x=280, y=350),
        _node("6", "process", "s := s + i * j", x=280, y=430),
        _node("7", "output", "writeln(s)", x=280, y=510),
        _node("8", "end", "Конец", x=280, y=590),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "4", "5"),
        _edge("e5", "5", "6"),
        _edge("e6", "6", "5"),
        _edge("e7", "5", "4"),
        _edge("e8", "4", "7"),
        _edge("e9", "7", "8"),
    ]
    return _diagram(nodes, edges)


def diagram_case_code() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=260, y=30),
        _node("2", "input", "readln(code)", x=260, y=120),
        _node("3", "decision", "code = 1 ?", x=260, y=220),
        _node("4", "output", "writeln('one')", x=40, y=340),
        _node("5", "decision", "code = 2 ?", x=260, y=340),
        _node("6", "output", "writeln('two')", x=140, y=460),
        _node("7", "output", "writeln('other')", x=400, y=460),
        _node("8", "end", "Конец", x=260, y=560),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "3", "5"),
        _edge("e5", "5", "6"),
        _edge("e6", "5", "7"),
        _edge("e7", "4", "8"),
        _edge("e8", "6", "8"),
        _edge("e9", "7", "8"),
    ]
    return _diagram(nodes, edges)


def diagram_linear_search() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Начало", x=260, y=30),
        _node("2", "input", "readln a,b,c,t", x=260, y=110),
        _node("3", "decision", "a = t ?", x=120, y=200),
        _node("4", "output", "writeln('yes')", x=40, y=300),
        _node("5", "decision", "b = t ?", x=260, y=200),
        _node("6", "decision", "c = t ?", x=400, y=200),
        _node("7", "output", "writeln('yes')", x=260, y=300),
        _node("8", "output", "writeln('no')", x=520, y=300),
        _node("9", "end", "Конец", x=260, y=390),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "3", "4"),
        _edge("e4", "3", "5"),
        _edge("e5", "5", "7"),
        _edge("e6", "5", "6"),
        _edge("e7", "6", "7"),
        _edge("e8", "6", "8"),
        _edge("e9", "4", "9"),
        _edge("e10", "7", "9"),
        _edge("e11", "8", "9"),
    ]
    return _diagram(nodes, edges)


def diagram_pow2_recursion() -> dict[str, Any]:
    nodes = [
        _node("1", "start", "Pow2(n)", x=240, y=40),
        _node("2", "decision", "n = 0 ?", x=240, y=150),
        _node("3", "output", "return 1", x=80, y=270),
        _node("4", "process", "return 2 * Pow2(n-1)", x=400, y=270),
        _node("5", "end", "Конец", x=240, y=380),
    ]
    edges = [
        _edge("e1", "1", "2"),
        _edge("e2", "2", "3"),
        _edge("e3", "2", "4"),
        _edge("e4", "3", "5"),
        _edge("e5", "4", "5"),
    ]
    return _diagram(nodes, edges)


def diagram_multi_branch_score() -> dict[str, Any]:
    return diagram_grade_chain()
