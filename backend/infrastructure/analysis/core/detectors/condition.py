"""Is there a branch / condition-like structure in the AST?"""
from __future__ import annotations

from tree_sitter import Tree

from infrastructure.analysis.structural_features import extract_node_features

STRUCTURE_ID = "condition"


def detect(tree: Tree) -> bool:
    for node in extract_node_features(tree):
        if node.child_count != 2:
            continue
        if not (3 <= node.subtree_size <= 14):
            continue
        if not (0.15 <= node.branching_factor <= 0.45):
            continue
        if node.leaf_ratio >= 0.55:
            continue
        return True
    return False
