"""Whether MPLT proactive warnings apply to what the student can actually edit."""

from __future__ import annotations

import re
from typing import Any

_ASSEMBLY_ACTIONS = frozenset({"assemble"})
_ASSEMBLY_TYPES = frozenset(
    {"block_reorder", "code_assembly", "task_build_from_blocks"},
)
_GAP_TEMPLATE_FORMAT = "сборка_фрагмента"


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _is_assembly_task(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any] | None,
) -> bool:
    showcase = showcase_fields or {}
    curriculum = payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {}
    action = str(
        showcase.get("primary_action")
        or payload.get("primary_action")
        or curriculum.get("action")
        or curriculum.get("primary_action")
        or "",
    ).strip().lower()
    task_type = str(payload.get("type") or payload.get("task_type") or "").strip().lower()
    return action in _ASSEMBLY_ACTIONS or task_type in _ASSEMBLY_TYPES


def _task_format(payload: dict[str, Any], showcase_fields: dict[str, Any] | None) -> str:
    showcase = showcase_fields or {}
    curriculum = payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {}
    return str(
        showcase.get("task_format")
        or curriculum.get("task_format")
        or payload.get("task_format")
        or "",
    ).strip()


def _assembly_template_for_language(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any] | None,
    target_language: str,
) -> str:
    lang = _normalize_lang(target_language)
    curriculum = payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {}
    showcase = showcase_fields or {}
    code_examples = payload.get("code_examples") if isinstance(payload.get("code_examples"), dict) else {}

    variants = payload.get("language_variants")
    if isinstance(variants, dict):
        entry = variants.get(lang)
        if isinstance(entry, dict) and entry.get("template"):
            return str(entry["template"])

    primary_lang = _normalize_lang(
        str(payload.get("language") or payload.get("target_language") or curriculum.get("language") or ""),
    )
    if lang == primary_lang:
        for source in (payload, showcase, curriculum, code_examples):
            if isinstance(source, dict) and source.get("template"):
                return str(source["template"])

    return ""


def _integer_division_fixed_in_gap_template(template: str, target_language: str) -> bool:
    """True when the output expression is literal (no {gap}) and already uses correct idiom."""
    lang = _normalize_lang(target_language)
    text = str(template or "")

    if lang == "pascal":
        for match in re.finditer(r"writeln\s*\(([^)]*)\)", text, flags=re.IGNORECASE):
            body = match.group(1)
            if "{" in body:
                continue
            if re.search(r"\bdiv\b", body, flags=re.IGNORECASE):
                return True
            if "/" in body:
                return True
        return False

    if lang == "python":
        for match in re.finditer(r"print\s*\(([^)]*)\)", text, flags=re.IGNORECASE):
            body = match.group(1)
            if "{" in body:
                continue
            if "//" in body or "/" in body:
                return True
        return False

    output_patterns = (
        r"std::cout\s*<<\s*([^;]+)",
        r"Console\.WriteLine\s*\(([^)]*)\)",
        r"System\.out\.print(?:ln)?\s*\(([^)]*)\)",
    )
    for pattern in output_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            body = match.group(1)
            if "{" in body:
                continue
            if "/" in body:
                return True
    return False


def proactive_pitfall_applies_to_student_workspace(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any] | None,
    *,
    pitfall_id: str | None,
    target_language: str,
) -> bool:
    """False when an assembly gap template fixes the pitfall lexeme (student cannot trigger FCC)."""
    pid = str(pitfall_id or "").strip()
    if not pid:
        return True
    if not _is_assembly_task(payload, showcase_fields):
        return True

    template = _assembly_template_for_language(payload, showcase_fields, target_language)
    if not template:
        return True

    task_format = _task_format(payload, showcase_fields)
    is_gap_template = task_format == _GAP_TEMPLATE_FORMAT or "{" in template
    if not is_gap_template:
        return True

    if pid == "integer_division":
        return not _integer_division_fixed_in_gap_template(template, target_language)

    return True


def strip_proactive_from_transfer(transfer: dict[str, Any]) -> dict[str, Any]:
    """Remove banner fields while keeping pitfall_id for reactive checks on submit."""
    result = dict(transfer)
    result["proactive"] = {"zone": None, "text": None, "concept_ids": []}
    result["proactive_items"] = []
    for key in ("reference_warning_ru", "hint_ru", "contrast_note_ru"):
        result.pop(key, None)
    return result


def filter_proactive_items_for_workspace(
    transfer: dict[str, Any],
    payload: dict[str, Any],
    showcase_fields: dict[str, Any] | None,
    *,
    target_language: str,
) -> dict[str, Any]:
    """Drop proactive texts for pitfalls fixed in assembly gap templates."""
    from application.curriculum.display.proactive_scope import (
        proactive_pitfall_applies_to_student_workspace,
        strip_proactive_from_transfer,
    )

    items = list(transfer.get("proactive_items") or [])
    if not items:
        pid = str(transfer.get("pitfall_id") or "").strip()
        if pid and not proactive_pitfall_applies_to_student_workspace(
            payload,
            showcase_fields,
            pitfall_id=pid,
            target_language=target_language,
        ):
            return strip_proactive_from_transfer(transfer)
        return transfer

    kept: list[dict[str, Any]] = []
    for item in items:
        pid = str(item.get("pitfall_id") or "").strip()
        if not pid:
            continue
        if proactive_pitfall_applies_to_student_workspace(
            payload,
            showcase_fields,
            pitfall_id=pid,
            target_language=target_language,
        ):
            kept.append(dict(item))

    result = dict(transfer)
    result["proactive_items"] = kept
    result["pitfall_ids"] = [str(item.get("pitfall_id") or "") for item in kept if item.get("pitfall_id")]
    if kept:
        banner = "\n\n".join(str(item.get("text") or "").strip() for item in kept if item.get("text"))
        result["pitfall_id"] = kept[0].get("pitfall_id")
        result["transfer_type"] = kept[0].get("transfer_type")
        result["proactive"] = {
            "zone": kept[0].get("zone"),
            "text": banner or kept[0].get("text"),
            "concept_ids": [
                cid
                for item in kept
                for cid in (item.get("concept_ids") or [])
            ],
        }
        if banner:
            result["reference_warning_ru"] = banner
    else:
        return strip_proactive_from_transfer(result)
    return result
