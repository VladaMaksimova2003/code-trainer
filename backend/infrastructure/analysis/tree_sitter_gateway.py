"""Tree-sitter parser access via language registry.

Provides a shim layer so callers use the classic tree-sitter property API
(node.type, node.children, node.text, tree.root_node) regardless of whether
tree-sitter ≥0.22 (method-based API) or the older property-based API is installed.
"""
from __future__ import annotations

from tree_sitter_language_pack import get_parser

from infrastructure.execution.language_registry import language_registry


def _call_or_value(obj: object, name: str) -> object:
    value = getattr(obj, name)
    return value() if callable(value) else value


class _CompatNode:
    """Wraps a tree-sitter Node to expose a stable property API across versions."""

    __slots__ = ("_n", "_src")

    def __init__(self, node: object, src: bytes) -> None:
        self._n = node
        self._src = src

    @property
    def type(self) -> str:
        node = self._n
        if hasattr(node, "kind"):
            kind = getattr(node, "kind")
            raw = kind() if callable(kind) else kind
            if raw:
                return str(raw)
        raw_type = getattr(node, "type")
        resolved = raw_type() if callable(raw_type) else raw_type
        return str(resolved)

    @property
    def child_count(self) -> int:
        raw_children = getattr(self._n, "children", None)
        if isinstance(raw_children, list):
            return len(raw_children)
        return int(_call_or_value(self._n, "child_count"))

    def child(self, index: int) -> "_CompatNode":
        raw_children = getattr(self._n, "children", None)
        if isinstance(raw_children, list):
            return _CompatNode(raw_children[index], self._src)
        return _CompatNode(self._n.child(index), self._src)  # type: ignore[attr-defined]

    @property
    def children(self) -> list["_CompatNode"]:
        raw_children = getattr(self._n, "children", None)
        if isinstance(raw_children, list):
            return [_CompatNode(child, self._src) for child in raw_children]
        count = self.child_count
        return [self.child(i) for i in range(count)]

    @property
    def text(self) -> bytes:
        start = int(_call_or_value(self._n, "start_byte"))
        end = int(_call_or_value(self._n, "end_byte"))
        return self._src[start:end]

    @property
    def is_named(self) -> bool:
        return bool(_call_or_value(self._n, "is_named"))

    @property
    def parent(self) -> "_CompatNode | None":
        raw = _call_or_value(self._n, "parent")
        return _CompatNode(raw, self._src) if raw is not None else None

    def child_by_field_name(self, name: str) -> "_CompatNode | None":
        child = self._n.child_by_field_name(name)  # type: ignore[attr-defined]
        return _CompatNode(child, self._src) if child is not None else None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _CompatNode):
            return (
                int(_call_or_value(self._n, "start_byte"))
                == int(_call_or_value(other._n, "start_byte"))
                and int(_call_or_value(self._n, "end_byte"))
                == int(_call_or_value(other._n, "end_byte"))
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash(
            (
                int(_call_or_value(self._n, "start_byte")),
                int(_call_or_value(self._n, "end_byte")),
            )
        )

    def __bool__(self) -> bool:
        return self._n is not None


class _CompatTree:
    """Wraps a tree-sitter Tree to expose the classic property API."""

    __slots__ = ("_t", "_src")

    def __init__(self, tree: object, src: bytes) -> None:
        self._t = tree
        self._src = src

    @property
    def root_node(self) -> _CompatNode:
        raw = _call_or_value(self._t, "root_node")
        return _CompatNode(raw, self._src)


def parse_code(code: str, language_id: str) -> _CompatTree:
    cfg = language_registry.get_or_raise(language_id)
    grammar = cfg.tree_sitter_grammar or cfg.id
    parser = get_parser(grammar)
    src = code.encode("utf-8")
    try:
        raw_tree = parser.parse(code)
    except TypeError:
        raw_tree = parser.parse(src)
    return _CompatTree(raw_tree, src)
