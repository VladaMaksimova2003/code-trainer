"""CLI entry for Pascal Course v3.1.1 catalog (re-export)."""
from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (  # noqa: F401
    all_v311_slots,
    all_v311_task_records,
    catalog_summary,
    records_by_chapter,
    slots_by_chapter,
    validate_v311_catalog,
)

if __name__ == "__main__":
    errors = validate_v311_catalog()
    summary = catalog_summary()
    print("v3.1.1 catalog validation:", "OK" if not errors else "FAILED")
    for err in errors:
        print(" ", err)
    print("summary:", summary)
