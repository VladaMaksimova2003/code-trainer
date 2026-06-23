"""Tests for context-aware placeholder distractors."""

from application.curriculum.content.algo_syntax_task_extra import (
    _placeholder_assembly,
    algo_assembly_payload,
)
from application.curriculum.content.placeholder_distractors import enrich_gap_variants


def test_task6_pascal_distractors_use_code_context_not_generic_names():
    code = (
        "var n, i, load, ___p1___: integer;"
        "begin  readln(n);  ___p2___ := 0;"
        "  for i := 1 to n do  begin    readln(load);"
        "    total := total + ___p3___;  end;"
        "  writeln(total div ___p4___);end."
    )
    gaps = [
        {"id": "p1", "answer": "total", "label": "переменная total в объявлении"},
        {"id": "p2", "answer": "total", "label": "начальное значение суммы"},
        {"id": "p3", "answer": "load", "label": "добавляемое значение текущей загрузки"},
        {"id": "p4", "answer": "n", "label": "делитель для среднего значения"},
    ]
    enriched = enrich_gap_variants(gaps[0], all_gaps=gaps, placeholder_code=code, language="pascal")
    assert enriched[0] == "total"
    assert "average" not in enriched
    assert "count" not in enriched
    assert any(item in enriched for item in ("load", "n", "i", "sum", "s"))

    p4 = enrich_gap_variants(gaps[3], all_gaps=gaps, placeholder_code=code, language="pascal")
    assert p4[0] == "n"
    assert any(item in p4 for item in ("i", "load", "total"))


def test_placeholder_assembly_expands_block_pool_for_task6():
    _display, template, blocks, correct_order = algo_assembly_payload(
        "pas_006",
        "pascal",
        task_format="сборка_фрагмента",
    )
    assert "{0}" in template
    assert len(correct_order) >= 4
    assert len(blocks) >= 16
    assert "average" not in blocks
    assert blocks[correct_order[0]] == "total"
    assert blocks[correct_order[2]] == "load"
    assert blocks[correct_order[3]] == "n"


def test_python_loads_vs_load_confusion():
    code = "n = int(input())loads = [int(input()) for _ in range(n)]___p1___ = 0for ___p2___ in loads:    total += loadprint(total // ___p3___)"
    gaps = [
        {"id": "p1", "answer": "total", "label": "переменная суммы"},
        {"id": "p2", "answer": "load", "label": "переменная текущего элемента цикла"},
        {"id": "p3", "answer": "n", "label": "количество значений для деления"},
    ]
    p2 = enrich_gap_variants(gaps[1], all_gaps=gaps, placeholder_code=code, language="python")
    assert p2[0] == "load"
    assert "loads" in p2

    p3 = enrich_gap_variants(gaps[2], all_gaps=gaps, placeholder_code=code, language="python")
    assert p3[0] == "n"
    assert "len(loads)" in p3 or "loads" in p3

    _display, _template, blocks, order = _placeholder_assembly(code, gaps, language="python")
    assert blocks[order[2]] == "n"
    assert len(set(blocks)) >= 10
