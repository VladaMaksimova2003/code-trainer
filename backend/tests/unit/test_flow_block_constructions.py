from application.execution.services.flow_block_constructions import (
    validate_constructions_from_blocks,
)


def test_io_requires_input_and_output_blocks():
    errors, debug_items = validate_constructions_from_blocks(
        submitted_types=["start", "input", "end"],
        constructions=["io"],
    )

    assert len(errors) == 1
    assert errors[0]["type"] == "FLOW_CONSTRUCTION_MISSING"
    assert "не хватает" in errors[0]["text"].lower()
    assert debug_items


def test_nested_loops_requires_two_loop_blocks():
    errors, _debug_items = validate_constructions_from_blocks(
        submitted_types=["start", "loop", "end"],
        constructions=["nested_loops"],
    )

    assert len(errors) == 1
    assert errors[0]["type"] == "FLOW_CONSTRUCTION_MISSING"
