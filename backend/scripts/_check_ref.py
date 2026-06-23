#!/usr/bin/env python3
from application.curriculum.content.v4_reference_code import get_reference_code

for slot in ("java_008", "task_008"):
    print(f"######## {slot}")
    for lang in ("cpp", "java", "csharp", "python", "pascal"):
        code = get_reference_code(slot, lang)
        print(f"=== {lang} ===")
        print(code[:600] if code else "(empty)")
        print()
