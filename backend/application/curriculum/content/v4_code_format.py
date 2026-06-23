"""Format minified v4 reference snippets for student-facing payloads."""

from __future__ import annotations

import re


def preserve_source_layout(code: str) -> str:
    """Keep authored line breaks and blank lines; trim trailing spaces per line only."""
    raw = str(code or "")
    if "\n" not in raw:
        return ""
    return "\n".join(line.rstrip() for line in raw.splitlines())


def normalize_authoring_code(code: str) -> str:
    """Return teacher/student code unchanged except normalized newlines and line-end trim."""
    raw = str(code or "")
    if not raw:
        return ""
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    if "\n" in normalized:
        lines = [line.rstrip() for line in normalized.splitlines()]
        result = "\n".join(lines)
        if normalized.endswith("\n"):
            result += "\n"
        return result
    return raw


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def _join_broken_for_in(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if (
            out
            and out[-1].startswith("for ")
            and " in " not in out[-1]
            and stripped.startswith("in ")
        ):
            out[-1] = f"{out[-1].rstrip()} {stripped}"
            continue
        out.append(stripped)
    return out


def _protect_python_calls(text: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def _stash(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"__PYCALL_{len(protected) - 1}__"

    out = text
    for pattern in (
        r"\bint\s*\(\s*input\s*\(\s*\)\s*\)",
        r"\bfloat\s*\(\s*input\s*\(\s*\)\s*\)",
        r"\bstr\s*\(\s*input\s*\(\s*\)\s*\)",
        r"\bmap\s*\(\s*int\s*,\s*input\s*\(\s*\)\.split\s*\(\s*\)\s*\)",
    ):
        out = re.sub(pattern, _stash, out, flags=re.I)
    return out, protected


def _restore_python_calls(text: str, protected: list[str]) -> str:
    out = text
    for index, original in enumerate(protected):
        out = out.replace(f"__PYCALL_{index}__", original)
    return out


def _protect_python_strings(text: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def stash(match: re.Match[str]) -> str:
        saved.append(match.group(0))
        return f"__PYSTR_{len(saved) - 1}__"

    out = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', stash, text)
    return out, saved


def _restore_python_strings(text: str, saved: list[str]) -> str:
    out = text
    for index, value in enumerate(saved):
        out = out.replace(f"__PYSTR_{index}__", value)
    return out


def format_python_code(code: str) -> str:
    raw = str(code or "")
    preserved = preserve_source_layout(raw)
    if preserved:
        return preserved

    one = _collapse_ws(raw.strip())
    one, protected_strings = _protect_python_strings(one)
    one, protected_lists = _protect_python_listcomps(one)
    one, protected_calls = _protect_python_calls(one)
    one = re.sub(r"(\S)(print\s*\()", r"\1\n\2", one, flags=re.I)
    one = re.sub(r"](?=\S)", "]\n", one)

    keywords = (
        "print",
        "input",
        "if",
        "elif",
        "else",
        "for",
        "while",
        "def",
        "class",
        "return",
        "import",
        "from",
        "try",
        "except",
        "with",
        "as",
        "break",
        "continue",
        "raise",
    )
    for kw in keywords:
        if kw == "input" and protected_calls:
            one = re.sub(rf"(?<=[A-Za-z0-9_\)\]])(?={kw}\b)", "\n", one)
            continue
        one = re.sub(rf"(?<=[A-Za-z0-9_\)\]])(?={kw}\b)", "\n", one)
        one = re.sub(rf"(?<!\w)({kw}\b)", r"\n\1", one)

    one = _restore_python_calls(one, protected_calls)
    one = _normalize_python_spacing(one)
    one = _restore_python_listcomps(one, protected_lists)
    one = _normalize_python_spacing(one)
    one = re.sub(r"(?<=[0-9]) (?=[A-Za-z_]+\s*=)", "\n", one)
    one = re.sub(r"(?<=[\)\}])(?!\s*for\b)(?!\s*if\b)\s+(?=[A-Za-z_#])", "\n", one)
    one = re.sub(r"(?<=\])\s+(?=[A-Za-z_#])", "\n", one)
    one = _restore_python_strings(one, protected_strings)
    lines = _join_broken_for_in([ln.strip() for ln in one.splitlines() if ln.strip()])

    formatted: list[str] = []
    indent = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("elif ", "else:", "except", "finally:")):
            indent = max(0, indent - 1)
        if ":" in stripped and not stripped.endswith(":"):
            head, tail = stripped.split(":", 1)
            tail = tail.strip()
            if tail:
                formatted.append(("    " * indent) + f"{head.strip()}:")
                tail = re.sub(r"(?<=[A-Za-z0-9_\)\]])(?=print\b)", "\n", tail)
                for piece in [part.strip() for part in tail.splitlines() if part.strip()]:
                    formatted.append(("    " * (indent + 1)) + piece)
                indent += 1
                continue
        if stripped.endswith(":"):
            formatted.append(("    " * indent) + stripped)
            indent += 1
            continue
        formatted.append(("    " * indent) + stripped)
        if stripped.startswith(("return ", "break", "continue", "raise ")):
            indent = max(0, indent - 1)

    return "\n".join(formatted).strip()


def format_pascal_code(code: str) -> str:
    raw = str(code or "")
    preserved = preserve_source_layout(raw)
    if preserved:
        return preserved

    one = _collapse_ws(raw.strip())
    if not one:
        return ""
    one = re.sub(r"\bdobegin\b", "do begin", one, flags=re.I)
    one = re.sub(r"\bthenbegin\b", "then begin", one, flags=re.I)
    one = re.sub(r"\belsebegin\b", "else begin", one, flags=re.I)
    one = re.sub(r"\bbeginassign\b", "begin assign", one, flags=re.I)
    one = re.sub(r"(begin)(readln\b)", r"\1\n\2", one, flags=re.I)
    one = re.sub(r"(begin)(writeln\b)", r"\1\n\2", one, flags=re.I)
    one = re.sub(r"(begin)(write\b)", r"\1\n\2", one, flags=re.I)
    one = re.sub(r"(begin)(if\b)", r"\1\n\2", one, flags=re.I)
    one = re.sub(r"(begin)(new\b)", r"\1\n\2", one, flags=re.I)
    one = re.sub(r"\)(else\b)", r")\n\1", one, flags=re.I)
    one = re.sub(r"(end\.)(begin\b)", r"\1\n\2", one, flags=re.I)
    one = re.sub(r"\s*\btype\b\s*", "\ntype ", one, flags=re.I)
    one = re.sub(r"\s*\bvar\b\s*", "\nvar ", one, flags=re.I)
    one = re.sub(r"\s*\bbegin\b\s*", "\nbegin\n", one, flags=re.I)
    one = re.sub(r"\s*\bfor\b\s*", "\nfor ", one, flags=re.I)
    one = re.sub(r"\s*\bif\b\s*", "\n  if ", one, flags=re.I)
    one = re.sub(r"\s*\bwriteln\b\s*", "\n  writeln", one, flags=re.I)
    one = re.sub(r"\s*\bwrite\b\s*", "\n  write", one, flags=re.I)
    one = re.sub(r"\s*\breadln\b\s*", "\n  readln", one, flags=re.I)
    one = re.sub(r"\s*\bnew\b\s*", "\n  new", one, flags=re.I)
    one = re.sub(r"\s*\belse\b\s*", "\nelse ", one, flags=re.I)
    one = re.sub(r"\bthen\s+(writeln\b|write\b)", r"then\n    \1", one, flags=re.I)
    one = re.sub(r"\belse\s+(writeln\b|write\b)", r"else\n    \1", one, flags=re.I)
    one = re.sub(r"\s*\bend\.\s*", "\nend.", one, flags=re.I)
    one = re.sub(r";\s*", ";\n", one)

    lines: list[str] = []
    for line in one.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in {"begin", "end."}:
            lines.append(stripped)
        elif stripped.startswith(("var ", "program ", "type ")):
            lines.append(stripped)
        elif stripped.startswith("else "):
            lines.append(stripped)
        else:
            if not stripped.startswith("  "):
                stripped = f"  {stripped.lstrip()}"
            lines.append(stripped)

    for index, line in enumerate(lines):
        prev = lines[index - 1].strip() if index > 0 else ""
        if prev.endswith("do") and line.strip().startswith("if "):
            lines[index] = f"    {line.strip()}"

    return "\n".join(lines).strip()


def _protect_regions(text: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def stash(match: re.Match[str]) -> str:
        saved.append(match.group(0))
        return f"__SAVE_{len(saved) - 1}__"

    out = str(text or "")
    out = re.sub(r'\$"(?:\\.|[^"\\])*"', stash, out)
    out = re.sub(r'"(?:\\.|[^"\\])*"', stash, out)
    out = re.sub(r"'(?:\\.|[^'\\])*'", stash, out)
    out = re.sub(r"<<|>>", stash, out)
    out = re.sub(r"<\s*\w+(?:\s*,\s*\w+)*\s*>", stash, out)
    return out, saved


def _restore_regions(text: str, saved: list[str]) -> str:
    out = text
    for index, value in enumerate(saved):
        out = out.replace(f"__SAVE_{index}__", value)
    return out


def _protect_python_listcomps(text: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def stash(match: re.Match[str]) -> str:
        saved.append(match.group(0))
        return f"__LIST_{len(saved) - 1}__"

    out = re.sub(r"\[[^\[\]]+\b(?:for|if)\b[^\[\]]+\]", stash, text)
    return out, saved


def _restore_python_listcomps(text: str, saved: list[str]) -> str:
    out = text
    for index, value in enumerate(saved):
        out = out.replace(f"__LIST_{index}__", value)
    return out


def _protect_internal_markers(text: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def stash(match: re.Match[str]) -> str:
        saved.append(match.group(0))
        return f"\x00M{len(saved) - 1}\x00"

    out = re.sub(r"__(?:LIST|PYCALL)_\d+__", stash, text)
    return out, saved


def _restore_internal_markers(text: str, saved: list[str]) -> str:
    out = text
    for index, value in enumerate(saved):
        out = out.replace(f"\x00M{index}\x00", value)
    return out


def _normalize_python_spacing(text: str) -> str:
    out, markers = _protect_internal_markers(text)
    out = re.sub(r"\(\s+", "(", out)
    out = re.sub(r"\s+\)", ")", out)
    out = re.sub(r"\bfor\s+(\w+)in\b", r"for \1 in", out, flags=re.I)
    out = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", out)
    out = _restore_internal_markers(out, markers)
    return out


def _split_statements_outside_parens(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == ";" and depth == 0:
            chunk = "".join(buf).strip()
            if chunk:
                parts.append(f"{chunk};")
            buf = []
            continue
        buf.append(char)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _split_c_family_prelude(text: str) -> str:
    out = text
    out = re.sub(r"(#include\s+[<\"][^>\"]+[>\"])\s*(?=[A-Za-z_#])", r"\1\n", out)
    out = re.sub(r"(import\s+(?:static\s+)?[^;]+;)\s*(?=[A-Za-z_#])", r"\1\n", out, flags=re.I)
    out = re.sub(r"(using\s+[^;]+;)\s*(?=[A-Za-z_#])", r"\1\n", out, flags=re.I)
    out = re.sub(
        r";\s*(?=(?:public|private|protected|class|interface|enum|namespace|int\s+main|void\s+main)\b)",
        ";\n",
        out,
        flags=re.I,
    )
    return out


def _repair_c_family_artifacts(text: str) -> str:
    out = str(text or "")
    out = re.sub(r"System\.out\.\s+print\b", "System.out.print", out)
    out = re.sub(r"System\.out\.\s+println\b", "System.out.println", out)
    out = re.sub(r"std::cout\s*\n\s*<<", "std::cout<<", out)
    out = re.sub(r"<<\s*\n\s*\"", "<<\"", out)
    return out


def _format_c_family_code(code: str) -> str:
    raw = str(code or "")
    preserved = preserve_source_layout(raw)
    if preserved:
        return preserved

    compact = raw.strip()
    if not compact:
        return ""

    if compact.count("\n") >= 3 and "/*" not in compact and "System.out. print" not in compact:
        return _repair_c_family_artifacts(compact)

    one = _collapse_ws(compact)
    one = _split_c_family_prelude(one)
    one, saved = _protect_regions(one)
    one = re.sub(r"\)\s*\{", ")\n{", one)
    one = re.sub(r"\s*\{\s*", "\n{\n", one)
    one = re.sub(r"\s*\}\s*", "\n}\n", one)
    one = _restore_regions(one, saved)

    formatted: list[str] = []
    depth = 0
    for segment in one.splitlines():
        stripped = segment.strip()
        if not stripped:
            continue
        if stripped == "{":
            formatted.append("    " * depth + "{")
            depth += 1
            continue
        if stripped == "}":
            depth = max(0, depth - 1)
            formatted.append("    " * depth + "}")
            continue
        for stmt in _split_statements_outside_parens(stripped):
            clean = stmt.strip()
            if not clean:
                continue
            if clean == "{":
                formatted.append("    " * depth + "{")
                depth += 1
                continue
            if clean == "}":
                depth = max(0, depth - 1)
                formatted.append("    " * depth + "}")
                continue
            formatted.append("    " * depth + clean)

    body = _repair_c_family_artifacts("\n".join(formatted).strip())
    if re.search(r"^\s*(?:import|using)\s", body, flags=re.I | re.M):
        body = re.sub(
            r"(^.*(?:import|using)[^\n]*;\n)(?=^\s*(?:class|namespace|public|interface)\b)",
            r"\1\n",
            body,
            count=1,
            flags=re.I | re.M,
        )
    return body


def format_cpp_code(code: str) -> str:
    return _format_c_family_code(code)


def format_csharp_code(code: str) -> str:
    return _format_c_family_code(code)


def format_java_code(code: str) -> str:
    return _format_c_family_code(code)


def format_reference_code(code: str, language: str) -> str:
    normalized = normalize_authoring_code(str(code or ""))
    if normalized and ("\n" in str(code or "") or "\r" in str(code or "")):
        return normalized

    preserved = preserve_source_layout(str(code or ""))
    if preserved:
        return preserved

    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        lang = "csharp"
    if lang == "python":
        return format_python_code(code)
    if lang == "pascal":
        return format_pascal_code(code)
    if lang == "cpp":
        return format_cpp_code(code)
    if lang == "csharp":
        return format_csharp_code(code)
    if lang == "java":
        return format_java_code(code)
    return str(code or "").strip()


_SLOT_RE = re.compile(r"\{(\d+)\}")


def _protect_assembly_slots(text: str) -> tuple[str, list[str]]:
    slots: list[str] = []

    def repl(match: re.Match[str]) -> str:
        slots.append(match.group(0))
        return f"__CT_ASM_SLOT_{len(slots) - 1}__"

    return _SLOT_RE.sub(repl, text), slots


def _restore_assembly_slots(text: str, slots: list[str]) -> str:
    out = text
    for index, slot in enumerate(slots):
        out = out.replace(f"__CT_ASM_SLOT_{index}__", slot)
    return out


def format_assembly_template(template: str, language: str) -> str:
    """Format minified block-assembly templates for display (preserves ``{n}`` slots)."""
    raw = str(template or "").strip()
    if not raw or not _SLOT_RE.search(raw):
        return raw

    if "\n" in raw:
        return "\n".join(line.rstrip() for line in raw.splitlines())

    body, slots = _protect_assembly_slots(raw)
    formatted = format_reference_code(body, language)
    return _restore_assembly_slots(formatted, slots)
