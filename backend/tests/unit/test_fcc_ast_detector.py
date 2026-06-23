"""Unit tests for FCC Tree-sitter AST detector."""

from application.curriculum.display.fcc_ast_detector import (
    ast_structurally_similar,
    detect_atcc_pattern_ast,
    detect_fcc_pattern_ast,
    pitfall_has_ast_rule,
)
from application.curriculum.display.pitfall_catalog import get_pitfall
from application.curriculum.display.transfer_pitfall_detector import (
    detect_atcc_pitfall,
    detect_fcc_pitfall,
)


def test_ast_detects_pascal_slash_division():
    assert detect_fcc_pattern_ast("integer_division", "pascal", "writeln(total / n);") is True


def test_ast_ignores_slash_in_string_literal():
    assert (
        detect_fcc_pattern_ast(
            "integer_division",
            "pascal",
            "msg := 'total / n';\nwriteln(msg);",
        )
        is False
    )


def test_ast_ignores_slash_in_comment():
    code = "program T; begin { total / n } writeln(total div n); end."
    assert detect_fcc_pattern_ast("integer_division", "pascal", code) is False


def test_ast_detects_zero_subscript():
    code = "program T; var a: array[1..10] of integer; begin writeln(a[0]); end."
    assert detect_fcc_pattern_ast("index_1based", "pascal", code) is True


def test_ast_detects_cpp_chained_comparison():
    code = "int f(int a, int x, int b) { return (a <= x <= b); }"
    assert detect_fcc_pattern_ast("chain_comparison", "cpp", code) is True


def test_ast_detects_pascal_chained_comparison():
    code = "program T; begin if 0 <= x <= 100 then writeln(x); end."
    assert detect_fcc_pattern_ast("chain_comparison", "pascal", code) is True


def test_ast_detects_pascal_for_start_zero():
    code = "program T; begin for i := 0 to n do writeln(i); end."
    assert detect_atcc_pattern_ast("for_range_off_by_one", "pascal", code) is True


def test_ast_detects_pascal_return_statement():
    code = "function F: integer; begin return 1; end."
    assert detect_atcc_pattern_ast("scope_block", "pascal", code) is True


def test_ast_rule_coverage_for_priority_pitfalls():
    for pid in (
        "integer_division",
        "index_1based",
        "chain_comparison",
        "for_range_off_by_one",
        "scope_block",
    ):
        assert pitfall_has_ast_rule(pid, "pascal")


def test_fcc_integration_uses_ast_for_integer_division():
    spec = get_pitfall("integer_division")
    assert spec
    hits = detect_fcc_pitfall(
        spec,
        target_language="pascal",
        code="program T; begin writeln(total / n); end.",
    )
    assert hits
    assert hits[0]["detection"] == "ast"


def test_fcc_integration_index_in_string_not_flagged():
    spec = get_pitfall("index_1based")
    assert spec
    code = "program T; begin s := 'a[0]'; writeln(s); end."
    hits = detect_fcc_pitfall(spec, target_language="pascal", code=code)
    assert not hits


def test_fcc_regex_fallback_blocked_when_ast_rules_out():
    spec = get_pitfall("integer_division")
    assert spec
    code = "program T; begin s := 'x / y'; writeln(s); end."
    hits = detect_fcc_pitfall(spec, target_language="pascal", code=code)
    assert not hits


def test_atcc_for_range_uses_ast_not_lex():
    spec = get_pitfall("for_range_off_by_one")
    assert spec
    code = "program T; begin for i := 0 to n - 1 do writeln(a[i]); end."
    hits = detect_atcc_pitfall(spec, target_language="pascal", code=code)
    assert hits
    assert hits[0]["detection"] == "ast"


def test_atcc_scope_block_return_uses_ast():
    spec = get_pitfall("scope_block")
    assert spec
    code = "function Sum: integer; begin return 42; end."
    hits = detect_atcc_pitfall(spec, target_language="pascal", code=code)
    assert hits
    assert hits[0]["detection"] == "ast"


def test_atcc_correct_pascal_for_not_flagged():
    spec = get_pitfall("for_range_off_by_one")
    assert spec
    code = "program T; begin for i := 1 to n do writeln(a[i]); end."
    hits = detect_atcc_pitfall(spec, target_language="pascal", code=code)
    assert not hits


def test_ast_structural_similarity_for_buggy_pair():
    buggy = "program T; begin for i := 0 to n - 1 do writeln(a[i]); end."
    near = "program T; begin for i := 1 to n do writeln(a[i]); end."
    different = "program T; begin writeln('ok'); end."
    assert ast_structurally_similar(buggy, buggy, "pascal")
    assert not ast_structurally_similar(different, buggy, "pascal")
    assert not ast_structurally_similar(near, buggy, "pascal", threshold=0.95)
