from domain.entities.tasks.block_reorder_task import BlockReorderTask
from shared.enums import Difficulty, TaskType


def test_build_code_free_form_placeholder_template_joins_blocks():
    entity = BlockReorderTask(
        id=1,
        teacher_id=1,
        title="t",
        description="d",
        difficulty=Difficulty.EASY,
        task_type=TaskType.BLOCK_REORDER,
        original_code="program Demo;\nbegin\n  writeln('done');\nend.",
        template="___",
        blocks=[
            "program Demo;",
            "begin",
            "  writeln('done');",
            "end.",
        ],
        correct_order=[0, 1, 2, 3],
        language="pascal",
    )

    assembled = entity.build_code([0, 1, 2, 3], "pascal")
    assert assembled == "program Demo;\nbegin\n  writeln('done');\nend."


def test_build_code_slot_template_still_replaces_markers():
    entity = BlockReorderTask(
        id=2,
        teacher_id=1,
        title="t",
        description="d",
        difficulty=Difficulty.EASY,
        task_type=TaskType.BLOCK_REORDER,
        original_code="x := 1;",
        template="begin\n  {0}\nend.",
        blocks=["x := 1;"],
        correct_order=[0],
        language="pascal",
    )

    assert entity.build_code([0], "pascal") == "begin\n  x := 1;\nend."
