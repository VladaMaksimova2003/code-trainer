"""Task payloads for the 128-task algorithm-syntax course (from docx)."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_SLOT_RE = re.compile(r"^(?:pas|py|cpp|cs|java)_(\d{3})$")
_GAP_RE = re.compile(r"___(p\d+)___")

_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    from algo_v128_catalog import ALGO_SYNTAX_META, V128_CORE_TASK_COUNT
    from algo_v192_plan import V192_TARGET_TASK_COUNT
except ImportError:
    ALGO_SYNTAX_META: dict[str, dict[str, Any]] = {}
    V128_CORE_TASK_COUNT = 0
    V192_TARGET_TASK_COUNT = 128

_LANG_ALIASES = {"cs": "csharp", "c#": "csharp"}


def _normalize_lang(language: str) -> str:
    lang = str(language or "python").strip().lower()
    return _LANG_ALIASES.get(lang, lang)


def slot_to_pattern(slot_id: str | None) -> str | None:
    if not slot_id:
        return None
    match = _SLOT_RE.match(str(slot_id).strip())
    if not match:
        return None
    num = int(match.group(1))
    from application.curriculum.course_scope import active_target_task_count

    if num < 1 or num > active_target_task_count():
        return None
    return f"task_{num:03d}"


_V128_SLOT_PATTERN_MAP: dict[str, str] | None = None


def _build_v128_slot_pattern_map() -> dict[str, str]:
    """Map pas_003 → task_005 etc. (course slot number ≠ ALGO pattern id)."""
    try:
        from algo_v128_catalog import _TASK_INDEX
    except ImportError:
        return {}
    prefixes = ("pas", "py", "cpp", "cs", "java")
    out: dict[str, str] = {}
    for item in _TASK_INDEX:
        n = int(item["task_num"])
        pattern = str(item["pattern_id"]).strip()
        if not re.match(r"^task_\d+$", pattern):
            continue
        for prefix in prefixes:
            out[f"{prefix}_{n:03d}"] = pattern
    return out


def v128_pattern_for_slot(slot_id: str | None) -> str | None:
    global _V128_SLOT_PATTERN_MAP
    if _V128_SLOT_PATTERN_MAP is None:
        _V128_SLOT_PATTERN_MAP = _build_v128_slot_pattern_map()
    return _V128_SLOT_PATTERN_MAP.get(str(slot_id or "").strip())


def resolve_slot_pattern_key(
    slot_id: str | None,
    *,
    slot_pattern_id: str | None = None,
) -> str | None:
    """Map a curriculum slot to ALGO_SYNTAX_META / reference code key."""
    mapped = v128_pattern_for_slot(slot_id)
    if mapped:
        return mapped
    pat = str(slot_pattern_id or "").strip()
    if re.match(r"^task_\d+$", pat):
        return pat
    return slot_to_pattern(slot_id)


def is_algo_syntax_slot(slot_id: str | None) -> bool:
    return slot_to_pattern(slot_id) is not None


def algo_meta(slot_id: str, *, slot_pattern_id: str | None = None) -> dict[str, Any] | None:
    pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
    if not pattern:
        return None
    raw = ALGO_SYNTAX_META.get(pattern)
    return dict(raw) if raw else None


def algo_implementation(slot_id: str, language: str, *, slot_pattern_id: str | None = None) -> dict[str, Any]:
    meta = algo_meta(slot_id, slot_pattern_id=slot_pattern_id) or {}
    impls = meta.get("implementations") or {}
    return dict(impls.get(_normalize_lang(language)) or {})


def algo_reference_code(slot_id: str, language: str, *, slot_pattern_id: str | None = None) -> str:
    meta = algo_meta(slot_id, slot_pattern_id=slot_pattern_id) or {}
    codes = meta.get("reference_codes") or {}
    raw = str(codes.get(_normalize_lang(language)) or "")
    pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
    if not raw.strip():
        from application.curriculum.content.v4_reference_code import get_reference_code

        return get_reference_code(slot_id, language, pattern_key=pattern)
    if pattern:
        from application.curriculum.content.v4_reference_overrides import resolve_reference_raw

        raw = resolve_reference_raw(pattern, language, raw)
    from application.curriculum.content.v4_code_format import normalize_authoring_code

    return normalize_authoring_code(raw)


def algo_test_cases(slot_id: str, *, slot_pattern_id: str | None = None) -> list[dict[str, str]]:
    meta = algo_meta(slot_id, slot_pattern_id=slot_pattern_id) or {}
    raw = meta.get("test_cases") or []
    return [dict(item) for item in raw if isinstance(item, dict)]


def algo_expected_concepts(
    slot_id: str,
    language: str,
    *,
    slot_pattern_id: str | None = None,
) -> list[str]:
    from application.curriculum.content.catalog_feature_concepts import (
        features_for_pattern,
        technical_ids_from_catalog_features,
    )

    meta = algo_meta(slot_id, slot_pattern_id=slot_pattern_id) or {}
    pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
    lang = _normalize_lang(language)

    features = features_for_pattern(pattern) or str(meta.get("features") or "").strip()
    if features:
        concepts = technical_ids_from_catalog_features(features)
    else:
        by_lang = meta.get("expected_concepts") or {}
        raw = by_lang.get(lang) or by_lang.get("pascal") or []
        concepts = [str(item).strip() for item in raw if str(item).strip()]

    if features:
        return concepts

    reference = algo_reference_code(slot_id, lang, slot_pattern_id=slot_pattern_id)
    if not reference:
        return concepts
    from application.curriculum.validation.expected_concept_checker import (
        prune_expected_concepts_for_code,
    )

    return prune_expected_concepts_for_code(concepts, reference, lang)


def algo_debug_starter(slot_id: str, language: str) -> str:
    from application.curriculum.content.v4_code_format import normalize_authoring_code

    impl = algo_implementation(slot_id, language)
    buggy = str(impl.get("buggy_code") or "")
    if buggy.strip():
        return normalize_authoring_code(buggy)
    return algo_reference_code(slot_id, language)


def algo_fixed_code(slot_id: str, language: str) -> str:
    """Correct reference for «Я знаю» on debug / исправление tasks."""
    from application.curriculum.content.v4_code_format import normalize_authoring_code

    impl = algo_implementation(slot_id, language)
    fixed = str(impl.get("fixed_code") or "")
    if fixed.strip():
        return normalize_authoring_code(fixed)
    return algo_reference_code(slot_id, language)


def _single_fix_assembly(fixed: str, buggy: str) -> tuple[str, str, list[str], list[int]] | None:
    """Build slot-template assembly when buggy and fixed differ by one token."""
    from difflib import SequenceMatcher

    matcher = SequenceMatcher(None, buggy, fixed)
    replace_ops = [op for op in matcher.get_opcodes() if op[0] == "replace"]
    other_ops = [op for op in matcher.get_opcodes() if op[0] not in {"equal", "replace"}]
    if len(replace_ops) != 1 or other_ops:
        return None

    _, i1, i2, j1, j2 = replace_ops[0]
    wrong = str(buggy[i1:i2]).strip()
    correct = str(fixed[j1:j2]).strip()
    if not wrong or not correct or wrong == correct:
        return None
    if len(wrong) > 24 or len(correct) > 24:
        return None

    template = fixed[:j1] + "{0}" + fixed[j2:]
    blocks = [correct, wrong]
    for token in (wrong, correct):
        if token not in blocks:
            blocks.append(token)
    correct_order = [0]
    display = template.replace("{0}", " ___ ")
    return display.strip() or fixed, template, blocks, correct_order


def algo_debug_assembly_payload(
    slot_id: str,
    language: str,
    *,
    slot_pattern_id: str | None = None,
) -> dict[str, Any] | None:
    """Turn simple debug fixes into placeholder block assembly."""
    impl = algo_implementation(slot_id, language, slot_pattern_id=slot_pattern_id)
    buggy = str(impl.get("buggy_code") or "").strip()
    fixed = str(impl.get("fixed_code") or "").strip()
    if not buggy or not fixed or buggy == fixed:
        return None

    from application.curriculum.content.v4_code_format import format_reference_code

    lang = _normalize_lang(language)
    buggy_fmt = format_reference_code(buggy, lang)
    fixed_fmt = format_reference_code(fixed, lang)
    if not buggy_fmt or not fixed_fmt or buggy_fmt == fixed_fmt:
        return None

    payload = _single_fix_assembly(fixed_fmt, buggy_fmt)
    if payload is None:
        return None

    original, template, blocks, correct_order = payload
    return {
        "original_code": original,
        "template": template,
        "blocks": blocks,
        "correct_order": correct_order,
        "language": lang,
        "reference_solution": fixed_fmt,
    }


def algo_multilingual_debug_assembly(
    slot_id: str,
    *,
    languages: tuple[str, ...] = ("pascal", "python", "cpp", "csharp", "java"),
    slot_pattern_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    variants: dict[str, dict[str, Any]] = {}
    for lang in languages:
        payload = algo_debug_assembly_payload(
            slot_id, lang, slot_pattern_id=slot_pattern_id
        )
        if not payload:
            continue
        variants[lang] = {
            "original_code": payload["original_code"],
            "template": payload["template"],
            "blocks": payload["blocks"],
            "correct_order": payload["correct_order"],
        }
    return variants


_TRANSLATION_STARTERS: dict[str, str] = {
    "pascal": (
        "program Demo;\n"
        "var\n"
        "  n: integer;\n"
        "begin\n"
        "  { TODO: переведите программу }\n"
        "end."
    ),
    "python": "# TODO: переведите программу\npass\n",
    "cpp": (
        "#include <iostream>\n"
        "int main() {\n"
        "    // TODO: переведите программу\n"
        "    return 0;\n"
        "}\n"
    ),
    "csharp": (
        "using System;\n"
        "class Program {\n"
        "    static void Main() {\n"
        "        // TODO: переведите программу\n"
        "    }\n"
        "}\n"
    ),
    "java": (
        "class Main {\n"
        "    public static void main(String[] args) {\n"
        "        // TODO: переведите программу\n"
        "    }\n"
        "}\n"
    ),
}


def algo_translation_starter(slot_id: str, language: str) -> str:
    """Incomplete starter for «Учу» on translation tasks (correct code lives in «Я знаю»)."""
    _ = slot_id
    lang = _normalize_lang(language)
    return _TRANSLATION_STARTERS.get(lang, _TRANSLATION_STARTERS["python"]).strip()


def algo_debug_solution(slot_id: str, language: str) -> str:
    impl = algo_implementation(slot_id, language)
    fixed = str(impl.get("fixed_code") or "").strip()
    if fixed:
        return fixed
    return algo_reference_code(slot_id, language)


def _full_line_assembly(blocks: list[str]) -> tuple[str, str, list[str], list[int]]:
    clean = [str(item).strip() for item in blocks if str(item).strip()]
    if not clean:
        clean = ["print('ok')"]
    original = "\n".join(clean)
    return original, "___", clean, list(range(len(clean)))


def _format_assembly_placeholder(code: str, language: str) -> str:
    """Pretty-print minified placeholder sources while keeping ``___gap___`` markers."""
    from application.curriculum.content.v4_assembly_builder import _normalize_lang
    from application.curriculum.content.v4_code_format import format_reference_code

    raw = str(code or "").strip()
    if not raw:
        return raw

    lang = _normalize_lang(language)
    protected: list[str] = []

    def _shield(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"__CT_GAP_{len(protected) - 1}__"

    body = _GAP_RE.sub(_shield, raw)
    formatted = format_reference_code(body, lang).strip()
    if not formatted:
        formatted = body
    for index, marker in enumerate(protected):
        formatted = formatted.replace(f"__CT_GAP_{index}__", marker)
    return formatted


def _placeholder_assembly(
    placeholder_code: str,
    gaps: list[dict[str, Any]],
    *,
    language: str = "python",
    reference_code: str = "",
) -> tuple[str, str, list[str], list[int]]:
    code = _format_assembly_placeholder(str(placeholder_code or "").strip(), language)
    if not code:
        return _full_line_assembly([])

    first_gap = _GAP_RE.search(code)
    if first_gap and first_gap.start() > 0:
        prefix = code[: first_gap.start()].rstrip()
        suffix = code[first_gap.start() :]
        if prefix and "\n" not in prefix:
            from application.curriculum.content.v4_assembly_builder import _reference_lines
            from application.curriculum.content.v4_code_format import format_reference_code

            lang = _normalize_lang(language)
            split_parts = re.split(r"(?<=\))(?=[a-z_]+\s*=)", prefix)
            if len(split_parts) > 1:
                code = "\n".join(part.strip() for part in split_parts if part.strip()) + suffix
            else:
                prefix_lines = _reference_lines(format_reference_code(prefix, lang), lang)
                if len(prefix_lines) > 1:
                    code = "\n".join(prefix_lines) + suffix

    gap_ids = _GAP_RE.findall(code)
    id_to_gap = {str(g.get("id") or ""): g for g in gaps if isinstance(g, dict)}

    template = code
    blocks: list[str] = []
    correct_order: list[int] = []

    from application.curriculum.content.placeholder_distractors import enrich_gap_variants

    gap_list = [g for g in gaps if isinstance(g, dict)]
    for idx, gap_id in enumerate(gap_ids):
        gap = id_to_gap.get(gap_id, {})
        answer = str(gap.get("answer") or gap.get("correct") or "").strip()
        variants = enrich_gap_variants(
            gap,
            all_gaps=gap_list,
            placeholder_code=code,
            reference_code=reference_code,
            language=_normalize_lang(language),
        )
        if not variants:
            raw = [str(v).strip() for v in (gap.get("variants") or []) if str(v).strip()]
            if answer and answer not in raw:
                variants = [answer, *raw]
            elif answer:
                variants = [answer, *[v for v in raw if v != answer]]
            elif raw:
                answer = raw[0]
                variants = raw
            else:
                answer = gap_id
                variants = [answer]
        elif not answer:
            answer = variants[0]

        # Each slot gets its own block indices so the same word can fill multiple gaps.
        slot_variants: list[str] = []
        for variant in variants:
            if variant not in slot_variants:
                slot_variants.append(variant)

        answer_idx = len(blocks)
        blocks.extend(slot_variants)
        correct_order.append(answer_idx)
        template = template.replace(f"___{gap_id}___", "{" + str(idx) + "}", 1)

    display = re.sub(r"(\{\d+\})", r" ___ ", template)
    return display.strip() or code, template, blocks, correct_order


def algo_assembly_payload(
    slot_id: str,
    language: str,
    *,
    task_format: str,
    slot_pattern_id: str | None = None,
) -> tuple[str, str, list[str], list[int]]:
    fmt = str(task_format or "")
    lang = _normalize_lang(language)
    pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)

    if fmt == "сборка_фрагмента" and pattern:
        from application.curriculum.content.ch1_fragment_assembly import CH1_FRAGMENT_ASSEMBLY
        from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format

        if pattern in CH1_FRAGMENT_ASSEMBLY:
            ref = algo_reference_code(slot_id, language, slot_pattern_id=slot_pattern_id)
            return assembly_payload_for_format(
                fmt,
                lang,
                ref,
                pattern_id=pattern,
                slot_id=slot_id,
            )

    impl = algo_implementation(slot_id, language, slot_pattern_id=slot_pattern_id)

    if fmt == "сборка_фрагмента":
        placeholder = str(impl.get("placeholder_code") or "").strip()
        gaps = list(impl.get("gaps") or [])
        if placeholder and ("___" in placeholder or gaps):
            from application.curriculum.content.v4_placeholder_gap_repair import repair_placeholder_impl

            ref = algo_reference_code(slot_id, language, slot_pattern_id=slot_pattern_id)
            impl = repair_placeholder_impl(impl, ref, language=_normalize_lang(language))
            placeholder = str(impl.get("placeholder_code") or placeholder)
            gaps = list(impl.get("gaps") or gaps)
            ref = algo_reference_code(slot_id, language, slot_pattern_id=slot_pattern_id)
            payload = _placeholder_assembly(
                placeholder,
                gaps,
                language=_normalize_lang(language),
                reference_code=ref,
            )
            if payload[2]:
                return payload
            if ref.strip():
                from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format

                return assembly_payload_for_format(fmt, _normalize_lang(language), ref)
            return payload

    blocks = list(impl.get("assembly_blocks") or [])
    if fmt == "сборка_программы":
        from application.curriculum.content.v4_assembly_builder import (
            canonical_assembly_blocks,
            line_assembly_payload,
        )
        from application.curriculum.content.v4_code_format import format_reference_code

        lang = _normalize_lang(language)
        if blocks:
            normalized = canonical_assembly_blocks(blocks, lang)
            if normalized:
                return _full_line_assembly(normalized)
        ref = algo_reference_code(slot_id, language, slot_pattern_id=slot_pattern_id)
        formatted = format_reference_code(str(ref).strip(), lang)
        if formatted.strip():
            return line_assembly_payload(lang, formatted)

    if blocks:
        return _full_line_assembly(blocks)

    from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format

    ref = algo_reference_code(slot_id, language, slot_pattern_id=slot_pattern_id)
    return assembly_payload_for_format(fmt or "сборка_программы", _normalize_lang(language), ref)


def algo_multilingual_assembly(
    slot_id: str,
    *,
    task_format: str,
    languages: tuple[str, ...] = ("pascal", "python", "cpp", "csharp", "java"),
    slot_pattern_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    variants: dict[str, dict[str, Any]] = {}
    for lang in languages:
        original, template, blocks, order = algo_assembly_payload(
            slot_id,
            lang,
            task_format=task_format,
            slot_pattern_id=slot_pattern_id,
        )
        variants[lang] = {
            "original_code": original,
            "template": template,
            "blocks": blocks,
            "correct_order": order,
        }
    return variants


def algo_pitfall_meta_by_pattern(pattern: str | None) -> dict[str, Any]:
    """Resolve pitfall_id + transfer texts for task_NNN pattern key."""
    key = str(pattern or "").strip()
    if not key:
        return {}
    from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta

    raw = ALGO_SYNTAX_META.get(key) or {}
    meta = resolve_v128_transfer_meta(key)
    reference_warning = str(raw.get("reference_warning_ru") or "").strip()
    if reference_warning:
        meta["reference_warning_ru"] = reference_warning
    elif meta.get("contrast_note_ru") and not meta.get("reference_warning_ru"):
        meta["reference_warning_ru"] = meta["contrast_note_ru"]
    pedagogy = str(raw.get("pedagogy_note_ru") or "").strip()
    if pedagogy:
        meta["pedagogy_note_ru"] = pedagogy
    return {k: v for k, v in meta.items() if v}


def algo_pitfall_meta(
    slot_id: str,
    *,
    slot_pattern_id: str | None = None,
) -> dict[str, Any]:
    pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
    if not pattern:
        return {}
    return algo_pitfall_meta_by_pattern(pattern)
