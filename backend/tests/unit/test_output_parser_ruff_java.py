from infrastructure.execution.output_parser import parse_diagnostics


def test_ruff_concise_output_maps_to_line_column():
    sample = "/tmp/home/abc/source.py:3:8: F821 Undefined name `undefined_name`"
    result = parse_diagnostics(sample)
    assert result == ["Line 3:8: error: F821 Undefined name `undefined_name`"]


def test_ruff_invalid_syntax_strips_noise_prefix():
    sample = "/tmp/home/abc/source.py:3:7: invalid-syntax: Expected a statement"
    result = parse_diagnostics(sample)
    assert result == ["Line 3:7: error: Expected a statement"]


def test_javac_error_output_maps_to_line():
    sample = "/tmp/home/abc/Main.java:5: error: cannot find symbol"
    result = parse_diagnostics(sample)
    assert result == ["Line 5: error: cannot find symbol"]


def test_javac_dedupes_multiple_messages_on_same_line():
    sample = "\n".join(
        [
            "/tmp/home/abc/Main.java:5: error: '.class' expected",
            "/tmp/home/abc/Main.java:5: error: ';' expected",
        ]
    )
    result = parse_diagnostics(sample)
    assert result == ["Line 5: error: '.class' expected"]


def test_ruff_and_javac_ignore_success_noise():
    assert parse_diagnostics("All checks passed!") == []
    assert parse_diagnostics("found 0 errors.") == []


def test_preformatted_line_diagnostics_are_preserved():
    sample = "Line 3:8: error: F821 Undefined name `undefined_name`"
    assert parse_diagnostics(sample) == [sample]
