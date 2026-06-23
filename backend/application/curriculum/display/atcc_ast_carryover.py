"""Tree-sitter AST layer for ATCC carryover detection (thesis §3.2.8)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from infrastructure.analysis.tree_sitter_gateway import parse_code

RuleKind = Literal["call_name", "node_type", "token_type", "identifier"]


@dataclass(frozen=True, slots=True)
class AtccAstRule:
    concept_id: str
    fragment: str
    kind: RuleKind
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AtccAstHit:
    concept_id: str
    fragment: str


# (source_language, target_language) → AST rules confirmed on target grammar.
AST_CARRYOVER_RULES: dict[tuple[str, str], tuple[AtccAstRule, ...]] = {
    ("pascal", "python"): (
        AtccAstRule("stdout_write", "writeln(...)", "call_name", ("writeln",)),
        AtccAstRule("stdin_read", "readln(...)", "call_name", ("readln",)),
        AtccAstRule("assignment", ":=", "token_type", (":=",)),
        AtccAstRule("counted_loop", "for i := … to … do", "token_type", ("kTo", "kDo")),
        AtccAstRule("arithmetic_ops", "div", "call_name", ("div",)),
        AtccAstRule("arithmetic_ops", "mod", "call_name", ("mod",)),
        AtccAstRule("simple_branch", "then", "token_type", ("kThen",)),
        AtccAstRule("switch_selection", "case x of", "token_type", ("kCase",)),
        AtccAstRule("program_entry", "begin", "token_type", ("kBegin",)),
        AtccAstRule("program_entry", "end.", "token_type", ("kEndDot", "kEnd")),
    ),
    ("python", "pascal"): (
        AtccAstRule("stdout_write", "print(...)", "call_name", ("print",)),
        AtccAstRule("stdin_read", "input()", "call_name", ("input",)),
        AtccAstRule("assignment", "elif", "node_type", ("elif_clause",)),
        AtccAstRule("counted_loop", "range(...)", "call_name", ("range",)),
        AtccAstRule("collection_iteration", "for x in …", "node_type", ("for_in_clause",)),
        AtccAstRule("function_definition", "def …", "node_type", ("function_definition",)),
        AtccAstRule("return_flow", "return", "node_type", ("return_statement",)),
    ),
    ("python", "cpp"): (
        AtccAstRule("stdout_write", "print(...)", "call_name", ("print",)),
        AtccAstRule("stdin_read", "input()", "call_name", ("input",)),
        AtccAstRule("counted_loop", "range(...)", "call_name", ("range",)),
    ),
    ("python", "java"): (
        AtccAstRule("stdout_write", "print(...)", "call_name", ("print",)),
        AtccAstRule("stdin_read", "input()", "call_name", ("input",)),
    ),
    ("python", "csharp"): (
        AtccAstRule("stdout_write", "print(...)", "call_name", ("print",)),
        AtccAstRule("stdin_read", "input()", "call_name", ("input",)),
    ),
    ("cpp", "python"): (
        AtccAstRule("stdout_write", "std::cout", "identifier", ("cout",)),
        AtccAstRule("stdin_read", "std::cin", "identifier", ("cin",)),
        AtccAstRule("import_dependency", "#include", "node_type", ("preproc_include",)),
    ),
    ("java", "python"): (
        AtccAstRule("stdout_write", "System.out.println", "identifier", ("System", "out")),
        AtccAstRule("program_entry", "public static void main", "node_type", ("method_declaration",)),
    ),
    ("csharp", "python"): (
        AtccAstRule("stdout_write", "Console.WriteLine", "identifier", ("Console", "WriteLine")),
    ),
}


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


def _call_name(node, language: str) -> str | None:
    lang = _normalize_lang(language)
    if lang == "python" and node.type == "call":
        for child in node.children:
            if child.type == "identifier" and child.is_named:
                return _decode(child)
            if child.type == "attribute":
                for part in child.children:
                    if part.type == "identifier" and part.is_named:
                        return _decode(part)
    if lang == "pascal" and node.type in {"exprCall", "exprcall"}:
        for child in node.children:
            if child.type == "identifier" and child.is_named:
                return _decode(child)
    if lang in {"cpp", "java", "csharp"} and node.type == "call_expression":
        for child in node.children:
            if child.type == "identifier" and child.is_named:
                return _decode(child)
            if child.type == "field_expression":
                parts = [
                    _decode(part)
                    for part in child.children
                    if part.type == "identifier" and part.is_named
                ]
                if parts:
                    return parts[-1]
    return None


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def _rule_matches(root, target_language: str, rule: AtccAstRule) -> bool:
    target = _normalize_lang(target_language)
    wanted = {value.lower() for value in rule.values}

    if rule.kind == "node_type":
        for node in _walk(root):
            if node.type in rule.values:
                return True
        return False

    if rule.kind == "token_type":
        for node in _walk(root):
            if node.type in rule.values:
                return True
            if _decode(node) in rule.values:
                return True
        return False

    if rule.kind == "call_name":
        for node in _walk(root):
            name = _call_name(node, target)
            if name and name.lower() in wanted:
                return True
        return False

    if rule.kind == "identifier":
        found: set[str] = set()
        for node in _walk(root):
            if node.type == "identifier" and node.is_named:
                found.add(_decode(node).lower())
            if node.type in {"field_expression", "scoped_identifier", "qualified_identifier"}:
                for part in node.children:
                    if part.type == "identifier" and part.is_named:
                        found.add(_decode(part).lower())
        return wanted.issubset(found) if len(wanted) > 1 else bool(found & wanted)

    return False


def detect_atcc_carryover_ast(
    source_language: str,
    target_language: str,
    code: str,
    *,
    expected_concepts: list[str] | None = None,
) -> list[AtccAstHit]:
    """Detect source-language idioms using Tree-sitter on the target grammar."""
    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if source == target:
        return []

    rules = AST_CARRYOVER_RULES.get((source, target))
    if not rules:
        return []

    tree = _safe_parse(code, target)
    if tree is None or tree.root_node is None:
        return []

    scope = {str(item).strip() for item in (expected_concepts or []) if str(item).strip()}
    hits: list[AtccAstHit] = []
    seen: set[tuple[str, str]] = set()

    for rule in rules:
        if scope and rule.concept_id not in scope:
            continue
        if not _rule_matches(tree.root_node, target, rule):
            continue
        key = (rule.concept_id, rule.fragment)
        if key in seen:
            continue
        seen.add(key)
        hits.append(AtccAstHit(concept_id=rule.concept_id, fragment=rule.fragment))

    return hits
