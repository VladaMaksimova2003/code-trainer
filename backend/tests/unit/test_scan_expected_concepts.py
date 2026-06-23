"""Tests for TC42 scan report and Java detection."""

from application.curriculum.validation.expected_concept_checker import (
    _label_for,
    analyze_expected_concepts,
    checker_coverage_for_language,
    detect_expected_concepts_in_code,
)


JAVA_MAX_SCORE = """
import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] scores = new int[n];
        for (int i = 0; i < n; i++) {
            scores[i] = sc.nextInt();
        }
        int best = scores[0];
        for (int score : scores) {
            if (score > best) {
                best = score;
            }
        }
        System.out.println(best);
    }
}
"""


def test_label_uses_display_registry_names():
    assert _label_for("loop", "Цикл") == "Циклы"
    assert _label_for("assignment", "Присваивание") == "Арифметика и операции"
    assert "Ввод" in _label_for("console_input", "Ввод")


def test_java_detects_core_concepts():
    found = set(detect_expected_concepts_in_code(JAVA_MAX_SCORE, language="java"))
    assert "tc_console_io" in found
    assert "tc_program_structure" in found
    assert "tc_loops" in found
    assert "tc_conditionals" in found
    assert "tc_arrays" in found
    assert "main_entry" not in found


def test_analyze_expected_concepts_reports_missing_reason():
    items = analyze_expected_concepts(
        "print('hello')",
        language="python",
        concept_ids=["console_output", "console_input"],
    )
    by_id = {item.id: item for item in items}
    assert by_id["console_output"].detected is True
    assert by_id["console_input"].detected is False
    assert by_id["console_input"].reason is not None
    assert "не найдена" in by_id["console_input"].reason


def test_java_checker_covers_canonical_ids():
    coverage = checker_coverage_for_language("java")
    assert "assignment" in coverage["covered"]
    assert coverage["missing_checker"] == []


def test_analyze_display_tc_ids_for_student_scan():
    items = analyze_expected_concepts(
        "x = 1\nfor i in range(3):\n    print(i)\n",
        language="python",
        concept_ids=["tc_arithmetic", "tc_loops", "tc_console_io"],
    )
    by_id = {item.id: item for item in items}
    assert by_id["tc_arithmetic"].detected is True
    assert by_id["tc_loops"].detected is True
    assert by_id["tc_console_io"].detected is True
