"""Resolve curriculum technical concepts from code + slot metadata."""

from __future__ import annotations

import re
from typing import Any

from application.curriculum.display.pascal_hint_engine import SHOWCASE_TECHNICAL_CONCEPTS

# tree-sitter / concepts.yml detector id → candidate curriculum TC ids.
DETECTOR_TO_CURRICULUM_TCS: dict[str, list[str]] = {
    "if_statement": [
        "simple_branch",
        "multi_branch",
        "switch_selection",
        "conditional_expression",
    ],
    "cond": ["simple_branch", "multi_branch", "conditional_expression"],
    "for_loop": ["counted_loop", "collection_iteration", "nested_iteration", "filter_select"],
    "while_loop": ["pre_condition_loop", "post_condition_loop", "loop_control"],
    "loop": [
        "counted_loop",
        "pre_condition_loop",
        "post_condition_loop",
        "collection_iteration",
        "nested_iteration",
        "loop_control",
    ],
    "nested_loops": ["nested_iteration"],
    "assign": ["assignment", "typed_declaration", "arithmetic_ops"],
    "arith": ["arithmetic_ops", "fold_aggregate"],
    "binary_expression": ["arithmetic_ops"],
    "io": ["stdin_read", "stdout_write"],
    "function_definition": [
        "function_definition",
        "return_flow",
        "parameter_passing",
        "recursion",
        "method_dispatch",
    ],
    "return_statement": ["return_flow", "function_definition"],
    "comprehension": ["filter_select", "collection_iteration"],
    "map": ["filter_select", "fold_aggregate"],
    "filter": ["filter_select"],
    "reduce": ["fold_aggregate"],
    "sort": ["sort_order"],
    "recursion": ["recursion"],
}

IO_CONCEPTS: frozenset[str] = frozenset(
    {"program_entry", "stdin_read", "stdout_write", "file_read", "file_write"}
)

# Which secondary TCs may appear alongside a slot's primary TC.
PRIMARY_RELATED: dict[str, frozenset[str]] = {
    "program_entry": IO_CONCEPTS | {"typed_declaration", "assignment"},
    "typed_declaration": frozenset({"assignment", "arithmetic_ops", "stdin_read", "stdout_write"}),
    "assignment": frozenset({"typed_declaration", "arithmetic_ops", "stdin_read", "stdout_write"}),
    "arithmetic_ops": frozenset({"assignment", "typed_declaration", "stdin_read", "stdout_write"}),
    "stdin_read": IO_CONCEPTS | {"assignment", "typed_declaration"},
    "stdout_write": IO_CONCEPTS | {"assignment", "typed_declaration"},
    "simple_branch": frozenset(
        {"multi_branch", "conditional_expression", "switch_selection", "stdin_read", "stdout_write"}
    ),
    "multi_branch": frozenset(
        {"simple_branch", "conditional_expression", "switch_selection", "stdin_read", "stdout_write"}
    ),
    "switch_selection": frozenset(
        {"simple_branch", "multi_branch", "conditional_expression", "stdin_read", "stdout_write"}
    ),
    "conditional_expression": frozenset(
        {"simple_branch", "multi_branch", "stdin_read", "stdout_write"}
    ),
    "counted_loop": frozenset(
        {
            "collection_iteration",
            "nested_iteration",
            "loop_control",
            "pre_condition_loop",
            "stdin_read",
            "stdout_write",
        }
    ),
    "pre_condition_loop": frozenset(
        {"post_condition_loop", "loop_control", "counted_loop", "stdin_read", "stdout_write"}
    ),
    "post_condition_loop": frozenset(
        {"pre_condition_loop", "loop_control", "stdin_read", "stdout_write"}
    ),
    "loop_control": frozenset({"counted_loop", "pre_condition_loop", "post_condition_loop"}),
    "nested_iteration": frozenset({"counted_loop", "collection_iteration"}),
    "collection_iteration": frozenset({"counted_loop", "nested_iteration", "filter_select", "fold_aggregate"}),
    "function_definition": frozenset(
        {"function_invocation", "return_flow", "parameter_passing", "recursion", "stdin_read", "stdout_write"}
    ),
    "function_invocation": frozenset({"function_definition", "return_flow", "stdin_read", "stdout_write"}),
    "return_flow": frozenset({"function_definition", "function_invocation"}),
    "indexed_sequence": frozenset({"dynamic_array", "collection_iteration", "stdin_read", "stdout_write"}),
    "dynamic_array": frozenset({"indexed_sequence", "collection_iteration", "stdin_read", "stdout_write"}),
    "string_sequence": frozenset({"indexed_sequence", "stdin_read", "stdout_write"}),
    "key_value_map": frozenset({"indexed_sequence", "string_sequence"}),
    "file_read": frozenset({"file_write", "stdin_read", "stdout_write"}),
    "file_write": frozenset({"file_read", "stdout_write"}),
    "parameter_passing": frozenset({"function_definition", "function_invocation"}),
    "import_dependency": frozenset({"module_namespace", "symbol_visibility"}),
    "module_namespace": frozenset({"import_dependency", "symbol_visibility"}),
    "symbol_visibility": frozenset({"import_dependency", "module_namespace"}),
    "recursion": frozenset({"function_definition", "return_flow"}),
    "search_find": frozenset({"filter_select", "collection_iteration", "simple_branch"}),
    "filter_select": frozenset({"search_find", "fold_aggregate", "collection_iteration"}),
    "fold_aggregate": frozenset({"filter_select", "collection_iteration", "arithmetic_ops"}),
    "sort_order": frozenset({"search_find", "collection_iteration"}),
    "stack_queue": frozenset({"linked_node", "collection_iteration"}),
    "linked_node": frozenset({"stack_queue", "tree_hierarchy"}),
    "tree_hierarchy": frozenset({"linked_node", "graph_edges", "recursion"}),
    "graph_edges": frozenset({"tree_hierarchy", "stack_queue", "linked_node"}),
    "class_type": frozenset({"object_instance", "method_dispatch", "inheritance_hierarchy"}),
    "object_instance": frozenset({"class_type", "method_dispatch"}),
    "method_dispatch": frozenset({"class_type", "object_instance", "inheritance_hierarchy"}),
    "inheritance_hierarchy": frozenset({"class_type", "method_dispatch", "object_instance"}),
}


