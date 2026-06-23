"""Detect curriculum concepts via tree-sitter AST + semantic passes."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from application.curriculum.validation.canonical_technical_ids import canonical_technical_id
from application.curriculum.validation.technical_concept_registry import (
    list_display_tc_cards,
    list_technical_concept_ids,
    load_ast_node_to_technical,
    load_ast_signal_to_technical,
    load_pascal_token_to_technical,
    load_technical_to_tc_map,
    normalize_display_card,
)
from application.curriculum.validation.technical_semantic_detectors import detect_semantic_concepts
from infrastructure.analysis.tree_sitter_gateway import parse_code


@dataclass(frozen=True, slots=True)
class TechnicalDetectionResult:
    """AST-confirmed ids, coarse signal ids, and rollup to display TC cards."""

    technical_ids: frozenset[str]
    signal_ids: frozenset[str]
    counts: dict[str, int]
    display_tc_ids: frozenset[str]


def detect_technical_concepts(
    code: str,
    language_id: str,
    *,
    concept_ids: frozenset[str] | None = None,
) -> TechnicalDetectionResult:
    lang = str(language_id).lower()
    target = concept_ids or frozenset(list_technical_concept_ids())
    tree = _safe_parse(code, lang)
    if tree is None or tree.root_node is None:
        return TechnicalDetectionResult(frozenset(), frozenset(), {}, frozenset())

    root = tree.root_node
    node_counts = _count_node_types(root)
    node_hits: Counter[str] = Counter()
    signal_hits: Counter[str] = Counter()

    for node_type, count in node_counts.items():
        if count <= 0:
            continue
        concept = (load_ast_node_to_technical().get(lang) or {}).get(node_type)
        if concept:
            node_hits[concept] += count
        signal = (load_ast_signal_to_technical().get(lang) or {}).get(node_type)
        if signal:
            signal_hits[signal] += count

    if lang == "pascal":
        lowered = code.lower()
        for token, concept in load_pascal_token_to_technical().items():
            if token.lower() in lowered:
                node_hits[concept] += 1

    for concept, amount in detect_semantic_concepts(root, lang, code).items():
        if amount > 0:
            node_hits[concept] += amount

    detected = {key for key, value in node_hits.items() if value > 0 and key in target}
    signals = {key for key, value in signal_hits.items() if value > 0 and key in target}
    if concept_ids is not None:
        detected = {key for key in detected if key in concept_ids}
        signals = {key for key in signals if key in concept_ids}

    all_counts = {**{k: node_hits[k] for k in detected}, **{k: signal_hits[k] for k in signals}}
    display_ids = rollup_to_display_tc(detected | signals)
    return TechnicalDetectionResult(
        technical_ids=frozenset(detected),
        signal_ids=frozenset(signals),
        counts=all_counts,
        display_tc_ids=display_ids,
    )


def rollup_to_display_tc(technical_ids: set[str] | frozenset[str]) -> frozenset[str]:
    mapping = load_technical_to_tc_map()
    out: set[str] = set()
    for concept_id in technical_ids:
        tc_id = mapping.get(concept_id)
        if tc_id:
            out.add(tc_id)
    return frozenset(out)


def validate_technical_to_tc_map() -> list[str]:
    cards = list_display_tc_cards()
    issues: list[str] = []
    known = set(list_technical_concept_ids())
    for technical_id, display_id in load_technical_to_tc_map().items():
        if technical_id not in known:
            issues.append(f"technical_to_tc_map references unknown technical id '{technical_id}'")
        if display_id not in cards:
            issues.append(
                f"technical_to_tc_map['{technical_id}'] -> unknown display card '{display_id}'"
            )
    return issues


def validate_ast_node_mappings() -> list[str]:
    rollup = load_technical_to_tc_map()
    issues: list[str] = []
    for section_name, loader in (
        ("nodes", load_ast_node_to_technical),
        ("signal_nodes", load_ast_signal_to_technical),
    ):
        for lang, lang_map in loader().items():
            for node_type, technical_id in lang_map.items():
                if technical_id not in rollup:
                    issues.append(
                        f"ast_node_to_technical[{section_name}][{lang}][{node_type}] "
                        f"-> '{technical_id}' has no entry in technical_to_tc_map"
                    )
    for token, technical_id in load_pascal_token_to_technical().items():
        if technical_id not in rollup:
            issues.append(
                f"pascal_tokens['{token}'] -> '{technical_id}' "
                f"has no entry in technical_to_tc_map"
            )
    return issues


def validate_display_registry_illustrates() -> list[str]:
    """UI registry ``illustrates`` tags must canonicalize to known rollup ids."""
    rollup_keys = set(load_technical_to_tc_map().keys())
    issues: list[str] = []
    for tc_id, raw_card in list_display_tc_cards().items():
        card = normalize_display_card(raw_card)
        for concept_id in card.get("technical_concept_ids") or []:
            canonical = canonical_technical_id(concept_id)
            if canonical not in rollup_keys:
                issues.append(f"{tc_id} technical_concept_ids contains unknown id '{concept_id}'")
        for language, rows in (card.get("hints_by_language") or {}).items():
            for index, row in enumerate(rows or []):
                for item in row.get("illustrates") or []:
                    canonical = canonical_technical_id(str(item))
                    if canonical not in rollup_keys:
                        issues.append(
                            f"{tc_id} hint[{language}#{index}] illustrates unknown id '{item}'"
                        )
    return issues


def validate_display_registry_covers() -> list[str]:
    """Backward-compatible alias."""
    return validate_display_registry_illustrates()


def technical_concept_label(concept_id: str) -> str:
    mapped = load_technical_to_tc_map().get(canonical_technical_id(concept_id))
    if mapped:
        card = list_display_tc_cards().get(mapped) or {}
        if card.get("name_ru"):
            return str(card["name_ru"])
    return concept_id


def phase_one_display_tc_ids() -> frozenset[str]:
    return frozenset({"tc_program_structure", "tc_variables_types", "tc_assignment"})


def _safe_parse(code: str, language_id: str):
    if not code.strip():
        return None
    try:
        return parse_code(code, language_id)
    except Exception:
        return None


def _count_node_types(root) -> Counter[str]:
    counts: Counter[str] = Counter()

    def walk(node) -> None:
        counts[node.type] += 1
        for child in node.children:
            walk(child)

    walk(root)
    return counts
