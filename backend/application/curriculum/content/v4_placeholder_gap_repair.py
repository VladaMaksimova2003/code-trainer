"""Repair docx placeholder gaps that contain labels instead of code tokens."""

from __future__ import annotations

import re
from typing import Any

_GAP_MARKER = re.compile(r"___(p\d+)___")
_CYRILLIC = re.compile(r"[\u0400-\u04ff]")
_LABEL_TOKENS = frozenset(
    {
        "условие",
        "condition",
        "цикл по данным",
        "условие if",
        "вывод результата",
        "объявление массива",
        "заголовок цикла",
        "флаг найденного элемента",
    }
)


def _normalize_lang(language: str) -> str:
    lang = str(language or "python").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def _answer_looks_invalid(answer: str) -> bool:
    text = str(answer or "").strip()
    if not text:
        return True
    if text in _LABEL_TOKENS:
        return True
    if _CYRILLIC.search(text):
        return True
    if len(text.split()) > 6:
        return False
    if any(ch in text for ch in "()[]{};:"):
        return False
    if text.isalpha() and text.lower() in {
        "found",
        "ok",
        "exists",
        "match",
        "maximum",
        "minimum",
        "result",
        "numbers",
        "value",
        "index",
        "integer",
        "boolean",
        "string",
    }:
        return False
    return False


def _extract_if_spans(reference: str) -> list[str]:
    spans: list[str] = []
    for match in re.finditer(
        r"if\s+(.+?)\s+then\s+(.+?)(?=;|\s+else\b|\s+end\b|\s+for\b|\s+while\b|$)",
        reference,
        flags=re.I,
    ):
        condition = match.group(1).strip()
        body = match.group(2).strip().rstrip(";")
        if condition and body:
            spans.append(f"{condition} then {body}")
    for match in re.finditer(r"if\s*\((.+?)\)\s*(.+?)(?=;|\s*\})?", reference, flags=re.I):
        condition = match.group(1).strip()
        body = match.group(2).strip().rstrip(";")
        if condition and body and body not in {"", "{"}:
            spans.append(f"{condition} {body}".strip())
    return spans


def _extract_for_headers(reference: str, lang: str) -> list[str]:
    headers: list[str] = []
    if lang == "pascal":
        for match in re.finditer(r"for\s+.+?\s+do", reference, flags=re.I):
            headers.append(match.group(0).strip())
    elif lang == "python":
        for match in re.finditer(r"for\s+.+?:", reference):
            headers.append(match.group(0).strip())
    else:
        for match in re.finditer(r"for\s*\(.+?\)", reference):
            headers.append(match.group(0).strip())
    return headers


def _infer_gap_answer(gap: dict[str, Any], reference: str, lang: str, used: set[str]) -> str | None:
    label = str(gap.get("label") or "").lower()
    ref = _collapse(reference)

    if "флаг" in label or "boolean" in label:
        for token in ("found", "seen", "ok", "exists", "flag"):
            if re.search(rf"\b{token}\b", ref, re.I):
                return token

    if "цикл" in label or "for" in label:
        headers = _extract_for_headers(reference, lang)
        for header in headers:
            if header not in used:
                return header

    if "услов" in label or "if" in label:
        for span in _extract_if_spans(reference):
            if span not in used:
                return span

    if "вывод" in label or "writeln" in label or "print" in label:
        for pattern in (
            r"writeln\s*\([^)]*\)",
            r"write\s*\([^)]*\)",
            r"print\s*\([^)]*\)",
            r"Console\.WriteLine\s*\([^)]*\)",
            r"System\.out\.print\w*\s*\([^)]*\)",
            r"std::cout\s*<<[^;]+",
        ):
            match = re.search(pattern, reference, flags=re.I)
            if match:
                return match.group(0).strip()

    if "массив" in label or "array" in label or "vector" in label:
        for pattern in (
            r"array\s*\[[^\]]+\]\s+of\s+\w+",
            r"std::vector<[^>]+>",
            r"int\s*\[\s*\]",
            r"int\[\]",
            r"list\s*\(",
        ):
            match = re.search(pattern, reference, flags=re.I)
            if match:
                return match.group(0).strip()

    for span in _extract_if_spans(reference):
        if span not in used:
            return span
    return None