def _accept_extra(primary: str, tc: str) -> bool:
    if tc == primary:
        return True
    related = PRIMARY_RELATED.get(primary, frozenset())
    return tc in related

# Heuristic Pascal patterns when tree-sitter grammar is unavailable.
PASCAL_TC_PATTERNS: dict[str, re.Pattern[str]] = {
    "program_entry": re.compile(r"\b(program\s+\w+|begin)\b", re.I),
    "typed_declaration": re.compile(r"\bvar\s+\w+\s*:\s*\w+", re.I),
    "assignment": re.compile(r":=", re.I),
    "stdin_read": re.compile(r"\breadln\b", re.I),
    "stdout_write": re.compile(r"\bwriteln\b", re.I),
    "simple_branch": re.compile(r"\bif\b.+\bthen\b", re.I | re.S),
    "multi_branch": re.compile(r"\belse\s+if\b", re.I),
    "switch_selection": re.compile(r"\bcase\b.+\bof\b", re.I | re.S),
    "counted_loop": re.compile(r"\bfor\s+\w+\s*:=", re.I),
    "pre_condition_loop": re.compile(r"\bwhile\b", re.I),
    "post_condition_loop": re.compile(r"\brepeat\b", re.I),
    "function_definition": re.compile(r"\bfunction\s+\w+", re.I),
    "function_invocation": re.compile(r"\w+\s*\([^)]*\)\s*;", re.I),
    "indexed_sequence": re.compile(r"\barray\s*\[", re.I),
    "dynamic_array": re.compile(r"\barray\s+of\b", re.I),
    "string_sequence": re.compile(r"\bstring\b", re.I),
    "class_type": re.compile(r"\btype\s+\w+\s*=\s*class\b", re.I),
    "object_instance": re.compile(r"\.Create\b", re.I),
    "method_dispatch": re.compile(r"\bfunction\s+\w+\.\w+", re.I),
    "inheritance_hierarchy": re.compile(r"\bclass\s*\(\s*\w+\s*\)", re.I),
    "parameter_passing": re.compile(r"\bprocedure\s+\w+\([^)]*\bvar\b", re.I),
    "recursion": re.compile(r"\bfunction\s+(\w+)[\s\S]*?\1\s*\(", re.I),
    "file_read": re.compile(r"\bReset\s*\(", re.I),
    "file_write": re.compile(r"\bRewrite\s*\(", re.I),
}

MAX_EXTRA_CONCEPTS = 3

