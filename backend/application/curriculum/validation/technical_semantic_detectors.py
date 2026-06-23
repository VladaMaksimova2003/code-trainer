"""Semantic curriculum concept detectors — AST walks beyond node-type counting.

Use for concepts that cannot be inferred reliably from a single tree-sitter node,
e.g. recursion, nested loops, console I/O, fold/aggregate patterns.
"""

from __future__ import annotations

import re
from collections import Counter

_LOOP_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset({"for_statement", "while_statement"}),
    "java": frozenset({"for_statement", "while_statement", "do_statement", "enhanced_for_statement"}),
    "cpp": frozenset({"for_statement", "while_statement", "do_statement", "range_based_for_statement"}),
    "csharp": frozenset({"for_statement", "while_statement", "do_statement", "foreach_statement"}),
    "pascal": frozenset({"for_statement", "while_statement", "repeat_statement", "for", "while", "repeat"}),
}

_CALL_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset({"call"}),
    "cpp": frozenset({"call_expression"}),
    "csharp": frozenset({"invocation_expression"}),
    "java": frozenset({"method_invocation"}),
    "pascal": frozenset({"call_statement", "exprCall"}),
}

_IO_INPUT_NAMES: dict[str, frozenset[str]] = {
    "python": frozenset({"input"}),
    "cpp": frozenset({"cin", "scanf", "getline"}),
    "csharp": frozenset({"Console.Read", "Console.ReadLine"}),
    "java": frozenset({"nextInt", "nextLine", "nextDouble", "next", "Scanner"}),
    "pascal": frozenset({"read", "readln"}),
}

_IO_OUTPUT_NAMES: dict[str, frozenset[str]] = {
    "python": frozenset({"print"}),
    "cpp": frozenset({"cout", "printf"}),
    "csharp": frozenset({"Console.Write", "Console.WriteLine"}),
    "java": frozenset({"println", "print"}),
    "pascal": frozenset({"write", "writeln"}),
}

_AUGMENTED_ASSIGNMENT_OPS = frozenset({"+", "-", "*", "/", "%"})
_ARITHMETIC_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset({"binary_operator", "unary_operator"}),
    "java": frozenset({"binary_expression", "unary_expression", "update_expression"}),
    "cpp": frozenset({"binary_expression", "unary_expression", "update_expression"}),
    "csharp": frozenset({"binary_expression", "unary_expression", "assignment_expression"}),
    "pascal": frozenset({"exprBinary", "exprUnary", "kAdd", "kSub", "kMul", "kFdiv", "kDiv", "kMod"}),
}


def detect_semantic_concepts(root, lang: str, code: str = "") -> dict[str, int]:
    """Return canonical technical id -> hit count for semantic detectors."""
    signals: Counter[str] = Counter()

    if has_main_entry(root, lang):
        signals["main_entry"] += 1
    if has_python_main_guard(root, lang):
        signals["main_entry"] += 1

    io_in, io_out = count_console_io(root, lang)
    if io_in:
        signals["console_input"] += io_in
    if io_out:
        signals["console_output"] += io_out

    if has_recursion(root, lang):
        signals["recursion"] += 1
    if has_nested_loops(root, lang):
        signals["nested_loop"] += 1
    if has_loop(root, lang):
        signals["loop"] += 1
    if has_fold_aggregate(root, lang):
        signals["fold_aggregate"] += 1
    if has_collection_iteration(root, lang):
        signals["collection_iteration"] += 1

    arithmetic_ops = count_arithmetic_ops(root, lang) if lang == "pascal" else 0
    if arithmetic_ops:
        signals["arithmetic"] += arithmetic_ops

    var_bindings = count_variable_bindings(root, lang)
    if var_bindings:
        signals["variable_declaration"] += var_bindings

    if has_search_find(root, lang, code):
        signals["search_find"] += 1

    lowered = code.lower()
    if lang == "pascal":
        if re.search(r"\bcase\b.+\bof\b", code, re.I | re.S):
            signals["switch_selection"] += 1
        if re.search(r"\belse\s+if\b", code, re.I):
            signals["multi_branch"] += 1
    elif lang == "python":
        if re.search(r"\belif\b", lowered):
            signals["multi_branch"] += 1
    elif lang in {"cpp", "csharp", "java"}:
        if re.search(r"\bswitch\s*\(", code):
            signals["switch_selection"] += 1
        if re.search(r"\belse\s+if\b", code, re.I):
            signals["multi_branch"] += 1

    return dict(signals)


def has_loop(root, lang: str) -> bool:
    loop_types = _LOOP_NODE_TYPES.get(lang, frozenset())
    if not loop_types:
        return False
    return any(node.type in loop_types for node in walk_nodes(root))


