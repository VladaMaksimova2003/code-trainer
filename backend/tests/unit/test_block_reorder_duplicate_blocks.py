"""Slot assembly accepts equivalent duplicate block indices when labels match."""

from domain.entities.tasks.block_reorder_task import BlockReorderTask
from shared.enums import Difficulty, TaskType
from application.execution.block_reorder_validation import (
    _is_structurally_correct,
    enqueue_block_reorder_execution,
)


def _task6_entity() -> BlockReorderTask:
    blocks = [
        "total",
        "average",
        "count",
        "result",
        "total",
        "load",
        "n",
        "i",
        "load",
        "total",
        "n",
        "i",
        "n",
        "total",
        "load",
        "i",
    ]
    template = (
        "var n, i, load, {0}: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  {1} := 0;\n"
        "  for i := 1 to n do\n"
        "begin\n"
        "  readln(load);\n"
        "  total := total + {2};\n"
        "  end;\n"
        "  writeln(total div {3});\n"
        "end."
    )
    return BlockReorderTask(
        id=6,
        teacher_id=1,
        title="Average",
        description="",
        difficulty=Difficulty.EASY,
        task_type=TaskType.BLOCK_REORDER,
        original_code="",
        template=template,
        blocks=blocks,
        correct_order=[0, 4, 8, 12],
        language="pascal",
    )


def test_validate_answer_accepts_duplicate_block_with_same_label():
    entity = _task6_entity()
    assert entity.validate_answer([0, 4, 8, 12], "pascal")
    assert entity.validate_answer([0, 4, 5, 10], "pascal")


def test_structural_correct_for_equivalent_duplicate_indices():
    entity = _task6_entity()
    correct = [0, 4, 8, 12]
    alt = [0, 4, 5, 10]
    assembled = entity.build_code(alt, "pascal")
    assert _is_structurally_correct(
        entity,
        alt,
        "pascal",
        None,
        assembled,
        correct,
        variant_template=entity.template,
    )


def test_enqueue_synthesizes_passed_tests_for_slot_assembly():
    structural = {
        "needs_execution": False,
        "structural_correct": True,
        "partial": [True, True, True, True],
        "assembled_code": "program Demo;\nbegin\nend.",
        "message": "Correct solution",
        "test_cases": [
            {"inputs": "5\n10\n20\n30\n40\n50", "output": "30"},
            {"inputs": "1\n7", "output": "7"},
        ],
        "construction_warnings": [],
    }
    payload = enqueue_block_reorder_execution(structural, user_id="u1")
    assert payload["correct"] is True
    assert payload["execution_results"]
    assert all(row["status"] == "PASSED" for row in payload["execution_results"])
