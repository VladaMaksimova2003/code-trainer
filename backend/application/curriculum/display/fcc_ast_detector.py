"""Tree-sitter AST layer for FCC pattern detection on the target language (thesis §3.2.8)."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Callable

from application.curriculum.display.pitfall_catalog import PitfallSpec
from infrastructure.analysis.tree_sitter_gateway import parse_code

FccAstCheck = Callable[[object, str], bool]

_PASCAL_COMP = frozenset({"kLte", "kLt", "kGte", "kGt", "kEq", "kNeq"})
_CPP_COMP = frozenset({"<=", "<", ">=", ">", "==", "!="})


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _safe_parse(code: str, language_id: str):
    if not str(code or "").strip():
        return None
    try:
        return parse_code(code, language_id)
    except Exception:
        return None


def _decode(node) -> str:
    return node.text.decode("utf-8", errors="replace")


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def _has_descendant(node, *, node_type: str | None = None, text: str | None = None) -> bool:
    for item in _walk(node):
        if node_type and item.type == node_type:
            return True
        if text is not None and _decode(item) == text:
            return True
    return False


def _has_real_division(root, lang: str) -> bool:
    if lang == "pascal":
        for node in _walk(root):
            if node.type != "kFdiv":
                continue
            if _inside_string_literal(node):
                continue
            return True
        return False
    if lang in {"cpp", "csharp", "java"}:
        for node in _walk(root):
            if node.type != "binary_expression":
                continue
            for child in node.children:
                if _decode(child) == "/" and child.type not in {"comment", "line_comment"}:
                    if _inside_string_literal(node):
                        continue
                    return True
    return False


def _inside_string_literal(node) -> bool:
    current = node.parent
    while current is not None:
        if current.type in {"string", "string_literal", "interpreted_string_literal"}:
            return True
        current = current.parent
    return False


def _has_writeln_real_division(root, lang: str) -> bool:
    if lang != "pascal":
        return False
    for node in _walk(root):
        if node.type != "exprCall":
            continue
        name = next(
            (_decode(child) for child in node.children if child.type == "identifier" and child.is_named),
            "",
        )
        if name.lower() != "writeln":
            continue
        if _has_descendant(node, node_type="kFdiv"):
            return True
    return False


def _has_zero_subscript(root, lang: str) -> bool:
    if lang == "pascal":
        for node in _walk(root):
            if node.type != "exprSubscript":
                continue
            if _inside_string_literal(node):
                continue
            for child in _walk(node):
                if child.type == "literalNumber" and _decode(child).strip() == "0":
                    return True
        return False
    if lang in {"cpp", "csharp", "java", "python"}:
        for node in _walk(root):
            if node.type not in {"subscript_expression", "element_access_expression", "subscript"}:
                continue
            if _inside_string_literal(node):
                continue
            for child in _walk(node):
                if child.type in {"number_literal", "integer_literal", "literalNumber"}:
                    if _decode(child).strip() == "0":
                        return True
    return False


def _has_percent_modulus(root, lang: str) -> bool:
    for node in _walk(root):
        if _decode(node) == "%":
            return True
    return False


def _comparison_ops(lang: str) -> frozenset[str]:
    if lang == "pascal":
        return _PASCAL_COMP
    if lang in {"cpp", "csharp", "java"}:
        return _CPP_COMP
    return frozenset()


def _is_comparison_binary(node, lang: str) -> bool:
    ops = _comparison_ops(lang)
    if lang == "pascal" and node.type == "exprBinary":
        return any(child.type in ops for child in node.children)
    if lang in {"cpp", "csharp", "java"} and node.type == "binary_expression":
        return any(child.type in ops or _decode(child) in ops for child in node.children)
    return False


def _has_chained_comparison(root, lang: str) -> bool:
    for node in _walk(root):
        if not _is_comparison_binary(node, lang):
            continue
        nested = [
            child
            for child in node.children
            if child.is_named and _is_comparison_binary(child, lang)
        ]
        if nested:
            return True
    return False


def _has_python_and_or(root, lang: str) -> bool:
    if lang not in {"cpp", "csharp"}:
        return False
    for node in _walk(root):
        if node.type != "binary_expression":
            continue
        for child in node.children:
            if child.type in {"and", "or"} or _decode(child).lower() in {"and", "or"}:
                return True
    return False


def _has_python_bool_literals(root, lang: str) -> bool:
    if lang != "pascal":
        return False
    for node in _walk(root):
        if node.type in {"kTrue", "kFalse"} and _decode(node) in {"True", "False"}:
            return True
        if node.type == "identifier" and _decode(node) in {"True", "False"}:
            return True
    return False


def _has_none_literal(root, lang: str) -> bool:
    for node in _walk(root):
        if node.type == "identifier" and _decode(node) == "None":
            if not _inside_string_literal(node):
                return True
    return False


def _has_for_range_off_by_one(root, lang: str) -> bool:
    """Detect Python-style loop bounds (start at 0) on target language."""
    if lang == "pascal":
        for node in _walk(root):
            if node.type != "for":
                continue
            for child in node.children:
                if child.type != "assignment":
                    continue
                for sub in _walk(child):
                    if sub.type == "literalNumber" and _decode(sub).strip() == "0":
                        return True
        return False
    if lang in {"cpp", "csharp", "java"}:
        for node in _walk(root):
            if node.type != "for_statement":
                continue
            for child in _walk(node):
                if child.type == "init_declarator":
                    text = _decode(child)
                    if re.search(r"\b=\s*0\b", text):
                        return True
                if child.type == "assignment_expression":
                    right = child.child_by_field_name("right")
                    if right is not None and right.type == "number_literal":
                        if _decode(right).strip() == "0":
                            return True
        return False
    if lang == "python":
        for node in _walk(root):
            if node.type != "for_statement":
                continue
            iterable = node.child_by_field_name("right")
            if iterable is None:
                continue
            if iterable.type == "call":
                fn = iterable.child_by_field_name("function")
                if fn is not None and _decode(fn) == "range":
                    return True
        return False
    return False


def _has_return_statement_in_pascal(root, lang: str) -> bool:
    if lang != "pascal":
        return False
    for node in _walk(root):
        if node.type != "statement":
            continue
        for child in node.children:
            if child.type == "identifier" and _decode(child).lower() == "return":
                return True
    return False


def _has_python_style_double_equals(root, lang: str) -> bool:
    """== in Pascal/C++ condition (Python habit)."""
    if lang == "pascal":
        for node in _walk(root):
            if node.type != "if":
                continue
            text = _decode(node)
            if "==" in text and not _inside_string_literal(node):
                return True
        return False
    if lang in {"cpp", "csharp", "java"}:
        for node in _walk(root):
            if node.type not in {"if_statement", "while_statement"}:
                continue
            condition = node.child_by_field_name("condition")
            if condition is None:
                continue
            for child in _walk(condition):
                if child.type == "assignment_expression":
                    return True
                if _decode(child) == "=" and child.type not in {"==", "!=", "<=", ">="}:
                    parent = child.parent
                    if parent is not None and parent.type == "binary_expression":
                        ops = [_decode(c) for c in parent.children if not c.is_named or c.type]
                        if "=" in ops and "==" not in ops and ":=" not in "".join(ops):
                            return True
        return False
    return False


def _has_sequential_single_readln(root, lang: str) -> bool:
    """Optional AFCC hint: multiple readln with one argument each."""
    if lang != "pascal":
        return False
    single_arg_calls = 0
    for node in _walk(root):
        if node.type not in {"exprCall", "exprcall"}:
            continue
        name = next(
            (_decode(child) for child in node.children if child.type == "identifier" and child.is_named),
            "",
        )
        if name.lower() != "readln":
            continue
        args = [c for c in node.children if c.type == "identifier" and c.is_named]
        if len(args) == 1:
            single_arg_calls += 1
    return single_arg_calls >= 2


def _named_type_sequence(root) -> list[str]:
    return [node.type for node in _walk(root) if node.is_named]


def code_outside_string_literals(code: str, language: str) -> str:
    """Return source text with string literal bodies removed for lex fallback."""
    del language  # quote stripping is enough for mirror languages here
    text = str(code or "")
    text = re.sub(r"'(?:''|[^'])*'", "''", text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    return text


def ast_structurally_similar(
    code: str,
    buggy_code: str,
    language: str,
    *,
    threshold: float = 0.90,
) -> bool:
    lang = _normalize_lang(language)
    tree = _safe_parse(code, lang)
    buggy_tree = _safe_parse(buggy_code, lang)
    if tree is None or buggy_tree is None:
        return False
    left = _named_type_sequence(tree.root_node)
    right = _named_type_sequence(buggy_tree.root_node)
    if not left or not right:
        return False
    return SequenceMatcher(None, left, right).ratio() >= threshold


FCC_AST_CHECKS: dict[tuple[str, str], FccAstCheck] = {
    ("integer_division", "pascal"): _has_real_division,
    ("integer_division", "cpp"): _has_real_division,
    ("integer_division", "csharp"): _has_real_division,
    ("integer_division", "java"): _has_real_division,
    ("float_division_pascal", "pascal"): _has_writeln_real_division,
    ("index_1based", "pascal"): _has_zero_subscript,
    ("index_1based", "cpp"): _has_zero_subscript,
    ("index_1based", "csharp"): _has_zero_subscript,
    ("index_1based", "java"): _has_zero_subscript,
    ("mod_negative", "pascal"): _has_percent_modulus,
    ("chain_comparison", "pascal"): _has_chained_comparison,
    ("chain_comparison", "cpp"): _has_chained_comparison,
    ("chain_comparison", "csharp"): _has_chained_comparison,
    ("chain_comparison", "java"): _has_chained_comparison,
    ("and_or_keywords", "cpp"): _has_python_and_or,
    ("and_or_keywords", "csharp"): _has_python_and_or,
    ("bool_literals", "pascal"): _has_python_bool_literals,
    ("null_vs_nil", "pascal"): _has_none_literal,
    ("null_vs_nil", "java"): _has_none_literal,
    ("null_vs_nil", "csharp"): _has_none_literal,
    ("assignment_vs_compare", "pascal"): _has_python_style_double_equals,
    ("assignment_vs_compare", "cpp"): _has_python_style_double_equals,
}

ATCC_PATTERN_CHECKS: dict[tuple[str, str], FccAstCheck] = {
    ("for_range_off_by_one", "pascal"): _has_for_range_off_by_one,
    ("for_range_off_by_one", "cpp"): _has_for_range_off_by_one,
    ("for_range_off_by_one", "csharp"): _has_for_range_off_by_one,
    ("for_range_off_by_one", "java"): _has_for_range_off_by_one,
    ("for_range_off_by_one", "python"): _has_for_range_off_by_one,
    ("scope_block", "pascal"): _has_return_statement_in_pascal,
}

AFCC_AST_CHECKS: dict[tuple[str, str], FccAstCheck] = {
    ("input_line_model", "pascal"): _has_sequential_single_readln,
}


def _tree_has_node_type(root, *types: str) -> bool:
    wanted = frozenset(types)
    return any(node.type in wanted for node in _walk(root))


def _ast_rule_applicable(root, pitfall_id: str, lang: str) -> bool:
    """Return False when parse succeeded but the AST lacks nodes needed to evaluate the rule."""
    if pitfall_id == "for_range_off_by_one":
        if lang == "pascal":
            return _tree_has_node_type(root, "for")
        if lang in {"cpp", "csharp", "java"}:
            return _tree_has_node_type(root, "for_statement")
        if lang == "python":
            return _tree_has_node_type(root, "for_statement")
    if pitfall_id == "scope_block" and lang == "pascal":
        return _tree_has_node_type(root, "function", "procedure", "statement")
    if pitfall_id == "input_line_model" and lang == "pascal":
        return _tree_has_node_type(root, "exprCall", "exprcall")
    return True


def fcc_ast_rule_keys() -> frozenset[tuple[str, str]]:
    return frozenset(FCC_AST_CHECKS.keys())


def mplt_ast_rule_keys() -> frozenset[tuple[str, str]]:
    return frozenset(FCC_AST_CHECKS.keys()) | frozenset(ATCC_PATTERN_CHECKS.keys()) | frozenset(AFCC_AST_CHECKS.keys())


def pitfall_has_ast_rule(pitfall_id: str, target_language: str) -> bool:
    lang = _normalize_lang(target_language)
    key = (str(pitfall_id or "").strip(), lang)
    return key in mplt_ast_rule_keys()


def _run_ast_check(checks: dict[tuple[str, str], FccAstCheck], pitfall_id: str, lang: str, code: str) -> bool | None:
    check = checks.get((pitfall_id, lang))
    if check is None:
        return None
    tree = _safe_parse(code, lang)
    if tree is None or tree.root_node is None:
        return None
    root = tree.root_node
    if not _ast_rule_applicable(root, pitfall_id, lang):
        return None
    return bool(check(root, lang))


def detect_fcc_pattern_ast(
    pitfall_id: str,
    target_language: str,
    code: str,
) -> bool | None:
    """Return True/False when AST rule exists; None if parse failed or no AST rule."""
    lang = _normalize_lang(target_language)
    return _run_ast_check(FCC_AST_CHECKS, str(pitfall_id or "").strip(), lang, code)


def detect_atcc_pattern_ast(
    pitfall_id: str,
    target_language: str,
    code: str,
) -> bool | None:
    lang = _normalize_lang(target_language)
    return _run_ast_check(ATCC_PATTERN_CHECKS, str(pitfall_id or "").strip(), lang, code)


def detect_afcc_pattern_ast(
    pitfall_id: str,
    target_language: str,
    code: str,
) -> bool | None:
    lang = _normalize_lang(target_language)
    return _run_ast_check(AFCC_AST_CHECKS, str(pitfall_id or "").strip(), lang, code)


def detect_mplt_pattern_ast(
    pitfall_id: str,
    target_language: str,
    code: str,
) -> bool | None:
    """Unified AST probe across FCC/ATCC/AFCC pattern tables."""
    for probe in (detect_fcc_pattern_ast, detect_atcc_pattern_ast, detect_afcc_pattern_ast):
        hit = probe(pitfall_id, target_language, code)
        if hit is not None:
            return hit
    return None


def detect_fcc_matches_buggy_ast(
    spec: PitfallSpec,
    *,
    target_language: str,
    code: str,
    buggy_code: str,
) -> bool | None:
    """Return True/False when conclusive; None when AST could not evaluate (use lex fallback)."""
    lang = _normalize_lang(target_language)
    pitfall_id = str(spec.get("id") or "")

    atcc_hit = detect_atcc_pattern_ast(pitfall_id, lang, code)
    if atcc_hit is True:
        return True
    if atcc_hit is False:
        return False

    fcc_hit = detect_fcc_pattern_ast(pitfall_id, lang, code)
    if fcc_hit is True:
        return True
    if fcc_hit is False and pitfall_has_ast_rule(pitfall_id, lang):
        return False

    if buggy_code.strip() and ast_structurally_similar(code, buggy_code, lang):
        return True
    return None