def count_arithmetic_ops(root, lang: str) -> int:
    """Arithmetic operations are represented differently across tree-sitter grammars."""
    node_types = _ARITHMETIC_NODE_TYPES.get(lang, frozenset())
    if not node_types:
        return 0

    hits = 0
    for node in walk_nodes(root):
        if node.type not in node_types:
            continue
        text = node.text.decode("utf-8", errors="replace")
        if lang == "pascal":
            if node.type in {"kAdd", "kSub", "kMul", "kFdiv", "kDiv", "kMod"}:
                hits += 1
            elif any(token in f" {text.lower()} " for token in (" + ", " - ", " * ", " / ", " div ", " mod ")):
                hits += 1
            continue
        if any(op in text for op in ("+", "-", "*", "/", "%")):
            hits += 1
    return hits


def has_search_find(root, lang: str, code: str = "") -> bool:
    """Linear scan / membership test: loop + conditional compare, or find/in helpers."""
    import re

    text = str(code or "")
    if re.search(r"\b(in|find|index|contains|IndexOf|binarySearch)\b", text, re.I):
        return True

    loop_types = _LOOP_NODE_TYPES.get(lang, frozenset())
    if not any(node.type in loop_types for node in walk_nodes(root)):
        return False
    if not any(
        node.type in {"if_statement", "conditional_expression"}
        for node in walk_nodes(root)
    ):
        return False
    if lang == "pascal":
        return bool(re.search(r"(=|<>|<=|>=|<|>)", text))
    return bool(re.search(r"(==|!=|<=|>=|<|>|[^!<>=]=[^=])", text))


def has_main_entry(root, lang: str) -> bool:
    if lang == "python":
        return _any_named_definition(root, "function_definition", "name", {b"main"})
    if lang == "cpp":
        return _any_named_definition(root, "function_definition", "name", {b"main"})
    if lang == "csharp":
        return _any_named_definition(root, "method_declaration", "name", {b"Main"})
    if lang == "java":
        return _any_java_main_method(root)
    if lang == "pascal":
        return b"program" in root.text.lower()
    return False


def has_python_main_guard(root, lang: str) -> bool:
    if lang != "python":
        return False
    for node in walk_nodes(root):
        if node.type != "if_statement":
            continue
        text = node.text.decode("utf-8", errors="replace")
        if "__name__" in text and "__main__" in text:
            return True
    return False


def count_console_io(root, lang: str) -> tuple[int, int]:
    input_names = _IO_INPUT_NAMES.get(lang, frozenset())
    output_names = _IO_OUTPUT_NAMES.get(lang, frozenset())
    if lang == "cpp":
        return _count_cpp_stream_io(root)

    if not input_names and not output_names:
        return 0, 0

    input_hits = 0
    output_hits = 0
    for node in walk_nodes(root):
        callee = call_callee_text(node, lang)
        if not callee:
            continue
        lowered = callee.lower()
        if any(name.lower() in lowered for name in input_names):
            input_hits += 1
        if any(name.lower() in lowered for name in output_names):
            output_hits += 1
    return input_hits, output_hits


def has_recursion(root, lang: str) -> bool:
    call_types = _CALL_TYPES.get(lang, frozenset())
    if not call_types:
        return False

    scope_types = {
        "python": {"function_definition"},
        "cpp": {"function_definition"},
        "csharp": {"method_declaration"},
        "java": {"method_declaration"},
        "pascal": {"function_declaration", "procedure_declaration"},
    }.get(lang, set())

    for scope in walk_nodes(root):
        if scope.type not in scope_types:
            continue
        name_node = scope.child_by_field_name("name")
        if name_node is None:
            continue
        fn_name = name_node.text
        if _calls_name_in_scope(scope, fn_name, call_types):
            return True
    return False


def has_nested_loops(root, lang: str) -> bool:
    loop_types = _LOOP_NODE_TYPES.get(lang, frozenset())
    if not loop_types:
        return False

    loop_nodes = [node for node in walk_nodes(root) if node.type in loop_types]
    for outer in loop_nodes:
        for inner in loop_nodes:
            if outer is inner:
                continue
            if is_ancestor(outer, inner):
                return True
    return False


