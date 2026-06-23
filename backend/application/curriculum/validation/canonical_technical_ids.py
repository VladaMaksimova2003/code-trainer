"""Canonical technical concept ids shared by AST maps, semantic detectors, and display UI."""

from __future__ import annotations

# Explicit legacy id overrides (display registry source still uses old names in generator).
LEGACY_TO_CANONICAL: dict[str, str] = {
    "program_entry": "program_root",
    "ast_program_root": "program_root",
    "pas_program_begin_end": "program_root",
    "py_script_top_level": "program_root",
    "cs_top_level_statements": "program_root",
    "ast_main_entry": "main_entry",
    "py_main_guard": "main_entry",
    "cpp_main_return": "main_entry",
    "java_public_static_main": "main_entry",
    "ast_compound_statement": "block_scope",
    "typed_declaration": "variable_declaration",
    "ast_variable_declaration": "variable_declaration",
    "pas_var_const_type": "variable_declaration",
    "pas_typed_field": "variable_declaration",
    "py_simple_binding": "variable_declaration",
    "py_type_annotation": "variable_declaration",
    "cpp_typed_decl": "variable_declaration",
    "cs_var_decl": "variable_declaration",
    "java_field_decl": "variable_declaration",
    "ast_const_declaration": "constant_declaration",
    "symbol_visibility": "constant_declaration",
    "ast_assignment": "assignment",
    "ast_augmented_assignment": "assignment",
    "pas_assign_colon_eq": "assignment",
    "py_assign": "assignment",
    "cpp_assign": "assignment",
    "cs_assign": "assignment",
    "java_assign": "assignment",
    "arithmetic_ops": "arithmetic",
    "ast_binary_arithmetic": "arithmetic",
    "ast_unary_arithmetic": "arithmetic",
    "pas_div_mod": "arithmetic",
    "ast_relational_ops": "conditional",
    "ast_logical_ops": "conditional",
    "conditional_expression": "conditional",
    "stdin_read": "console_input",
    "stdout_write": "console_output",
    "ast_io_call": "console_output",
    "pas_readln_writeln": "console_output",
    "py_input_print": "console_output",
    "cpp_cin_cout": "console_output",
    "cs_console_read_write": "console_output",
    "java_scanner_system_out": "console_output",
    "io": "console_output",
    "ast_for_c": "loop",
    "ast_while": "loop",
    "ast_do_while": "loop",
    "ast_foreach": "collection_iteration",
    "for_counted": "loop",
    "for_collection": "collection_iteration",
    "pas_for_to_downto": "loop",
    "pas_repeat_until": "loop",
    "py_for_in": "loop",
    "py_while": "loop",
    "cpp_range_for": "collection_iteration",
    "cs_foreach": "collection_iteration",
    "java_enhanced_for": "collection_iteration",
    "ast_nested_loops": "nested_loop",
    "ast_break_continue": "loop",
    "nested_loops": "nested_loop",
    "counted_loop": "loop",
    "pre_condition_loop": "loop",
    "post_condition_loop": "loop",
    "collection_iteration": "collection_iteration",
    "nested_iteration": "nested_loop",
    "loop_control": "loop",
    "condition": "conditional",
    "simple_branch": "conditional",
    "multi_branch": "conditional",
    "switch_selection": "switch_selection",
    "function_invocation": "function_call",
    "ast_function_definition": "function_definition",
    "ast_call_expression": "function_call",
    "pas_function_procedure": "function_definition",
    "py_def": "function_definition",
    "function": "function_definition",
    "parameter_passing": "parameter_list",
    "ast_parameter_list": "parameter_list",
    "pas_value_var_ref": "parameter_list",
    "py_default_args": "parameter_list",
    "ast_self_call": "recursion",
    "ast_base_case_branch": "recursion",
    "pas_result_recursion": "recursion",
    "py_recursive_def": "recursion",
    "return_flow": "return_flow",
    "method_dispatch": "method_declaration",
    "object_instance": "class_type",
    "indexed_sequence": "indexed_access",
    "dynamic_array": "indexed_access",
    "string_sequence": "string_literal",
    "key_value_map": "map_type",
    "file_read": "file_io",
    "file_write": "file_io",
    "import_dependency": "import_module",
    "module_namespace": "import_module",
    "inheritance_hierarchy": "inheritance",
    "search_find": "search_find",
    "filter_select": "filter_select",
    "fold_aggregate": "fold_aggregate",
    "sort_order": "sort",
    "stack_queue": "linear_structure",
    "linked_node": "linear_structure",
    "tree_hierarchy": "tree_structure",
    "graph_edges": "graph_structure",
    "field_access": "member_access",
    "ast_linear_scan": "search_find",
    "ast_binary_search": "search_find",
    "ast_membership_test": "search_find",
    "py_in_operator": "search_find",
    "ast_binary_tree_node": "tree_structure",
    "ast_tree_traversal_pre_in_post": "tree_structure",
    "ast_recursive_tree_walk": "tree_structure",
    "ast_filter_loop": "filter_select",
    "ast_filter_builtin": "filter_select",
    "ast_fold_loop": "fold_aggregate",
    "ast_reduce_builtin": "fold_aggregate",
    "ast_sort_builtin": "sort",
    "ast_bubble_sort": "sort",
    "ast_graph_edge_list": "graph_structure",
    "ast_adjacency_list": "graph_structure",
    "ast_linked_list_node": "linear_structure",
    "ast_stack_push_pop": "linear_structure",
    "ast_queue_enqueue_dequeue": "linear_structure",
    "ast_polymorphism_override": "inheritance",
    "ast_virtual_method": "method_declaration",
    "ast_interface_impl": "class_type",
    "ast_record_type": "map_type",
    "ast_dict_literal": "map_type",
    "ast_struct_type": "map_type",
    "ast_enum_type": "class_type",
    "ast_namespace": "import_module",
    "ast_using_module": "import_module",
    "ast_package_import": "import_module",
    "ast_unit_uses": "import_module",
    "ast_file_open": "file_io",
    "ast_try_catch": "class_type",
    "ast_exception_throw": "class_type",
    # Short legacy names produced by prefix stripping or old card lists
    "vector": "indexed_access",
    "cpp_vector": "indexed_access",
    "pas_static_array": "indexed_access",
    "cs_array_list": "indexed_access",
    "java_array": "indexed_access",
    "iterator": "collection_iteration",
    "iterator_loop": "collection_iteration",
    "cpp_iterator_loop": "collection_iteration",
    "java_iterator": "collection_iteration",
    "ast_enumeration_loop": "collection_iteration",
    "py_enumerate_zip": "collection_iteration",
    "cs_ienumerable": "collection_iteration",
    "filter": "filter_select",
    "predicate_loop": "filter_select",
    "ast_predicate_loop": "filter_select",
    "reduce": "fold_aggregate",
    "py_reduce": "fold_aggregate",
    "cpp_accumulate": "fold_aggregate",
    "cs_aggregate": "fold_aggregate",
    "java_stream_reduce": "fold_aggregate",
    "ast_accumulator_pattern": "fold_aggregate",
    "orderby": "sort",
    "cs_orderby": "sort",
    "import": "import_module",
    "include": "import_module",
    "cpp_include": "import_module",
    "py_import_from": "import_module",
    "cs_using": "import_module",
    "java_import_package": "import_module",
    "ast_import": "import_module",
    "fstream": "file_io",
    "cpp_fstream": "file_io",
    "open_with": "file_io",
    "py_open_with": "file_io",
    "class": "class_type",
    "deque": "linear_structure",
    "py_deque": "linear_structure",
    "push_pop": "linear_structure",
    "bfs_dfs": "graph_structure",
    "ast_bfs_dfs": "graph_structure",
    "visited_set": "graph_structure",
    "ast_visited_set": "graph_structure",
    "pas_string_ops": "string_literal",
    "py_str_methods": "string_literal",
    "ast_string_concat": "string_literal",
    "ast_class_declaration": "class_type",
    "ast_array_subscript": "indexed_access",
    "ast_array_literal": "indexed_access",
}


