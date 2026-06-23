"""Language-agnostic compiler/linter output parsing."""
from __future__ import annotations

import re

_LINT_SUCCESS_LINE = re.compile(
    r"^(all checks passed!*|found 0 errors?\.?|no issues found\.?)$",
    re.IGNORECASE,
)

_GCC_DIAG = re.compile(
    r"^(?P<path>(?:/tmp/home/)?[^:\s]+):(?P<line>\d+):(?P<col>\d+):\s+"
    r"(?P<sev>fatal error|error|warning):\s+(?P<msg>.+)$",
    re.IGNORECASE,
)

_SKIP_COMPILER_LINE = re.compile(
    r"^(In file included from|from /usr/|from \.\./|note:|candidate:|\s+\d+\s+\||\s+\^+\s*$)",
    re.IGNORECASE,
)

_FPC_SKIP_LINE = re.compile(
    r"^(Free Pascal Compiler|Copyright \(c\)|Target OS:|Compiling\s+|Linking\s+|"
    r"\d+\s+lines?\s+compiled|\d+\s+warning|\d+\s+error|Hint:|Note:)",
    re.IGNORECASE,
)
_FPC_NOISE_MESSAGE = re.compile(
    r"^(?:Fatal:\s*Compilation aborted|"
    r"Error:\s*/usr/bin/ppcx64|"
    r"Warning:\s*/usr/bin/ppcx64|"
    r"Error:\s*.*returned an error exitcode)",
    re.IGNORECASE,
)
_FPC_BARE_DIAG = re.compile(
    r"^(?P<sev>Error|Fatal|Warning):\s+(?P<msg>.+)$",
    re.IGNORECASE,
)
_FPC_DIAG = re.compile(
    r"^(?P<path>[^:]+?)\((?P<line>\d+),(?P<col>\d+)\)\s+"
    r"(?P<sev>Error|Fatal|Warning):\s+(?P<msg>.+)$",
    re.IGNORECASE,
)

# ruff concise: source.py:3:8: F821 Undefined name `x`
_RUFF_DIAG = re.compile(
    r"^(?P<path>(?:/tmp/home/)?[^:\s]+):(?P<line>\d+):(?P<col>\d+):\s+(?P<msg>.+)$"
)

# javac: Main.java:5: error: cannot find symbol
_JAVAC_DIAG = re.compile(
    r"^(?P<path>(?:/tmp/home/)?[^:\s]+):(?P<line>\d+):\s*"
    r"(?P<sev>error|warning):\s+(?P<msg>.+)$",
    re.IGNORECASE,
)

# Roslyn / dotnet-script: source.csx(1,9): error CS0103: message
_ROSLYN_DIAG = re.compile(
    r"^(?P<path>.+?)\((?P<line>\d+),(?P<col>\d+)\):\s+"
    r"(?P<sev>error|warning)\s+(?P<msg>.+)$",
    re.IGNORECASE,
)

_MAX_COMPILER_DIAGNOSTICS = 5

_STANDARD_LINE_DIAG = re.compile(
    r"^Line\s+(?P<line>\d+)(?::(?P<col>\d+))?\s*:\s*"
    r"(?P<sev>error|warning|fatal error|fatal)\s*:\s*(?P<msg>.+)$",
    re.IGNORECASE,
)
_RUFF_NOISE_PREFIX = re.compile(
    r"^(?:invalid-syntax|syntax-error|indentation-error|name-error|type-error):\s*",
    re.IGNORECASE,
)

_PY_FILE_LINE = re.compile(
    r'(File\s+"[^"]+",\s+line\s+)(\d+)',
    re.IGNORECASE,
)
_LINE_PREFIX = re.compile(r'^Line\s+(\d+)\b', re.IGNORECASE | re.MULTILINE)
_SOURCE_PATH_LINE = re.compile(
    r'(source\.[a-z]+:)(\d+)(:\d+)',
    re.IGNORECASE,
)


def _map_wrapped_line_number(line_num: int, line_offset: int) -> int:
    if line_num <= line_offset:
        return line_num
    return line_num - line_offset


