from application.curriculum.validation.expected_concept_checker import (
    format_construction_warning_messages,
    missing_expected_concept_messages,
)


def test_python_missing_stdin_read():
    code = "print('hello')"
    messages = missing_expected_concept_messages(
        code,
        ["stdout_write", "stdin_read"],
        language="python",
    )
    assert messages
    assert any("Ввод" in msg or "ввод" in msg.lower() for msg in messages)


def test_python_detects_console_io_and_loop():
    code = "name = input()\nprint(name)"
    messages = missing_expected_concept_messages(
        code,
        ["console_input", "console_output"],
        language="python",
    )
    assert messages == []


def test_format_construction_warning_single_summary_when_tests_passed():
    concept_check = {
        "enabled": True,
        "passed": False,
        "missing": ["variable_declaration"],
        "mode": "technical",
    }
    messages = format_construction_warning_messages(concept_check, tests_passed=True)
    assert len(messages) == 1
    assert "Тесты пройдены" in messages[0]["text"]
    assert "Переменные и типы" in messages[0]["text"]
    assert messages[0]["text"].count("Переменные и типы") == 1


def test_format_construction_warning_per_label_when_tests_not_passed():
    concept_check = {
        "enabled": True,
        "passed": False,
        "missing": ["variable_declaration", "counted_loop"],
        "mode": "technical",
    }
    messages = format_construction_warning_messages(concept_check, tests_passed=False)
    assert len(messages) == 2
    assert all("В коде не найдена" in item["text"] for item in messages)


def test_format_construction_warning_includes_example_snippet():
    concept_check = {
        "enabled": True,
        "passed": False,
        "missing": ["tc_search"],
        "mode": "display",
        "language": "java",
    }
    messages = format_construction_warning_messages(
        concept_check,
        tests_passed=False,
        language="java",
    )
    assert len(messages) == 1
    assert "Поиск в данных" in messages[0]["text"]
    assert "Ожидается приём" in messages[0]["text"]
    assert "position" in messages[0]["text"]
