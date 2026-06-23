"""Parse v4 course docx and regenerate v4_reference_code.py."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

LANG_KEYS = ("pascal", "python", "cpp", "csharp", "java")


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    parts: list[str] = []
    for node in root.iter():
        if node.tag.endswith("}t") and node.text:
            parts.append(node.text)
        elif node.tag.endswith("}br"):
            parts.append("\n")
    return "".join(parts)


def _strip_concept_prefix(blob: str) -> str:
    return re.sub(
        r"^(?:(?:program_entry|typed_declaration|simple_branch|counted_loop|stdin_read|"
        r"multi_branch|switch_selection|pre_condition_loop|post_condition_loop|loop_control|"
        r"nested_iteration|indexed_sequence|collection_iteration|dynamic_array|string_sequence|"
        r"function_definition|function_invocation|return_flow|parameter_passing|recursion|"
        r"search_find|filter_select|fold_aggregate|sort_order|key_value_map|file_read|"
        r"file_write|import_dependency|module_namespace|symbol_visibility|stack_queue|"
        r"linked_node|tree_hierarchy|graph_edges|comprehension|lambda|class_type|"
        r"object_instance|method_dispatch|inheritance_hierarchy)[^\n]*\n?)+",
        "",
        blob,
        flags=re.IGNORECASE,
    ).lstrip()


def _extract_codes_from_blob(blob: str) -> dict[str, str]:
    blob = _strip_concept_prefix(blob)
    if not blob.strip():
        return {}

    pascal = ""
    python = ""
    cpp = ""
    csharp = ""
    java = ""

    pascal_match = re.search(
        r"(?s)(program[\s\S]*?end\.|var[\s\S]*?end\.|type[\s\S]*?end\.)",
        blob,
    )
    if pascal_match:
        pascal = pascal_match.group(1).strip()
        tail = blob[pascal_match.end() :].lstrip()
    else:
        tail = blob.lstrip()

    py_end = len(tail)
    for marker in ("#include", "using System;", "using System.", "class Main{", "public class "):
        idx = tail.find(marker)
        if idx > 0:
            py_end = min(py_end, idx)
    boundary = re.search(r"(?<=[\)\}\.])(?=(?:int|double|float|long|char|bool|string|#include|using System|class Main))", tail)
    if boundary:
        py_end = min(py_end, boundary.start())

    python = tail[:py_end].strip()
    tail = tail[py_end:].lstrip()

    cpp_match = re.search(
        r"(?s)(?:(?:#include[\s\S]*?;)|(?:int[\s\S]*?std::cout[\s\S]*?;)|(?:float[\s\S]*?std::cout[\s\S]*?;)|"
        r"(?:double[\s\S]*?std::cout[\s\S]*?;))",
        tail,
    )
    if cpp_match:
        cpp = cpp_match.group(0).strip()
        tail = tail[cpp_match.end() :].lstrip()

    cs_match = re.search(r"(?s)(?:(?:using System[\s\S]*?;)|(?:int[\s\S]*?Console\.WriteLine[\s\S]*?;))", tail)
    if cs_match:
        csharp = cs_match.group(0).strip()
        tail = tail[cs_match.end() :].lstrip()

    java_match = re.search(
        r"(?s)(?:(?:class Main[\s\S]*?;)|(?:int[\s\S]*?System\.out\.println[\s\S]*?;)|"
        r"(?:public class[\s\S]*?System\.out\.println[\s\S]*?;))",
        tail,
    )
    if java_match:
        java = java_match.group(0).strip()

    if not python and not pascal:
        return {}

    return {
        "pascal": pascal,
        "python": python,
        "cpp": cpp,
        "csharp": csharp,
        "java": java,
    }


def parse_tasks(text: str) -> list[dict]:
    chunks = re.split(r"(?=Задача\s+\d+\.)", text)
    tasks: list[dict] = []
    for chunk in chunks:
        header = re.match(r"Задача\s+(\d+)\.\s*(.+?)(?=Краткое условие|Подробное условие|$)", chunk)
        if not header:
            continue
        num = int(header.group(1))
        title = header.group(2).strip()
        parts = chunk.split("PascalPythonC++C#Java")
        if len(parts) < 3:
            continue
        codes = _extract_codes_from_blob(parts[2])
        if not codes.get("python") and not codes.get("pascal"):
            continue
        tasks.append(
            {
                "num": num,
                "pattern_id": f"task_{num:03d}",
                "title": title,
                "codes": codes,
            }
        )
    return tasks


def _escape(code: str) -> str:
    return json.dumps(code, ensure_ascii=False)


def emit_reference_code(tasks: list[dict], out_path: Path) -> None:
    lines = [
        '"""Reference code for v4 tasks — all 5 languages per task."""',
        "from __future__ import annotations",
        "",
        "_TASK_REFERENCE_CODE: dict[str, dict[str, str]] = {",
    ]
    for task in sorted(tasks, key=lambda item: item["num"]):
        safe_title = re.sub(r"\s+", " ", task["title"]).strip()[:100]
        lines.append(f'    # Task {task["num"]}: {safe_title}')
        lines.append(f'    "{task["pattern_id"]}": {{')
        for lang in LANG_KEYS:
            code = _escape(task["codes"].get(lang, ""))
            lines.append(f'        "{lang}": {code},')
        lines.append("    },")
    lines.extend(
        [
            "}",
            "",
            "",
            "def get_reference_code(slot_id: str, language: str) -> str:",
            '    """Get reference code for a slot and language."""',
            "    import re",
            "",
            "    from application.curriculum.content.v4_code_format import format_reference_code",
            "",
            "    pat = slot_id",
            '    m = re.match(r"^(?:pas|py|cpp|cs|java)_(\\d+)$", slot_id)',
            "    if m:",
            '        pat = f"task_{int(m.group(1)):03d}"',
            '    raw = _TASK_REFERENCE_CODE.get(pat, {}).get(language, "")',
            "    if not raw:",
            '        m2 = re.match(r"^task_(\\d+)$", slot_id)',
            "        if m2:",
            '            pat = f"task_{int(m2.group(1)):03d}"',
            '            raw = _TASK_REFERENCE_CODE.get(pat, {}).get(language, "")',
            "    return format_reference_code(raw, language)",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "application" / "curriculum" / "content" / "v4_reference_code.py",
    )
    args = parser.parse_args()
    text = extract_docx_text(args.docx)
    tasks = parse_tasks(text)
    print(f"parsed {len(tasks)} tasks")
    if tasks:
        sample = tasks[2]
        print("sample task 3 python:", sample["codes"].get("python", "")[:80])
    emit_reference_code(tasks, args.out)


if __name__ == "__main__":
    main()
