"""Is there a function-like structure in the AST?"""
from __future__ import annotations

from tree_sitter import Tree

from infrastructure.analysis.structural_features import extract_node_features

STRUCTURE_ID = "function"
_THRESHOLD = 0.4


def detect(tree: Tree) -> bool:
    return any(node.function_signal >= _THRESHOLD for node in extract_node_features(tree))
