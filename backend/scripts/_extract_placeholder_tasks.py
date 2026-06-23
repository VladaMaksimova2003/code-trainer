"""Extract placeholder block tasks from docx."""
from __future__ import annotations

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(r"c:\Users\redmi\Downloads\final_course_270_tasks_with_placeholder_capstones.docx")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TASK = re.compile(r"^Задача\s+(\d+)\.\s*(.+)$")
LANGS = ["Pascal", "Python", "C++", "C#", "Java"]


def paras(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    out: list[str] = []
    for para in root.iter(f"{W}p"):
        t = "".join(n.text or "" for n in para.iter(f"{W}t")).strip()
        if t:
            out.append(t)
    return out


def main() -> None:
    lines = paras(SRC)
    tasks: dict[int, dict] = {}
    cur: int | None = None
    fmt: str | None = None
    phase = None
    tc_rows: list[dict] = []
    cur_tc: dict | None = None

    for line in lines:
        m = TASK.match(line)
        if m:
            if cur is not None and fmt:
                tasks[cur]["task_format"] = fmt
                tasks[cur]["test_cases"] = tc_rows
            cur = int(m.group(1))
            tasks[cur] = {"title": m.group(2).strip(), "test_cases": []}
            fmt = None
            phase = None
            tc_rows = []
            cur_tc = None
            continue
        if cur is None:
            continue
        if line == "Тип реализации":
            phase = "await_fmt"
            continue
        if phase == "await_fmt":
            fmt = line
            phase = None
            continue
        if line == "№" and fmt == "блоки с плейсхолдерами":
            phase = "tc_header"
            continue
        if phase == "tc_header" and line in {"Вход / данные", "Ожидаемый вывод / результат"}:
            continue
        if phase == "tc_header":
            if line.isdigit():
                if cur_tc:
                    tc_rows.append(cur_tc)
                cur_tc = {"idx": int(line)}
                continue
            if cur_tc is not None:
                if "inputs" not in cur_tc:
                    cur_tc["inputs"] = line
                else:
                    cur_tc["output"] = line
            continue
        if phase == "tc_header" and line in LANGS:
            if cur_tc:
                tc_rows.append(cur_tc)
                cur_tc = None
            phase = "lang_hdr"
            continue
        if phase == "lang_hdr" and line not in LANGS:
            phase = "concepts"
        if phase == "concepts" and "," in line and re.match(r"^[a-z_]", line.split(",")[0].strip()):
            tasks[cur]["concepts_line"] = line
            phase = "lang_hdr2"
            continue
        if phase == "lang_hdr2" and line in LANGS:
            phase = "codes"
            tasks[cur]["codes"] = {}
            continue
        if phase == "codes" and line in LANGS:
            phase = "code_lang"
            tasks[cur]["_pending_lang"] = line
            continue
        if phase == "code_lang":
            lang = tasks[cur].pop("_pending_lang", None)
            if lang:
                tasks[cur]["codes"][lang] = line
            phase = "codes"

    placeholder = {k: v for k, v in tasks.items() if v.get("task_format") == "блоки с плейсхолдерами"}
    capstone = {k: v for k, v in tasks.items() if "Проверочная" in v.get("title", "")}

    out = Path(__file__).resolve().parents[1] / "_placeholder_tasks.json"
    out.write_text(
        json.dumps(
            {
                "placeholder_count": len(placeholder),
                "capstone_count": len(capstone),
                "sample_placeholder_1": placeholder.get(1),
                "sample_placeholder_682_task": placeholder.get(13),  # io chapter task 13?
                "capstone_12": capstone.get(12),
                "placeholder_task_nums": sorted(placeholder.keys())[:30],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("placeholder", len(placeholder), "capstone", len(capstone), "->", out)


if __name__ == "__main__":
    main()