def needs_wrapped_line_remap(text: str, line_offset: int) -> bool:
    if not text or line_offset <= 0:
        return False
    file_match = _PY_FILE_LINE.search(text)
    if file_match and int(file_match.group(2)) > line_offset:
        return True
    summary_match = _LINE_PREFIX.search(text)
    if summary_match and int(summary_match.group(1)) > line_offset:
        return True
    source_match = _SOURCE_PATH_LINE.search(text)
    if source_match and int(source_match.group(2)) > line_offset:
        return True
    return False


def remap_wrapped_source_lines(text: str, line_offset: int) -> str:
    """Map /tmp/home/source.py line numbers back to the student's editor."""
    if not text or line_offset <= 0 or not needs_wrapped_line_remap(text, line_offset):
        return text

    remapped = _PY_FILE_LINE.sub(
        lambda match: (
            f"{match.group(1)}{_map_wrapped_line_number(int(match.group(2)), line_offset)}"
        ),
        text,
    )
    remapped = _LINE_PREFIX.sub(
        lambda match: f"Line {_map_wrapped_line_number(int(match.group(1)), line_offset)}",
        remapped,
    )
    remapped = _SOURCE_PATH_LINE.sub(
        lambda match: (
            f"{match.group(1)}{_map_wrapped_line_number(int(match.group(2)), line_offset)}"
            f"{match.group(3)}"
        ),
        remapped,
    )
    return remapped


def is_lint_success_message(text: str) -> bool:
    return bool(_LINT_SUCCESS_LINE.match(str(text or "").strip()))


def _normalize_severity(severity: str) -> str:
    lowered = str(severity or "error").strip().lower()
    if lowered.startswith("fatal"):
        return "fatal"
    if lowered == "warning":
        return "warning"
    return "error"


def _clean_diagnostic_message(message: str) -> str:
    msg = str(message or "").strip()
    msg = re.sub(r"\s+\[(?:/tmp/home/)?[^\]]+\]\s*$", "", msg).strip()
    msg = re.sub(
        r"\s+\((?:error|warning|fatal)\)\s*$",
        "",
        msg,
        flags=re.IGNORECASE,
    ).strip()
    msg = _RUFF_NOISE_PREFIX.sub("", msg).strip()
    msg = re.sub(
        r"^(?:fatal error|error|warning)\s*:\s*",
        "",
        msg,
        flags=re.IGNORECASE,
    ).strip()
    return msg or str(message or "").strip()


def _format_standard_diagnostic(
    line: str | int,
    message: str,
    *,
    column: str | int | None = None,
    severity: str = "error",
) -> str:
    sev = _normalize_severity(severity)
    msg = _clean_diagnostic_message(message)
    row = str(line)
    if column is not None and str(column).strip():
        return f"Line {row}:{column}: {sev}: {msg}"
    return f"Line {row}: {sev}: {msg}"


def _dedupe_diagnostics_by_line(diagnostics: list[str]) -> list[str]:
    seen_lines: set[str] = set()
    deduped: list[str] = []
    for item in diagnostics:
        match = _STANDARD_LINE_DIAG.match(item.strip())
        key = match.group("line") if match else item.strip().lower()
        if key in seen_lines:
            continue
        seen_lines.add(key)
        deduped.append(item)
        if len(deduped) >= _MAX_COMPILER_DIAGNOSTICS:
            break
    return deduped


def _finalize_diagnostics(diagnostics: list[str]) -> list[str]:
    if not diagnostics:
        return []
    normalized: list[str] = []
    for item in diagnostics:
        match = _STANDARD_LINE_DIAG.match(item.strip())
        if match:
            normalized.append(
                _format_standard_diagnostic(
                    match.group("line"),
                    match.group("msg"),
                    column=match.group("col"),
                    severity=match.group("sev"),
                )
            )
            continue
        legacy = re.match(
            r"^Line\s+(?P<line>\d+)(?::(?P<col>\d+))?\s*:\s*(?P<msg>.+?)\s*"
            r"\((?P<sev>error|warning|fatal)\)\s*$",
            item.strip(),
            re.IGNORECASE,
        )
        if legacy:
            normalized.append(
                _format_standard_diagnostic(
                    legacy.group("line"),
                    legacy.group("msg"),
                    column=legacy.group("col"),
                    severity=legacy.group("sev"),
                )
            )
            continue
        normalized.append(item.strip())
    return _dedupe_diagnostics_by_line(normalized)


