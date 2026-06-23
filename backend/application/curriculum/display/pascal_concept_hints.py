"""Pascal-focused concept hints keyed by technical concept id."""

from __future__ import annotations

# Maps curriculum technical_concept_id → construction_hints.json pattern keys.
TC_CONSTRUCTION_PATTERNS: dict[str, list[str]] = {
    "program_entry": ["io"],
    "typed_declaration": ["assign"],
    "assignment": ["assign"],
    "arithmetic_ops": ["arith", "binary_expression"],
    "stdin_read": ["io"],
    "stdout_write": ["io"],
    "simple_branch": ["if_statement", "cond"],
    "multi_branch": ["if_statement", "cond"],
    "switch_selection": ["if_statement", "cond"],
    "conditional_expression": ["if_statement", "cond"],
    "counted_loop": ["for_loop", "loop"],
    "pre_condition_loop": ["while_loop", "loop"],
    "post_condition_loop": ["while_loop", "loop"],
    "loop_control": ["for_loop", "loop"],
    "nested_iteration": ["nested_loops", "loop"],
    "collection_iteration": ["for_loop", "loop"],
    "function_definition": ["function_definition"],
    "function_invocation": ["function_definition"],
    "return_flow": ["return_statement"],
    "indexed_sequence": ["assign"],
    "dynamic_array": ["for_loop", "loop"],
    "string_sequence": ["assign"],
    "key_value_map": ["assign"],
    "file_read": ["io"],
    "file_write": ["io"],
    "parameter_passing": ["function_definition"],
    "import_dependency": ["function_definition"],
    "module_namespace": ["function_definition"],
    "symbol_visibility": ["function_definition"],
    "recursion": ["function_definition", "return_statement"],
    "search_find": ["if_statement", "loop"],
    "filter_select": ["for_loop", "loop"],
    "fold_aggregate": ["for_loop", "arith"],
    "sort_order": ["if_statement", "loop"],
    "stack_queue": ["assign"],
    "linked_node": ["assign"],
    "tree_hierarchy": ["if_statement"],
    "graph_edges": ["assign"],
    "class_type": ["function_definition"],
    "object_instance": ["function_definition"],
    "method_dispatch": ["function_definition"],
    "inheritance_hierarchy": ["if_statement", "function_definition"],
}

PASCAL_HINTS_RU: dict[str, str] = {
    "assign_op": "`:=` — присваивание в Pascal (не `=`).",
    "compare_eq": "`=` — сравнение на равенство (не `==`).",
    "block": "`begin` / `end` — блок кода.",
    "io": "`readln` / `writeln` — ввод и вывод.",
    "for_inclusive": "`for i := 1 to n do` — цикл с включёнными границами.",
    "array_base": "Индексация массивов в Pascal часто начинается с 1.",
    "repeat_once": "`repeat` … `until` выполняется минимум один раз.",
    "var_param": "`var` в параметрах процедуры — передача по ссылке.",
    "program": "`program Name;` — точка входа программы.",
    "function_return": "Функция возвращает значение через имя функции: `Sq := x * x;`.",
}


def patterns_for_tc(technical_concept_id: str) -> list[str]:
    return list(TC_CONSTRUCTION_PATTERNS.get(technical_concept_id, ["assign"]))


def pascal_hints_for_tc(technical_concept_id: str) -> list[str]:
    """Short Pascal-specific hints for student UI."""
    hints: list[str] = []
    if technical_concept_id in {
        "assignment",
        "typed_declaration",
        "arithmetic_ops",
    }:
        hints.extend([PASCAL_HINTS_RU["assign_op"], PASCAL_HINTS_RU["compare_eq"]])
    if technical_concept_id in {"program_entry", "stdin_read", "stdout_write", "file_read", "file_write"}:
        hints.append(PASCAL_HINTS_RU["io"])
    if "loop" in technical_concept_id or technical_concept_id in {
        "counted_loop",
        "pre_condition_loop",
        "post_condition_loop",
        "nested_iteration",
        "collection_iteration",
    }:
        hints.append(PASCAL_HINTS_RU["for_inclusive"])
    if technical_concept_id == "post_condition_loop":
        hints.append(PASCAL_HINTS_RU["repeat_once"])
    if technical_concept_id in {"indexed_sequence", "dynamic_array"}:
        hints.append(PASCAL_HINTS_RU["array_base"])
    if technical_concept_id == "parameter_passing":
        hints.append(PASCAL_HINTS_RU["var_param"])
    if technical_concept_id == "program_entry":
        hints.append(PASCAL_HINTS_RU["program"])
    if technical_concept_id in {"function_definition", "function_invocation", "return_flow"}:
        hints.append(PASCAL_HINTS_RU["function_return"])
    if not hints:
        hints.append(PASCAL_HINTS_RU["block"])
    return hints
