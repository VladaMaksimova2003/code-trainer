from application.execution.block_reorder_validation import validate_block_reorder_structural


class _FakeRelation:
    blocks = ["a", "b"]
    language = "python"
    template = None


class _FakeEntity:
    template = None
    language = "python"

    def _get_variant(self, language):
        return {"blocks": self.blocks, "correct_order": [0, 1], "template": None}

    blocks = ["a", "b"]

    def validate_answer(self, order, language=None):
        return list(order) == [0, 1]

    def validate_partial(self, order, language=None):
        return [True, True] if list(order) == [0, 1] else [False, False]

    def build_code(self, order, language=None, indents=None):
        return "\n".join(self.blocks[i] for i in order)


class _FakeTask:
    id = 2
    task_type = "task_build_from_blocks"
    test_cases = [{"inputs": "1", "output": "1"}]
    block_reorder_task = _FakeRelation()


def test_wrong_order_with_assembled_code_skips_execution(monkeypatch):
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

    result = validate_block_reorder_structural(
        _Db(),
        task_id=2,
        order=[1, 0],
        assembled_code="b\na",
    )

    assert result is not None
    assert result["structural_correct"] is False
    assert result["needs_execution"] is True


def test_wrong_assembled_code_with_matching_order_indices(monkeypatch):
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

    result = validate_block_reorder_structural(
        _Db(),
        task_id=2,
        order=[0, 1],
        assembled_code="b\na",
    )

    assert result is not None
    assert result["structural_correct"] is False
    assert result["needs_execution"] is True
