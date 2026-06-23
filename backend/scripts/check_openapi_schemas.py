"""Smoke-check OpenAPI schemas for response_model coverage."""
from __future__ import annotations

from main import app

EXPECTED = [
    "PublicTaskDetailResponse",
    "StudentAnalyticsResponse",
    "TeacherAnalyticsResponse",
    "TeacherSubmissionsListResponse",
    "TeacherSubmissionDetailResponse",
    "CurriculumGlobalNextResponse",
    "CurriculumCollectionsViewResponse",
    "CurriculumCollectionNavigationResponse",
    "PascalShowcaseStudentViewResponse",
    "PascalShowcaseNextResponse",
    "PascalShowcaseTasksListResponse",
]

schema = app.openapi()["components"]["schemas"]
for key in EXPECTED:
    print(key, "OK" if key in schema else "MISSING")

paths = app.openapi()["paths"]
for path in ["/tasks/{task_id}", "/student/analytics", "/teacher/analytics", "/curriculum/next"]:
    get_op = paths.get(path, {}).get("get")
    if not get_op:
        print(path, "NO GET")
        continue
    ref = get_op["responses"]["200"]["content"]["application/json"]["schema"]
    print(path, ref)