def canonical_technical_id(raw: str) -> str:
    key = str(raw or "").strip()
    if not key:
        return key
    if key in LEGACY_TO_CANONICAL:
        return LEGACY_TO_CANONICAL[key]
    if key.startswith("ast_"):
        return _canonicalize_ast_legacy(key[4:])
    if key.startswith(("pas_", "py_", "cpp_", "cs_", "java_")):
        return _canonicalize_prefixed_legacy(key)
    return key


def _canonicalize_ast_legacy(suffix: str) -> str:
    if "assignment" in suffix or suffix in {"assign"}:
        return "assignment"
    if "const" in suffix:
        return "constant_declaration"
    if "variable" in suffix or suffix in {"var_decl", "field_decl"}:
        return "variable_declaration"
    if suffix in {"program_root", "program"} or suffix.startswith("program"):
        return "program_root"
    if "main" in suffix:
        return "main_entry"
    if "compound" in suffix or suffix == "block":
        return "block_scope"
    if "nested" in suffix:
        return "nested_loop"
    if any(token in suffix for token in ("for", "while", "do_while", "repeat")):
        return "loop"
    if "foreach" in suffix or "enhanced_for" in suffix or "range_for" in suffix:
        return "collection_iteration"
    if any(token in suffix for token in ("binary_arithmetic", "unary", "div_mod", "arithmetic")):
        return "arithmetic"
    if any(token in suffix for token in ("logical", "relational", "conditional", "branch", "if")):
        return "conditional"
    if "switch" in suffix or "case" in suffix:
        return "switch_selection"
    if any(token in suffix for token in ("io", "read", "write", "print", "input", "cin", "cout")):
        return "console_output"
    if any(token in suffix for token in ("scan", "search", "membership", "find")):
        return "search_find"
    if any(token in suffix for token in ("filter",)):
        return "filter_select"
    if any(token in suffix for token in ("fold", "aggregate", "accum", "reduce")):
        return "fold_aggregate"
    if "sort" in suffix:
        return "sort"
    if any(token in suffix for token in ("tree", "traversal")):
        return "tree_structure"
    if "graph" in suffix or "adjacency" in suffix or "edge" in suffix:
        return "graph_structure"
    if any(token in suffix for token in ("stack", "queue", "linked", "list_node")):
        return "linear_structure"
    if any(token in suffix for token in ("class", "struct", "record", "dict", "map", "enum")):
        return "class_type" if "record" not in suffix and "dict" not in suffix and "map" not in suffix else "map_type"
    if any(token in suffix for token in ("method", "procedure", "function", "constructor")):
        return "function_definition" if "constructor" not in suffix else "constructor"
    if "return" in suffix:
        return "return_flow"
    if "import" in suffix or "using" in suffix or "namespace" in suffix or "unit" in suffix:
        return "import_module"
    if "file" in suffix:
        return "file_io"
    if "string" in suffix:
        return "string_literal"
    if "array" in suffix or "index" in suffix or "subscript" in suffix:
        return "indexed_access"
    if "inherit" in suffix or "override" in suffix or "virtual" in suffix or "polymorph" in suffix:
        return "inheritance"
    return suffix


def _canonicalize_prefixed_legacy(key: str) -> str:
    for prefix, default in (
        ("pas_assign", "assignment"),
        ("py_assign", "assignment"),
        ("cpp_assign", "assignment"),
        ("cs_assign", "assignment"),
        ("java_assign", "assignment"),
        ("pas_div_mod", "arithmetic"),
        ("py_in_operator", "search_find"),
    ):
        if key.startswith(prefix) or key == prefix.rstrip("_"):
            return default
    body = key.split("_", 1)[-1]
    return _canonicalize_ast_legacy(body)


def canonicalize_technical_ids(raw_ids: list[str]) -> list[str]:
    return sorted({canonical_technical_id(item) for item in raw_ids if str(item).strip()})
