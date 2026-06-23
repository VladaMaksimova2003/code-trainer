from application.curriculum.content.v4_reference_code import get_reference_code
from application.curriculum.content.v4_reference_overrides import is_stub_reference_code
from application.curriculum.display.pascal_tc_pedagogy import _card_for


def test_stub_reference_detection():
    stub = "/* Линейный поиск */ for(int x:a) System.out. print(x+\" \" );"
    assert is_stub_reference_code(stub, "java")


def test_java_reference_override_for_search_task():
    code = get_reference_code("java_057", "java")
    assert "System.out. print" not in code
    assert "Scanner" in code
    assert "nextInt" in code


def test_tc_card_formats_cpp_java_examples():
    card = _card_for("filter_select")
    assert card is not None
    cpp_code = card["examples_by_language"]["cpp"][0]["code"]
    java_code = card["examples_by_language"]["java"][0]["code"]
    assert "copy_if" in cpp_code
    assert "stream" in java_code
    assert "System.out. print" not in java_code