def _is_user_source_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    if any(
        marker in normalized
        for marker in ("/usr/", "/include/", "/bits/", "/lib/gcc/", "c++/")
    ):
        return False
    if normalized.startswith("/tmp/home/"):
        return True
    basename = normalized.rsplit("/", 1)[-1]
    return basename.startswith("source.") or basename in {
        "main.cpp",
        "main.c",
        "main.java",
        "main.cs",
        "program.cs",
        "source.cs",
        "solution.py",
    }


def _format_fpc_diagnostic(
    severity: str,
    message: str,
    *,
    line: str | None = None,
    column: str | None = None,
) -> str | None:
    msg = message.strip()
    if not msg:
        return None
    noise_candidate = f"{severity.capitalize()}: {msg}"
    if _FPC_NOISE_MESSAGE.match(noise_candidate) or _FPC_NOISE_MESSAGE.match(msg):
        return None
    if line and column:
        formatted = _format_standard_diagnostic(
            line, msg, column=column, severity=severity
        )
    elif line:
        formatted = _format_standard_diagnostic(line, msg, severity=severity)
    else:
        formatted = _format_standard_diagnostic(1, msg, severity=severity)
    if _FPC_NOISE_MESSAGE.match(msg):
        return None
    return formatted


def _parse_fpc_diagnostics(output: str) -> list[str]:
    seen: set[str] = set()
    diagnostics: list[str] = []

    for raw in output.splitlines():
        candidate = raw.rstrip().replace("\\", "/")
        if not candidate.strip() or _FPC_SKIP_LINE.match(candidate):
            continue

        bare = _FPC_BARE_DIAG.match(candidate)
        if bare:
            if _FPC_NOISE_MESSAGE.match(candidate):
                continue
            formatted = _format_fpc_diagnostic(
                bare.group("sev"),
                bare.group("msg"),
            )
            if formatted and formatted not in seen:
                seen.add(formatted)
                diagnostics.append(formatted)
            if len(diagnostics) >= _MAX_COMPILER_DIAGNOSTICS:
                break
            continue

        match = _FPC_DIAG.match(candidate)
        if not match:
            inline = re.search(
                r"\((?P<line>\d+),(?P<col>\d+)\)\s+"
                r"(?P<sev>Error|Fatal|Warning):\s+(?P<msg>.+)$",
                candidate,
                re.IGNORECASE,
            )
            if inline:
                formatted = _format_fpc_diagnostic(
                    inline.group("sev"),
                    inline.group("msg"),
                    line=inline.group("line"),
                    column=inline.group("col"),
                )
                if formatted and formatted not in seen:
                    seen.add(formatted)
                    diagnostics.append(formatted)
            continue

        path = match.group("path")
        if not _is_user_source_path(path):
            basename = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if not basename.startswith("source."):
                continue

        formatted = _format_fpc_diagnostic(
            match.group("sev"),
            match.group("msg"),
            line=match.group("line"),
            column=match.group("col"),
        )
        if formatted and formatted not in seen:
            seen.add(formatted)
            diagnostics.append(formatted)
        if len(diagnostics) >= _MAX_COMPILER_DIAGNOSTICS:
            break

    return diagnostics


