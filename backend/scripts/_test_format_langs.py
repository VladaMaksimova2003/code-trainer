from application.curriculum.content.v4_reference_code import get_reference_code
from application.curriculum.content.v4_code_format import format_reference_code

for task in ["task_008", "task_002", "task_001"]:
    print(f"######## {task}")
    for lang in ["cpp", "java", "csharp", "python"]:
        raw = get_reference_code(task, lang)
        fmt = format_reference_code(raw, lang)
        print(f"=== {lang} ===")
        print(fmt[:600])
        print()
