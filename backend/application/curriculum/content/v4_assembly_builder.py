"""Build block-reorder payloads for v4 course tasks from reference solutions."""

from __future__ import annotations

import re
from typing import Any

AssemblyPayload = tuple[str, str, list[str], list[int]]

_FREE_FORM_TEMPLATE = "___"

_LANGUAGE_DECOYS: dict[str, list[str]] = {
    "pascal": [":=", ">=", "then", "=", "do", "and"],
    "python": ["input", "int", "float", ">", ">=", "print", "readln"],
    "cpp": [">>", "<<", "=", "+=", ">", ">=", "then"],
    "csharp": ["Parse", "=", "+=", ">", ">=", "WriteLine", "ReadLine"],
    "java": ["nextInt", "=", "+=", "println", "print", "nextLine"],
}

_GAP_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "pascal": [
        (r":=", ":="),
        (r">=", ">="),
        (r"\bthen\b", "then"),
        (r"\bdo\b", "do"),
        (r"(?<![<>!=])=(?!=)", "="),
    ],
    "python": [
        (r"\bint\s*\(", "int"),
        (r"\bfloat\s*\(", "float"),
        (r"\binput\s*\(", "input"),
        (r"\bprint\s*\(", "print"),
        (r">=", ">="),
        (r"(?<![<>!=])=(?!=)", "="),
    ],
    "cpp": [
        (r">>", ">>"),
        (r"<<", "<<"),
        (r"\+=", "+="),
        (r">=", ">="),
        (r"(?<![<>!=])=(?!=)", "="),
    ],
    "csharp": [
        (r"\bParse\s*\(", "Parse"),
        (r"WriteLine", "WriteLine"),
        (r"ReadLine", "ReadLine"),
        (r">=", ">="),
        (r"(?<![<>!=])=(?!=)", "="),
    ],
    "java": [
        (r"nextInt\s*\(", "nextInt"),
        (r"nextLine\s*\(", "nextLine"),
        (r"println", "println"),
        (r">=", ">="),
        (r"(?<![<>!=])=(?!=)", "="),
    ],
}

_MAX_GAPS = 5

from application.curriculum.content.ch1_fragment_assembly import CH1_FRAGMENT_ASSEMBLY

_CURATED_FRAGMENT_ASSEMBLY: dict[str, dict[str, dict[str, Any]]] = dict(CH1_FRAGMENT_ASSEMBLY)


def _resolve_pattern_id(
    pattern_id: str | None = None,
    slot_id: str | None = None,
) -> str | None:
    pid = str(pattern_id or "").strip()
    if pid:
        return pid
    sid = str(slot_id or "").strip()
    if not sid:
        return None
    from application.curriculum.content.algo_syntax_task_extra import resolve_slot_pattern_key

    return resolve_slot_pattern_key(sid) or None


def _curated_fragment_payload(
    pattern_id: str,
    language: str,
    reference_code: str,
) -> AssemblyPayload | None:
    lang = _normalize_lang(language)
    spec = _CURATED_FRAGMENT_ASSEMBLY.get(pattern_id, {}).get(lang)
    if not spec:
        return None
    from application.curriculum.content.v4_code_format import format_reference_code

    ref = format_reference_code(reference_code, lang).strip()
    if not ref:
        return None
    return (
        ref,
        str(spec["template"]),
        list(spec["blocks"]),
        list(spec["correct_order"]),
    )


def _normalize_lang(language: str) -> str:
    lang = str(language or "python").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _reference_lines(reference_code: str, language: str = "python") -> list[str]:
    text = str(reference_code or "").strip()
    if not text:
        return ["print('Hello')"]
    if "\n" in text:
        lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
        return lines or [text]
    lang = _normalize_lang(language)
    from application.curriculum.content.v4_code_format import format_reference_code

    formatted = format_reference_code(text, lang)
    if "\n" in formatted:
        lines = [ln.rstrip() for ln in formatted.splitlines() if ln.strip()]
        return lines or [formatted]
    # Minified one-liner: split before common statement starters.
    parts = re.split(
        r"(?<=[;\}])(?=(?:print|writeln|readln|std::|Console\.|System\.|if\b|for\b|while\b|def\b|class\b|return\b|#include|using\b|var\b|int\b|double\b|float\b|name\b|type\b|begin\b|new\b))",
        text,
        flags=re.IGNORECASE,
    )
    lines = [part.strip() for part in parts if part.strip()]
    return lines or [text]


def _merge_wrapped_assembly_blocks(blocks: list[str]) -> list[str]:
    """Join only obvious docx line-wrap pairs (``for x`` + ``in xs:``)."""
    merged: list[str] = []
    i = 0
    while i < len(blocks):
        block = blocks[i]
        if i + 1 < len(blocks):
            nxt = blocks[i + 1]
            if re.match(r"^for\b", block, re.I) and re.match(r"^in\b", nxt, re.I):
                merged.append(f"{block} {nxt}")
                i += 2
                continue
            if re.match(r"^while\b", block, re.I) and not block.rstrip().endswith(":"):
                if ":" in nxt:
                    merged.append(f"{block} {nxt}")
                    i += 2
                    continue
        merged.append(block)
        i += 1
    return merged


