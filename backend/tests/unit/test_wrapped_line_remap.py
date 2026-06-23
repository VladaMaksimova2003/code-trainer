from infrastructure.execution.output_parser import remap_wrapped_source_lines

OFFSET = 10

WRAPPED_STDERR = """  File "/tmp/home/source.py", line 12
    if n  2 == 0:
          ^
SyntaxError: invalid syntax
"""

REMAPPED_ONCE = """  File "/tmp/home/source.py", line 2
    if n  2 == 0:
          ^
SyntaxError: invalid syntax
"""


def test_remap_wrapped_syntax_error_line():
    result = remap_wrapped_source_lines(WRAPPED_STDERR, OFFSET)
    assert 'line 2' in result
    assert "line 12" not in result


def test_remap_is_idempotent_for_already_mapped_output():
    result = remap_wrapped_source_lines(REMAPPED_ONCE, OFFSET)
    assert result == REMAPPED_ONCE
