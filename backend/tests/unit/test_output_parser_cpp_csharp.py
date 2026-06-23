from infrastructure.execution.output_parser import parse_diagnostics


def test_gcc_cpp_output_maps_to_line_column():
    sample = (
        "/tmp/home/abc/source.cpp:1:22: error: "
        "'undefined_var' was not declared in this scope"
    )
    result = parse_diagnostics(sample)
    assert result == [
        "Line 1:22: error: 'undefined_var' was not declared in this scope"
    ]


def test_roslyn_csharp_output_maps_to_line_column():
    sample = (
        "/tmp/home/abc/source.csx(1,9): error CS0103: "
        "The name 'undefinedName' does not exist in the current context"
    )
    result = parse_diagnostics(sample)
    assert result == [
        "Line 1:9: error: CS0103: The name 'undefinedName' does not exist in the current context"
    ]


def test_dotnet_build_style_csharp_output():
    sample = (
        "/tmp/home/abc/app/Program.cs(3,5): error CS0103: "
        "The name 'foo' does not exist in the current context "
        "[/tmp/home/abc/app/App.csproj]"
    )
    result = parse_diagnostics(sample)
    assert result == ["Line 3:5: error: CS0103: The name 'foo' does not exist in the current context"]