def canonical_assembly_blocks(blocks: list[str], language: str) -> list[str]:
    """Normalize docx assembly blocks without gluing separate numbered rows."""
    clean = [str(item).replace("\n", " ").strip() for item in blocks if str(item).strip()]
    if not clean:
        return []

    if len(clean) > 1:
        return _merge_wrapped_assembly_blocks(clean)

    from application.curriculum.content.v4_code_format import format_reference_code

    raw = clean[0]
    formatted = format_reference_code(raw, _normalize_lang(language))
    lines = _reference_lines(formatted, _normalize_lang(language))
    return lines if lines else clean


def line_assembly_payload(language: str, reference_code: str) -> AssemblyPayload:
    """Full-line block reorder (блоки с плейсхолдерами / сборка_программы)."""
    from application.curriculum.content.v4_code_format import format_reference_code

    lang = _normalize_lang(language)
    formatted = format_reference_code(reference_code, lang)
    lines = _reference_lines(formatted, lang)
    original = "\n".join(lines)
    blocks = list(lines)
    order = list(range(len(blocks)))
    return original, _FREE_FORM_TEMPLATE, blocks, order


def _find_gap_replacements(language: str, reference_code: str) -> list[tuple[int, int, str]]:
    lang = _normalize_lang(language)
    patterns = _GAP_PATTERNS.get(lang, _GAP_PATTERNS["python"])
    text = str(reference_code or "")
    found: list[tuple[int, int, str]] = []
    used_spans: list[tuple[int, int]] = []

    for pattern, token in patterns:
        if len(found) >= _MAX_GAPS:
            break
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start, end = match.span()
            if any(not (end <= s or start >= e) for s, e in used_spans):
                continue
            found.append((start, end, token))
            used_spans.append((start, end))
            break

    found.sort(key=lambda item: item[0])
    return found


def gap_assembly_payload(language: str, reference_code: str) -> AssemblyPayload:
    """Inline syntax gaps with {0} slots (сборка_фрагмента / placeholder capstones)."""
    from application.curriculum.content.v4_code_format import format_reference_code

    lang = _normalize_lang(language)
    ref = format_reference_code(reference_code, lang).strip()
    if not ref:
        ref = "print('Hello')"

    replacements = _find_gap_replacements(lang, ref)
    if not replacements:
        return line_assembly_payload(lang, ref)

    template = ref
    correct_tokens: list[str] = []
    for slot_idx, (start, end, token) in enumerate(reversed(replacements)):
        correct_tokens.insert(0, token)
        template = template[:start] + "{" + str(len(replacements) - 1 - slot_idx) + "}" + template[end:]

    from application.curriculum.content.placeholder_distractors import contextual_decoys_for_token

    blocks: list[str] = []
    correct_order: list[int] = []
    decoys_seen: set[str] = set()
    for token in correct_tokens:
        correct_order.append(len(blocks))
        blocks.append(token)
        decoys_seen.add(token)
        for decoy in contextual_decoys_for_token(token, ref, lang):
            if decoy not in decoys_seen:
                blocks.append(decoy)
                decoys_seen.add(decoy)
    for decoy in _LANGUAGE_DECOYS.get(lang, _LANGUAGE_DECOYS["python"]):
        if decoy not in decoys_seen:
            blocks.append(decoy)
            decoys_seen.add(decoy)

    return ref, template, blocks, correct_order


def assembly_payload_for_format(
    task_format: str,
    language: str,
    reference_code: str,
    *,
    pattern_id: str | None = None,
    slot_id: str | None = None,
) -> AssemblyPayload:
    fmt = str(task_format or "")
    resolved_pattern = _resolve_pattern_id(pattern_id, slot_id)
    if fmt == "сборка_фрагмента" and resolved_pattern:
        curated = _curated_fragment_payload(resolved_pattern, language, reference_code)
        if curated is not None:
            return curated
    if fmt == "сборка_фрагмента":
        return gap_assembly_payload(language, reference_code)
    return line_assembly_payload(language, reference_code)


def assembly_variant(
    language: str,
    reference_code: str,
    *,
    task_format: str,
    pattern_id: str | None = None,
    slot_id: str | None = None,
) -> dict[str, Any]:
    original, template, blocks, order = assembly_payload_for_format(
        task_format,
        language,
        reference_code,
        pattern_id=pattern_id,
        slot_id=slot_id,
    )
    return {
        "original_code": original,
        "template": template,
        "blocks": blocks,
        "correct_order": order,
    }


def build_multilingual_assembly_variants(
    slot_id: str,
    *,
    task_format: str,
    languages: tuple[str, ...] = ("pascal", "python", "cpp", "csharp", "java"),
) -> dict[str, dict[str, Any]]:
    from application.curriculum.content.v4_reference_code import get_reference_code

    variants: dict[str, dict[str, Any]] = {}
    for lang in languages:
        ref = get_reference_code(slot_id, lang)
        if not ref:
            continue
        variants[lang] = assembly_variant(
            lang,
            ref,
            task_format=task_format,
            slot_id=slot_id,
        )
    return variants


def primary_assembly_extra(
    slot_id: str,
    language: str,
    *,
    task_format: str,
    reference_code: str | None = None,
) -> dict[str, Any]:
    from application.curriculum.content.v4_reference_code import get_reference_code

    lang = _normalize_lang(language)
    ref = reference_code or get_reference_code(slot_id, lang) or ""
    original, template, blocks, order = assembly_payload_for_format(
        task_format,
        lang,
        ref,
        slot_id=slot_id,
    )
    return {
        "language": lang,
        "original_code": original,
        "template": template,
        "blocks": blocks,
        "correct_order": order,
    }
