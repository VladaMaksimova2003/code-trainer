"""Is there a call-like structure in the AST?"""
from __future__ import annotations

from tree_sitter import Tree

from infrastructure.analysis.structural_features import extract_node_features

STRUCTURE_ID = "call"
_THRESHOLD = 0.5


def detect(tree: Tree) -> bool:
    return any(node.call_density >= _THRESHOLD for node in extract_node_features(tree))
