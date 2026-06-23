"""Is there a return-like structure in the AST?"""
from __future__ import annotations

from tree_sitter import Tree

from infrastructure.analysis.structural_features import extract_node_features

STRUCTURE_ID = "return"


def detect(tree: Tree) -> bool:
    for node in extract_node_features(tree):
        if node.subtree_size > 5:
            continue
        if node.depth < 1:
            continue
        if node.leaf_ratio < 0.75:
            continue
        if node.child_count > 2:
            continue
        return True
    return False
