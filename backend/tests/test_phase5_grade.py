"""Phase 5 — simplified exam model."""
from __future__ import annotations

from application.analysis.core.exam_service import CoreExamService


def test_exam_service_minimal_payload():
    code = "def f(n):\n    for i in range(n):\n        pass\n"
    exam = CoreExamService().examine(
        code,
        "python",
        [{"type": "function", "min_count": 1}],
    )
    data = exam.to_dict()
    assert set(data.keys()) == {"result", "core"}
    assert set(data["core"].keys()) == {"detected", "missing"}
    assert data["result"] == "PASS"
