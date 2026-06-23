"""Deterministic subtype detection from Tree-sitter node types + simple rules."""
from __future__ import annotations

from tree_sitter import Node, Tree

from infrastructure.analysis.metadata.subtype_map_loader import maps_for_language

_LOOP_STRUCTURES = frozenset({"for_loop", "while_loop", "foreach"})
_CALL_NODE_TYPES = frozenset({"call", "call_expression", "invocation_expression"})


def detect_subtypes(tree: Tree, language_id: str) -> dict[str, set[str]]:
    maps = maps_for_language(language_id)
    found: dict[str, set[str]] = {key: set() for key in maps}
    loop_nodes: list[Node] = []

    if not tree.root_node:
        return {k: set() for k in found}

    def walk(node: Node) -> None:
        node_type = node.type
        for structure, subtype_types in maps.items():
            for subtype, types in subtype_types.items():
                if node_type in types:
                    found[structure].add(subtype)
                    if structure == "loop" and subtype in _LOOP_STRUCTURES:
                        loop_nodes.append(node)

        _apply_special_rules(node, language_id, found)
        for child in node.children:
            walk(child)

    walk(tree.root_node)

    if len(loop_nodes) >= 2 and _has_nested_loop(loop_nodes):
        found.setdefault("loop", set()).add("nested_loop")

    return {k: v for k, v in found.items() if v}


def _apply_special_rules(
    node: Node,
    language_id: str,
    found: dict[str, set[str]],
) -> None:
    lang = str(language_id).lower()

    if node.type in _CALL_NODE_TYPES:
        found.setdefault("call", set()).update(_classify_call(node))

    if lang == "python" and node.type == "function_definition":
        if _python_function_in_class(node):
            found.setdefault("function", set()).add("method")
        else:
            found.setdefault("function", set()).add("function")

    if lang == "javascript" and node.type == "function_declaration":
        found.setdefault("function", set()).add("function")

    if node.type == "lambda":
        found.setdefault("function", set()).add("lambda")


def _python_function_in_class(node: Node) -> bool:
    parent = node.parent
    while parent is not None:
        if parent.type == "class_definition":
            return True
        if parent.type in ("function_definition", "module"):
            return False
        parent = parent.parent
    return False


def _classify_call(node: Node) -> set[str]:
    kinds: set[str] = set()
    fn = node.child_by_field_name("function") if node.child_count else None
    if fn is None and node.children:
        fn = node.children[0]

    if fn is not None and fn.type in ("attribute", "field_expression", "member_expression"):
        kinds.add("method_call")
    else:
        kinds.add("direct_call")

    parent = node.parent
    while parent is not None:
        if parent.type in _CALL_NODE_TYPES or parent.type in (
            "attribute",
            "field_expression",
            "member_expression",
        ):
            kinds.add("chained_call")
            break
        if parent.type in ("expression_statement", "block", "module", "program"):
            break
        parent = parent.parent

    return kinds


def _has_nested_loop(loop_nodes: list[Node]) -> bool:
    for outer in loop_nodes:
        for inner in loop_nodes:
            if outer is inner:
                continue
            if _is_ancestor(outer, inner):
                return True
    return False


def _is_ancestor(ancestor: Node, descendant: Node) -> bool:
    parent = descendant.parent
    while parent is not None:
        if parent == ancestor:
            return True
        parent = parent.parent
    return False
