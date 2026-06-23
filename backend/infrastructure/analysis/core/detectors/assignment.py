"""Is there an assignment-like structure in the AST?"""
from __future__ import annotations

from tree_sitter import Tree

from infrastructure.analysis.structural_features import extract_node_features

STRUCTURE_ID = "assignment"
_THRESHOLD = 0.45


def detect(tree: Tree) -> bool:
    return any(node.mutation_signal >= _THRESHOLD for node in extract_node_features(tree))