def _parse_ruff_diagnostics(output: str) -> list[str]:
    seen: set[str] = set()
    diagnostics: list[str] = []

    for raw in output.splitlines():
        candidate = raw.rstrip().replace("\\", "/")
        if not candidate.strip() or is_lint_success_message(candidate):
            continue

        match = _RUFF_DIAG.match(candidate)
        if not match:
            continue

        path = match.group("path")
        if not _is_user_source_path(path):
            basename = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if not basename.startswith("source."):
                continue

        row = match.group("line")
        column = match.group("col")
        message = match.group("msg").strip()
        formatted = _format_standard_diagnostic(row, message, column=column)
        if formatted not in seen:
            seen.add(formatted)
            diagnostics.append(formatted)
        if len(diagnostics) >= _MAX_COMPILER_DIAGNOSTICS:
            break

    return diagnostics


def _parse_roslyn_diagnostics(output: str) -> list[str]:
    seen: set[str] = set()
    diagnostics: list[str] = []

    for raw in output.splitlines():
        candidate = raw.rstrip().replace("\\", "/")
        if not candidate.strip() or _SKIP_COMPILER_LINE.match(candidate):
            continue

        match = _ROSLYN_DIAG.match(candidate)
        if not match:
            continue

        path = match.group("path")
        if not _is_user_source_path(path):
            basename = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if basename not in {"program.cs", "main.cs", "source.cs", "source.csx"} and not basename.startswith(
                "source."
            ):
                continue

        row = match.group("line")
        column = match.group("col")
        severity = match.group("sev")
        message = match.group("msg").strip()
        formatted = _format_standard_diagnostic(
            row, message, column=column, severity=severity
        )
        if formatted not in seen:
            seen.add(formatted)
            diagnostics.append(formatted)
        if len(diagnostics) >= _MAX_COMPILER_DIAGNOSTICS:
            break

    return diagnostics


def _parse_javac_diagnostics(output: str) -> list[str]:
    seen: set[str] = set()
    diagnostics: list[str] = []

    for raw in output.splitlines():
        candidate = raw.rstrip().replace("\\", "/")
        if not candidate.strip() or _SKIP_COMPILER_LINE.match(candidate):
            continue

        match = _JAVAC_DIAG.match(candidate)
        if not match:
            continue

        path = match.group("path")
        if not _is_user_source_path(path):
            basename = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if basename not in {"main.java", "source.java"} and not basename.startswith(
                "source."
            ):
                continue

        row = match.group("line")
        severity = match.group("sev")
        message = match.group("msg").strip()
        formatted = _format_standard_diagnostic(row, message, severity=severity)
        if formatted not in seen:
            seen.add(formatted)
            diagnostics.append(formatted)
        if len(diagnostics) >= _MAX_COMPILER_DIAGNOSTICS:
            break

    return diagnostics


def _parse_gcc_clang_diagnostics(output: str) -> list[str]:
    seen: set[tuple[str, str, str]] = set()
    diagnostics: list[str] = []

    for raw in output.splitlines():
        candidate = raw.rstrip().replace("\\", "/")
        if not candidate.strip() or _SKIP_COMPILER_LINE.match(candidate):
            continue

        match = _GCC_DIAG.match(candidate)
        if not match:
            continue

        path = match.group("path")
        if not _is_user_source_path(path):
            continue

        row = match.group("line")
        column = match.group("col")
        severity = match.group("sev").lower()
        message = match.group("msg").strip()
        key = (row, column, message)
        if key in seen:
            continue
        seen.add(key)

        diagnostics.append(
            _format_standard_diagnostic(row, message, column=column, severity=severity)
        )
        if len(diagnostics) >= _MAX_COMPILER_DIAGNOSTICS:
            break

    return diagnostics


