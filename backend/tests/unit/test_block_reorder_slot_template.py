"""Tests for slot-template structural validation."""

from application.execution.block_reorder_validation import validate_block_reorder_structural


class _FakeRelation:
    blocks = ["integer", "real", "maximum", "writeln"]
    language = "pascal"
    template = "var x: {0}; {1}({2});"


class _FakeEntity:
    template = "var x: {0}; {1}({2});"
    language = "pascal"
    blocks = ["integer", "real", "maximum", "writeln"]

    def _get_variant(self, language):
        return {
            "blocks": self.blocks,
            "correct_order": [0, 2, 3],
            "template": self.template,
        }

    def _template_has_slots(self, template):
        import re

        return bool(template and re.search(r"\{\d+\}", template))

    def validate_answer(self, order, language=None):
        return list(order) == [0, 2, 3]

    def validate_partial(self, order, language=None):
        return [True, True, True]

    def build_code(self, order, language=None, indents=None):
        blocks = self.blocks
        template = self.template
        result = template
        for i, idx in enumerate(order):
            result = result.replace("{" + str(i) + "}", blocks[idx], 1)
        return result


class _FakeTask:
    id = 99
    task_type = "task_build_from_blocks"
    test_cases = [{"inputs": "1", "output": "1"}]
    block_reorder_task = _FakeRelation()


def test_slot_template_runs_tests_when_order_correct_despite_whitespace(monkeypatch):
    task = _FakeTask()
    entity = _FakeEntity()

    monkeypatch.setattr(
        "application.execution.block_reorder_validation.build_entity_from_db",
        lambda task, relation: entity,
    )
    monkeypatch.setattr(
        "application.execution.block_reorder_validation.is_build_from_blocks_task_type",
        lambda task_type: True,
    )

    class _Query:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return task

    class _Db:
        def query(self, model):
            return _Query()

    expected = entity.build_code([0, 2, 3], "pascal")
    formatted = expected.replace(";", ";\n")

    result = validate_block_reorder_structural(
        _Db(),
        task_id=99,
        order=[0, 2, 3],
        language="pascal",
        assembled_code=formatted,
    )

    assert result is not None
    assert result["structural_correct"] is True
    assert result["needs_execution"] is False
    assert result["assembled_code"] == expected