# Pascal heuristics only for concepts that are not present in every program skeleton.
PASCAL_SPECIFIC_TCS: frozenset[str] = frozenset(
    {
        "simple_branch",
        "multi_branch",
        "switch_selection",
        "conditional_expression",
        "counted_loop",
        "pre_condition_loop",
        "post_condition_loop",
        "loop_control",
        "nested_iteration",
        "collection_iteration",
        "indexed_sequence",
        "dynamic_array",
        "string_sequence",
        "key_value_map",
        "class_type",
        "object_instance",
        "method_dispatch",
        "inheritance_hierarchy",
        "parameter_passing",
        "recursion",
        "file_read",
        "file_write",
        "search_find",
        "filter_select",
        "fold_aggregate",
        "sort_order",
        "stack_queue",
        "linked_node",
        "tree_hierarchy",
        "graph_edges",
    }
)


def _detect_from_source_code(source_code: str, source_language: str) -> set[str]:
    if not str(source_code or "").strip():
        return set()
    lang = str(source_language or "").lower()
    if lang not in {"python", "cpp", "java", "csharp", "javascript", "js"}:
        return set()

    try:
        from application.analysis.concept_analysis_service import ConceptAnalysisService

        result = ConceptAnalysisService().analyze(source_code, lang)
        detected_detector_ids = set(result.concept_ids)
    except Exception:
        return set()

    found: set[str] = set()
    for detector_id in detected_detector_ids:
        for tc in DETECTOR_TO_CURRICULUM_TCS.get(detector_id, []):
            if tc in SHOWCASE_TECHNICAL_CONCEPTS:
                found.add(tc)
    return found


def _detect_from_pascal_code(pascal_code: str) -> set[str]:
    if not str(pascal_code or "").strip():
        return set()
    found: set[str] = set()
    for tc, pattern in PASCAL_TC_PATTERNS.items():
        if tc not in PASCAL_SPECIFIC_TCS:
            continue
        if pattern.search(pascal_code):
            found.add(tc)
    return found


def _pick_pascal_reference(task_payload: dict[str, Any]) -> str:
    examples = task_payload.get("code_examples") or {}
    pascal = examples.get("pascal")
    if isinstance(pascal, str) and pascal.strip():
        return pascal
    template = task_payload.get("template")
    if isinstance(template, str) and template.strip():
        return template
    return ""


def _pick_source_code(task_payload: dict[str, Any], source_language: str) -> str:
    lang = str(source_language or "").lower()
    examples = task_payload.get("code_examples") or {}
    direct = examples.get(lang)
    if isinstance(direct, str) and direct.strip():
        return direct
    variants = task_payload.get("known_language_variants") or {}
    if isinstance(variants, dict):
        entry = variants.get(lang) or {}
        if isinstance(entry, dict):
            code = entry.get("source_code") or entry.get("code")
            if isinstance(code, str) and code.strip():
                return code
    if lang and str(task_payload.get("source_language") or "").lower() == lang:
        raw = task_payload.get("source_code")
        if isinstance(raw, str) and raw.strip():
            return raw
    return ""


def resolve_technical_concepts(
    *,
    primary_tc: str,
    task_payload: dict[str, Any] | None = None,
    source_language: str | None = None,
) -> list[str]:
    """Primary TC from slot metadata + optional detection from task code."""
    primary = str(primary_tc or "").strip()
    ordered: list[str] = []
    seen: set[str] = set()

    def add(tc: str) -> None:
        tc_id = str(tc).strip()
        if not tc_id or tc_id not in SHOWCASE_TECHNICAL_CONCEPTS or tc_id in seen:
            return
        seen.add(tc_id)
        ordered.append(tc_id)

    add(primary)

    payload = task_payload or {}
    pascal_code = _pick_pascal_reference(payload)
    for tc in sorted(_detect_from_pascal_code(pascal_code)):
        if _accept_extra(primary, tc):
            add(tc)

    known_langs: list[str] = []
    examples = payload.get("code_examples") or {}
    if isinstance(examples, dict):
        known_langs.extend(
            str(key).lower()
            for key in examples
            if str(key).lower() in {"python", "cpp", "java", "csharp"}
        )
    if source_language:
        known_langs.insert(0, str(source_language).lower())

    extra_from_source: set[str] = set()
    for lang in dict.fromkeys(known_langs):
        extra_from_source |= _detect_from_source_code(_pick_source_code(payload, lang), lang)

    extras = [
        tc
        for tc in sorted(extra_from_source)
        if tc != primary and tc not in seen and _accept_extra(primary, tc)
    ]
    for tc in extras[:MAX_EXTRA_CONCEPTS]:
        add(tc)

    return ordered