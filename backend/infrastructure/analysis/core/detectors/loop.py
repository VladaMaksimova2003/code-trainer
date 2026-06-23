"""Is there a loop-like structure in the AST?"""
from __future__ import annotations

from tree_sitter import Tree

from infrastructure.analysis.structural_features import extract_node_features

STRUCTURE_ID = "loop"
_THRESHOLD = 0.45


def detect(tree: Tree) -> bool:
    return any(node.loop_signal >= _THRESHOLD for node in extract_node_features(tree))