def _rebuild_placeholder(reference: str, gaps: list[dict[str, Any]]) -> str:
    marked = str(reference or "")
    for gap in sorted(gaps, key=lambda item: str(item.get("id") or "")):
        answer = str(gap.get("answer") or gap.get("correct") or "").strip()
        gid = str(gap.get("id") or "")
        if not answer or not gid or answer not in marked:
            continue
        marked = marked.replace(answer, f"___{gid}___", 1)
    if _GAP_MARKER.search(marked):
        return _collapse(marked)
    return _collapse(reference)


def scrub_pedagogical_labels(code: str, gaps: list[dict[str, Any]], *, language: str = "pascal") -> str:
    """Replace docx pedagogical labels left inside reference/placeholder bodies."""
    out = str(code or "")
    if not any(label in out for label in _LABEL_TOKENS):
        return out

    lang = _normalize_lang(language)
    if_spans = _extract_if_spans(out)
    for label in _LABEL_TOKENS:
        if label not in out:
            continue
        replacement = ""
        if "цикл" in label or "услов" in label:
            replacement = if_spans[0] if if_spans else ""
        if not replacement:
            for gap in gaps:
                answer = str(gap.get("answer") or gap.get("correct") or "").strip()
                if answer and not _answer_looks_invalid(answer):
                    replacement = answer
                    break
        if replacement:
            out = out.replace(label, replacement)
    return out


def rebuild_placeholder_from_reference(reference: str, gaps: list[dict[str, Any]], *, language: str = "pascal") -> str:
    text = scrub_pedagogical_labels(reference, gaps, language=language)
    for gap in sorted(gaps, key=lambda item: str(item.get("id") or "")):
        answer = str(gap.get("answer") or gap.get("correct") or "").strip()
        gid = str(gap.get("id") or "")
        if answer and gid and answer in text:
            text = text.replace(answer, f"___{gid}___", 1)
    if _GAP_MARKER.search(text):
        return _collapse(text)
    return _collapse(reference)


def repair_placeholder_impl(
    impl: dict[str, Any],
    reference: str,
    *,
    language: str,
) -> dict[str, Any]:
    """Return a copy of *impl* with gap answers and placeholder rebuilt from reference."""
    out = dict(impl or {})
    gaps = [dict(g) for g in (out.get("gaps") or []) if isinstance(g, dict)]
    if not gaps:
        return out

    lang = _normalize_lang(language)
    from application.curriculum.content.v4_code_format import format_reference_code

    ref = format_reference_code(str(reference or ""), lang).strip()
    if not ref:
        return out

    used: set[str] = set()
    changed = False
    for gap in gaps:
        answer = str(gap.get("answer") or gap.get("correct") or "").strip()
        if not _answer_looks_invalid(answer):
            used.add(answer)
            continue
        inferred = _infer_gap_answer(gap, ref, lang, used)
        if not inferred:
            continue
        gap["answer"] = gap["correct"] = inferred
        gap["variants"] = [inferred, *[v for v in (gap.get("variants") or []) if v != inferred][:3]]
        used.add(inferred)
        changed = True

    placeholder = str(out.get("placeholder_code") or "")
    if changed or not _GAP_MARKER.search(placeholder):
        rebuilt = rebuild_placeholder_from_reference(ref, gaps, language=lang)
        if _GAP_MARKER.search(rebuilt):
            placeholder = rebuilt
            changed = True

    if changed:
        out["gaps"] = gaps
        out["placeholder_code"] = placeholder
    return out


def repair_task_placeholders(task: dict[str, Any]) -> None:
    """Mutate task implementations in place for placeholder assembly tasks."""
    fmt = str(task.get("format_ru") or "")
    if fmt != "сборка_фрагмента":
        return
    implementations = dict(task.get("implementations") or {})
    reference_codes = dict(task.get("reference_codes") or {})
    for lang in ("pascal", "python", "cpp", "csharp", "java"):
        impl = dict(implementations.get(lang) or {})
        ref = str(reference_codes.get(lang) or "")
        repaired = repair_placeholder_impl(impl, ref, language=lang)
        if repaired != impl:
            implementations[lang] = repaired
    task["implementations"] = implementations