def has_collection_iteration(root, lang: str) -> bool:
    """for-in / foreach over a collection (not a counted range loop)."""
    if lang == "python":
        for node in walk_nodes(root):
            if node.type != "for_statement":
                continue
            iterable = node.child_by_field_name("right")
            if iterable is None:
                continue
            if iterable.type == "call":
                fn = iterable.child_by_field_name("function")
                if fn is not None and fn.text == b"range":
                    continue
            return True
        return False

    loop_types = _LOOP_NODE_TYPES.get(lang, frozenset())
    collection_loop_types = {
        "csharp": frozenset({"foreach_statement"}),
        "java": frozenset({"enhanced_for_statement"}),
        "cpp": frozenset({"range_based_for_statement", "for_range_loop"}),
    }.get(lang, frozenset())
    if not collection_loop_types:
        return False
    return any(node.type in collection_loop_types for node in walk_nodes(root))


def count_variable_bindings(root, lang: str) -> int:
    """Python simple bindings (x = …) are declarations without a dedicated AST node."""
    if lang != "python":
        return 0

    binding_lhs_types = frozenset({"identifier", "tuple", "list", "pattern_list"})
    hits = 0
    for node in walk_nodes(root):
        if node.type == "annotated_assignment":
            hits += 1
            continue
        if node.type != "assignment":
            continue
        left = node.child_by_field_name("left")
        if left is not None and left.type in binding_lhs_types:
            hits += 1
    return hits


def has_fold_aggregate(root, lang: str) -> bool:
    loop_types = _LOOP_NODE_TYPES.get(lang, frozenset())
    if not loop_types:
        return False

    for loop in walk_nodes(root):
        if loop.type not in loop_types:
            continue
        if _loop_has_self_update(loop, lang):
            return True
    return False


def _loop_has_self_update(loop, lang: str) -> bool:
    assign_types = {
        "python": {"augmented_assignment", "assignment"},
        "cpp": {"assignment_expression", "update_expression"},
        "csharp": {"assignment_expression"},
        "java": {"assignment_expression", "update_expression"},
        "pascal": {"assignment"},
    }.get(lang, set())

    for node in walk_nodes(loop):
        if node.type not in assign_types:
            continue
        if lang == "python" and node.type == "augmented_assignment":
            return True
        if lang in {"cpp", "java"} and node.type == "update_expression":
            return True
        if lang == "pascal" and node.type == "assignment":
            children = [child for child in node.children if child.is_named]
            if len(children) >= 2:
                left_text = children[0].text.decode("utf-8", errors="replace").strip()
                right_text = children[-1].text.decode("utf-8", errors="replace")
                if left_text and left_text in right_text:
                    return True
            continue
        left = node.child_by_field_name("left") or node.child_by_field_name("name")
        right = node.child_by_field_name("right") or node.child_by_field_name("value")
        if left is None or right is None:
            continue
        left_text = left.text.decode("utf-8", errors="replace")
        if left_text and left_text in right.text.decode("utf-8", errors="replace"):
            return True
    return False


def _count_cpp_stream_io(root) -> tuple[int, int]:
    input_hits = 0
    output_hits = 0
    for node in walk_nodes(root):
        if node.type != "binary_expression":
            continue
        text = node.text.decode("utf-8", errors="replace").lower()
        if "cin" in text and ">>" in text:
            input_hits += 1
        if "cout" in text and "<<" in text:
            output_hits += 1
    return input_hits, output_hits


def call_callee_text(node, lang: str) -> str | None:
    if node.type not in _CALL_TYPES.get(lang, frozenset()):
        return None
    fn = node.child_by_field_name("function") or node.child_by_field_name("name")
    if fn is None and node.children:
        fn = node.children[0]
    if fn is None:
        return node.text.decode("utf-8", errors="replace")
    return fn.text.decode("utf-8", errors="replace")


def walk_nodes(root):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))


def is_ancestor(ancestor, descendant) -> bool:
    parent = descendant.parent
    while parent is not None:
        if parent == ancestor:
            return True
        parent = parent.parent
    return False


def _any_java_main_method(root) -> bool:
    for node in walk_nodes(root):
        if node.type != "method_declaration":
            continue
        text = node.text.decode("utf-8", errors="replace").lower()
        if "static" in text and "main" in text and "string[]" in text.replace(" ", ""):
            return True
    return False


def _any_named_definition(root, node_type: str, field: str, names: set[bytes]) -> bool:
    for node in walk_nodes(root):
        if node.type != node_type:
            continue
        name_node = node.child_by_field_name(field)
        if name_node is not None and name_node.text in names:
            return True
    return False


def _calls_name_in_scope(scope, target: bytes, call_types: frozenset[str]) -> bool:
    for node in walk_nodes(scope):
        if node.type not in call_types:
            continue
        fn = node.child_by_field_name("function")
        if fn is not None and fn.text == target:
            return True
        if fn is not None and fn.type == "attribute":
            attr = fn.child_by_field_name("attribute")
            if attr is not None and attr.text == target:
                return True
    return False
