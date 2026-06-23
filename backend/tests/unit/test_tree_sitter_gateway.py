"""Tree-sitter gateway compatibility across package versions."""

from infrastructure.analysis.tree_sitter_gateway import parse_code


def test_parse_code_exposes_node_type():
    tree = parse_code("x = 1\nprint(x)\n", "python")
    root = tree.root_node
    assert root.type == "module"
    assert root.children
    assert root.children[0].type in ("assignment", "expression_statement")
    assert root.children[1].type in ("expression_statement", "call")


def test_detect_technical_concepts_does_not_crash():
    from application.curriculum.validation.technical_concept_detector import detect_technical_concepts

    result = detect_technical_concepts("for i in range(3):\n    print(i)\n", "python")
    assert "loop" in result.technical_ids or "counted_loop" in result.technical_ids