def parse_diagnostics(output: str, file_hint: str = "") -> list[str]:
    if not output:
        return []

    preformatted: list[str] = []
    for raw in output.splitlines():
        candidate = raw.strip()
        if not candidate or is_lint_success_message(candidate):
            continue
        if _LINE_PREFIX.match(candidate):
            preformatted.append(candidate)
    if preformatted:
        return _finalize_diagnostics(preformatted)

    fpc_diagnostics = _parse_fpc_diagnostics(output)
    if fpc_diagnostics:
        return _finalize_diagnostics(fpc_diagnostics)

    ruff_diagnostics = _parse_ruff_diagnostics(output)
    if ruff_diagnostics:
        return _finalize_diagnostics(ruff_diagnostics)

    javac_diagnostics = _parse_javac_diagnostics(output)
    if javac_diagnostics:
        return _finalize_diagnostics(javac_diagnostics)

    roslyn_diagnostics = _parse_roslyn_diagnostics(output)
    if roslyn_diagnostics:
        return _finalize_diagnostics(roslyn_diagnostics)

    gcc_diagnostics = _parse_gcc_clang_diagnostics(output)
    if gcc_diagnostics:
        return _finalize_diagnostics(gcc_diagnostics)

    normalized_path = file_hint.replace("\\", "/") if file_hint else ""
    diagnostics: list[str] = []

    gcc_pattern = (
        re.compile(
            rf"{re.escape(normalized_path)}:(\d+):(\d+):\s+"
            r"(fatal error|error|warning):\s+(.*)",
            re.IGNORECASE,
        )
        if normalized_path
        else None
    )
    line_col_pattern = re.compile(r"^(\d+):(\d+):\s+(.*)$")
    py_file_pattern = re.compile(
        r'File\s+"(?P<file>[^"]+)",\s+line\s+(?P<line>\d+)(?:\s+(?P<code>.*))?$',
        re.IGNORECASE,
    )
    py_error_pattern = re.compile(
        r"^(?P<kind>[A-Za-z_][\w.]*(Error|Exception)):\s*(?P<msg>.+)$"
    )

    py_line: str | None = None
    py_code_hint: str | None = None
    py_parts: list[str] = []

    for raw in output.splitlines():
        candidate = raw.rstrip().replace("\\", "/")
        if not candidate.strip() or _SKIP_COMPILER_LINE.match(candidate):
            continue

        if gcc_pattern:
            match = gcc_pattern.search(candidate)
            if match:
                row, column, severity, message = match.groups()
                diagnostics.append(
                    _format_standard_diagnostic(
                        row, message.strip(), column=column, severity=severity
                    )
                )
                continue

        match = line_col_pattern.match(candidate.strip())
        if match:
            row, column, message = match.groups()
            diagnostics.append(
                _format_standard_diagnostic(row, message.strip(), column=column)
            )
            continue

        file_match = py_file_pattern.search(candidate)
        if file_match:
            py_line = file_match.group("line")
            code_hint = (file_match.group("code") or "").strip()
            if code_hint:
                py_code_hint = code_hint
            continue

        err_match = py_error_pattern.match(candidate.strip())
        if err_match:
            py_parts.append(
                f"{err_match.group('kind')}: {err_match.group('msg').strip()}"
            )
            continue

        if candidate.startswith("SyntaxError:"):
            py_parts.append(candidate.replace("SyntaxError:", "").strip())

    if py_line and py_parts:
        diagnostics.append(
            _format_standard_diagnostic(py_line, " — ".join(py_parts), severity="error")
        )
    elif py_line:
        hint = py_code_hint or "ошибка выполнения"
        diagnostics.append(_format_standard_diagnostic(py_line, hint, severity="error"))

    if diagnostics:
        return _finalize_diagnostics(diagnostics)

    fallback = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
        and not is_lint_success_message(line)
        and not _SKIP_COMPILER_LINE.match(line.strip())
        and not _FPC_SKIP_LINE.match(line.strip())
    ]
    cleaned: list[str] = []
    for line in fallback:
        bare = _FPC_BARE_DIAG.match(line)
        if bare:
            formatted = _format_fpc_diagnostic(bare.group("sev"), bare.group("msg"))
            if formatted:
                cleaned.append(formatted)
            continue
        inline = re.search(
            r"\((?P<line>\d+),(?P<col>\d+)\)\s+"
            r"(?P<sev>Error|Fatal|Warning):\s+(?P<msg>.+)$",
            line,
            re.IGNORECASE,
        )
        if inline:
            formatted = _format_fpc_diagnostic(
                inline.group("sev"),
                inline.group("msg"),
                line=inline.group("line"),
            )
            if formatted:
                cleaned.append(formatted)
    return _finalize_diagnostics(cleaned)
