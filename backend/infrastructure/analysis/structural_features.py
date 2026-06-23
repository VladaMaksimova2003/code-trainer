"""Language-agnostic structural metrics from Tree-sitter nodes (no node-type rules)."""
from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Node, Tree


@dataclass(frozen=True)
class NodeStructuralFeatures:
    node_id: int
    raw_type: str
    depth: int
    child_count: int
    subtree_size: int
    branching_factor: float
    max_child_depth: int
    leaf_ratio: float
    sibling_uniformity: float
    loop_signal: float
    function_signal: float
    call_density: float
    recursion_signal: float
    mutation_signal: float
    iteration_signal: float

    def as_vector(self) -> list[float]:
        return [
            float(self.depth),
            float(self.child_count),
            float(self.subtree_size),
            self.branching_factor,
            float(self.max_child_depth),
            self.leaf_ratio,
            self.sibling_uniformity,
            self.loop_signal,
            self.function_signal,
            self.call_density,
            self.recursion_signal,
            self.mutation_signal,
            self.iteration_signal,
        ]


def _loop_signal(depth: int, subtree_size: int, child_count: int, max_child_depth: int) -> float:
    depth_span = max(0, max_child_depth - depth)
    size_factor = min(1.0, subtree_size / 12.0)
    child_factor = min(1.0, child_count / 3.0)
    return round(min(1.0, size_factor * (0.4 + 0.3 * child_factor + 0.3 * depth_span / 8.0)), 4)


def _function_signal(child_count: int, subtree_size: int, depth: int) -> float:
    if child_count < 3 or subtree_size < 6:
        return 0.0
    header_depth = 1.0 / (1.0 + depth)
    arity = min(1.0, child_count / 6.0)
    return round(min(1.0, arity * header_depth * min(1.0, subtree_size / 16.0)), 4)


def _call_density(child_count: int, leaf_ratio: float, subtree_size: int) -> float:
    if subtree_size > 8:
        return 0.0
    compact = 1.0 - min(1.0, subtree_size / 8.0)
    return round(min(1.0, leaf_ratio * compact * (1.0 + child_count * 0.2)), 4)


def _recursion_signal(
    depth: int,
    subtree_size: int,
    call_density: float,
    max_child_depth: int,
) -> float:
    depth_factor = min(1.0, depth / 6.0)
    span = max_child_depth - depth
    self_similar = min(1.0, subtree_size / 20.0) * min(1.0, span / 10.0)
    return round(min(1.0, self_similar * 0.6 + call_density * depth_factor * 0.4), 4)


def _mutation_signal(child_count: int, sibling_uniformity: float, leaf_ratio: float) -> float:
    if child_count != 2:
        return 0.0
    return round(min(1.0, sibling_uniformity * (1.0 - leaf_ratio * 0.5)), 4)


def _iteration_signal(loop_signal: float, branching_factor: float, subtree_size: int) -> float:
    return round(min(1.0, loop_signal * (0.5 + branching_factor) * min(1.0, subtree_size / 10.0)), 4)


def extract_node_features(tree: Tree) -> list[NodeStructuralFeatures]:
    features: list[NodeStructuralFeatures] = []
    counter = 0

    def walk(node: Node, depth: int) -> tuple[int, int]:
        nonlocal counter
        node_id = counter
        counter += 1

        child_sizes: list[int] = []
        subtree_size = 1
        max_child_depth = depth
        for child in node.children:
            child_subtree, child_max_depth = walk(child, depth + 1)
            child_sizes.append(child_subtree)
            subtree_size += child_subtree
            max_child_depth = max(max_child_depth, child_max_depth)

        child_count = len(node.children)
        leaf_ratio = (
            sum(1 for child in node.children if not child.children) / child_count
            if child_count
            else 1.0
        )
        if child_sizes:
            avg = sum(child_sizes) / len(child_sizes)
            variance = sum((size - avg) ** 2 for size in child_sizes) / len(child_sizes)
            sibling_uniformity = 1.0 / (1.0 + variance)
        else:
            sibling_uniformity = 1.0

        branching_factor = child_count / max(subtree_size, 1)
        loop_sig = _loop_signal(depth, subtree_size, child_count, max_child_depth)
        fn_sig = _function_signal(child_count, subtree_size, depth)
        call_den = _call_density(child_count, leaf_ratio, subtree_size)
        rec_sig = _recursion_signal(depth, subtree_size, call_den, max_child_depth)
        mut_sig = _mutation_signal(child_count, sibling_uniformity, leaf_ratio)
        iter_sig = _iteration_signal(loop_sig, branching_factor, subtree_size)

        features.append(
            NodeStructuralFeatures(
                node_id=node_id,
                raw_type=node.type,
                depth=depth,
                child_count=child_count,
                subtree_size=subtree_size,
                branching_factor=branching_factor,
                max_child_depth=max_child_depth,
                leaf_ratio=leaf_ratio,
                sibling_uniformity=sibling_uniformity,
                loop_signal=loop_sig,
                function_signal=fn_sig,
                call_density=call_den,
                recursion_signal=rec_sig,
                mutation_signal=mut_sig,
                iteration_signal=iter_sig,
            )
        )
        return subtree_size, max_child_depth

    if tree.root_node:
        walk(tree.root_node, 0)
    return features


def aggregate_tree_metrics(nodes: list[NodeStructuralFeatures]) -> dict[str, float | int | bool]:
    if not nodes:
        return {
            "loop_presence": False,
            "function_presence": False,
            "call_density": 0.0,
            "nesting_depth": 0,
            "branching_factor": 0.0,
            "recursion_indicators": 0.0,
            "mutation_signals": 0.0,
            "iteration_signals": 0.0,
        }

    loop_presence = any(n.loop_signal >= 0.45 for n in nodes)
    function_presence = any(n.function_signal >= 0.4 for n in nodes)
    return {
        "loop_presence": loop_presence,
        "function_presence": function_presence,
        "call_density": round(sum(n.call_density for n in nodes) / len(nodes), 4),
        "nesting_depth": max(n.depth for n in nodes),
        "branching_factor": round(sum(n.branching_factor for n in nodes) / len(nodes), 4),
        "recursion_indicators": round(max(n.recursion_signal for n in nodes), 4),
        "mutation_signals": round(sum(n.mutation_signal for n in nodes) / len(nodes), 4),
        "iteration_signals": round(max(n.iteration_signal for n in nodes), 4),
    }
