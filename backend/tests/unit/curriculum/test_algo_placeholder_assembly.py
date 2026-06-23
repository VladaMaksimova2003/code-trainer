"""Tests for placeholder block assembly with repeated answers."""
from application.curriculum.content.algo_syntax_task_extra import _placeholder_assembly


def test_repeated_answer_gets_unique_block_indices():
    code = (
        "var n, i, load, ___p1___: integer;"
        "begin  readln(n);  ___p2___ := 0;"
        "  total := total + ___p3___;  writeln(total div ___p4___);end."
    )
    gaps = [
        {"id": "p1", "answer": "total", "variants": ["total", "average", "count"]},
        {"id": "p2", "answer": "total", "variants": ["total", "load", "n"]},
        {"id": "p3", "answer": "load", "variants": ["load", "total", "n"]},
        {"id": "p4", "answer": "n", "variants": ["n", "total", "load"]},
    ]
    _display, template, blocks, correct_order = _placeholder_assembly(code, gaps)

    assert len(correct_order) == 4
    assert len(set(correct_order)) == 4
    assert blocks[correct_order[0]] == "total"
    assert blocks[correct_order[1]] == "total"
    assert blocks[correct_order[0]] == blocks[correct_order[1]]
    assert correct_order[0] != correct_order[1]
    assert "{0}" in template and "{3}" in template
