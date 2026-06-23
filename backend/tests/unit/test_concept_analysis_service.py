"""Teacher reference code → detected concepts."""
from __future__ import annotations

from application.analysis.concept_analysis_service import ConceptAnalysisService
from application.tasks.services.code_analysis_service import CodeAnalysisService


def test_analyze_reference_code_returns_concept_ids():
    code = (
        "n = int(input())\n"
        "total = 0\n"
        "for _ in range(n):\n"
        "    total += int(input())\n"
        "print(total)\n"
    )
    result = ConceptAnalysisService().analyze(code, "python")
    ids = set(result.concept_ids)
    assert "loop" in ids
    assert "io" in ids
    assert "variable" in ids
    assert "call" not in ids
    assert "return" not in ids


def test_code_analysis_service_patterns_use_concept_ids():
    code = "for i in range(3):\n    print(i)\n"
    analysis = CodeAnalysisService().analyze(code, "python")
    assert analysis.patterns
    assert all(p.id == p.type for p in analysis.patterns)
    assert all(p.id != "call" for p in analysis.patterns)
