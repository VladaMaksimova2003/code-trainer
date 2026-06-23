"""Student-facing display helpers for curriculum showcase tasks."""



from __future__ import annotations

import re
from typing import Any



from application.curriculum.display.pascal_tc_pedagogy import (
    build_expected_concepts_payload,
    _teacher_expected_concept_ids_for_language,
)

from application.curriculum.pascal.showcase.pascal_showcase_registry import all_showcase_title_prefixes
from application.curriculum.python.showcase.python_v311_registry import PYTHON_V311_SHOWCASE_COLLECTIONS


def all_curriculum_showcase_title_prefixes() -> tuple[str, ...]:
    prefixes = set(all_showcase_title_prefixes())
    for col in PYTHON_V311_SHOWCASE_COLLECTIONS:
        prefixes.add(col.title_prefix)
    return tuple(sorted(prefixes, key=len, reverse=True))


SHOWCASE_TITLE_PREFIXES: tuple[str, ...] = all_curriculum_showcase_title_prefixes()

_CURRICULUM_BRACKET_PREFIX = re.compile(
    r"^\[(?:Pascal v3\.1\.1|Python v1|C\+\+ v1|C# v1|Java v1|Pascal Showcase|Pascal Loops Showcase|Pascal Conditions Showcase|\d+\.\s[^\]]+)[^\]]*\]\s*",
    re.IGNORECASE,
)


def resolve_showcase_technical_concept_id(
    tc_id: str | None,
    study_order_tc: list[str] | tuple[str, ...],
) -> str | None:
    """Map imported/legacy TC ids into a chapter section bucket."""
    order = [str(item).strip() for item in study_order_tc if str(item).strip()]
    if not order:
        return str(tc_id).strip() if tc_id else None
    resolved = str(tc_id or "").strip()
    if resolved in order:
        return resolved
    return order[0]


def strip_showcase_title_prefix(title: str) -> str:

    text = (title or "").strip()
    text = _CURRICULUM_BRACKET_PREFIX.sub("", text, count=1)

    for prefix in SHOWCASE_TITLE_PREFIXES:

        if text.startswith(prefix):

            return text[len(prefix) :].strip()

    return text





_KNOWN_STARTER_LANGS = ("pascal", "python", "cpp", "csharp", "java")


def _starter_field_names() -> tuple[str, ...]:
    return tuple(f"starter_{lang}" for lang in _KNOWN_STARTER_LANGS)


def _merge_starter_fields_into_curriculum(
    curriculum: dict[str, Any],
    showcase_fields: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(curriculum)
    for key in _starter_field_names():
        if showcase_fields.get(key) is not None:
            merged[key] = showcase_fields[key]
    for key, value in showcase_fields.items():
        if str(key).startswith("starter_") and value is not None:
            merged[str(key)] = value
    return merged


def _extract_showcase_student_fields(code_examples: Any) -> dict[str, Any]:

    if not isinstance(code_examples, dict):

        return {}

    showcase = code_examples.get("curriculum_showcase")

    if not isinstance(showcase, dict):

        return {}

    fields: dict[str, Any] = {}

    for key in (

        "known_language_variants",

        "expected_output",

        "assemble_context",

        "primary_action",

        "technical_concept_id",

        "concept_patterns",

        "target_language",

        "pascal_features",

        "expected_concept_ids",

        "expected_concepts",

        "slot_id",

        "slot_pattern_id",

        "exercise_pattern_id",

        "task_format",

        *_starter_field_names(),

    ):

        if key in showcase and showcase[key] is not None:

            fields[key] = showcase[key]

    for key, value in showcase.items():
        if str(key).startswith("starter_") and value is not None:
            fields[str(key)] = value

    return fields





def sanitize_student_code_examples(code_examples: Any) -> Any:

    if not isinstance(code_examples, dict):

        return code_examples

    sanitized = dict(code_examples)

    sanitized.pop("curriculum_showcase", None)

    return sanitized





def _known_languages_from_payload(payload: dict[str, Any]) -> list[str]:

    from application.curriculum.display.pascal_hint_engine import KNOWN_SOURCE_LANGUAGES



    langs: list[str] = []

    examples = payload.get("code_examples") or {}

    if isinstance(examples, dict):

        for key in examples:

            lang = str(key).lower()

            if lang in KNOWN_SOURCE_LANGUAGES:

                langs.append(lang)

    variants = payload.get("known_language_variants") or {}

    if isinstance(variants, dict):

        for key in variants:

            lang = str(key).lower()

            if lang in KNOWN_SOURCE_LANGUAGES and lang not in langs:

                langs.append(lang)

    return langs





def _resolve_showcase_target_language(
    showcase_fields: dict[str, Any],
    curriculum: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> str | None:
    curriculum = curriculum or {}
    payload = payload or {}
    for candidate in (
        payload.get("requested_target_language"),
        payload.get("target_language"),
        payload.get("language"),
        curriculum.get("target_language"),
        curriculum.get("language"),
        showcase_fields.get("target_language"),
    ):
        lang = str(candidate or "").lower()
        if lang in {"pascal", "python", "cpp", "csharp", "java"}:
            return lang
    return None


def _apply_showcase_target_language(payload: dict[str, Any], showcase_fields: dict[str, Any]) -> dict[str, Any]:
    target = _resolve_showcase_target_language(
        showcase_fields,
        payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {},
        payload,
    )
    if not target:
        return payload
    result = dict(payload)
    result["target_language"] = target
    result["language"] = target
    return result


def _is_pascal_showcase_payload(payload: dict[str, Any], showcase_fields: dict[str, Any]) -> bool:

    curriculum = payload.get("curriculum") or {}

    if str(curriculum.get("language") or "").lower() == "pascal":

        return True

    if str(showcase_fields.get("target_language") or "").lower() == "pascal":

        return True

    if str(payload.get("target_language") or "").lower() == "pascal":

        return True

    return False





def enrich_pascal_showcase_hints(payload: dict[str, Any]) -> dict[str, Any]:

    """Compute expected pedagogical concepts for Pascal/Python curriculum tasks."""

    raw_examples = payload.get("code_examples")

    showcase_fields = _extract_showcase_student_fields(raw_examples)

    target_lang = _resolve_showcase_target_language(
        showcase_fields,
        payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {},
        payload,
    )
    if target_lang not in {"pascal", "python", "cpp", "csharp", "java"}:
        if showcase_fields:
            return _apply_showcase_target_language(dict(payload), showcase_fields)
        return payload

    if target_lang in {"cpp", "python", "csharp", "java"} and showcase_fields.get("expected_concept_ids"):
        payload = dict(payload)
        payload["expected_concept_ids"] = showcase_fields["expected_concept_ids"]

    hint_input = dict(payload)
    hint_input.update(showcase_fields)

    expected_by_lang = showcase_fields.get("expected_concepts")
    if not isinstance(expected_by_lang, dict):
        raw_examples = payload.get("code_examples")
        if isinstance(raw_examples, dict):
            expected_by_lang = raw_examples.get("expected_concepts")
    if isinstance(expected_by_lang, dict):
        lang_ids = expected_by_lang.get(target_lang)
        if isinstance(lang_ids, list) and lang_ids:
            hint_input["expected_concept_ids"] = lang_ids
            hint_input["expected_concepts"] = expected_by_lang

    curriculum = dict(payload.get("curriculum") or {})

    from application.tasks.services.teacher_assembly_preservation import (
        has_teacher_assembly_override,
    )

    code_examples = payload.get("code_examples")
    teacher_override = isinstance(code_examples, dict) and has_teacher_assembly_override(
        code_examples
    )

    primary_tc = (
        curriculum.get("technical_concept_id")
        or showcase_fields.get("technical_concept_id")
        or ""
    )

    pattern_key = _resolve_algo_pattern_key(hint_input, showcase_fields)
    slot_id = str(
        showcase_fields.get("slot_id")
        or showcase_fields.get("slug")
        or curriculum.get("slot_id")
        or payload.get("slot_id")
        or payload.get("pedagogical_slot_id")
        or ""
    ).strip()
    if pattern_key and (slot_id or pattern_key) and not _has_teacher_expected_concepts(
        showcase_fields,
    ):
        from application.curriculum.content.algo_syntax_showcase_meta import (
            enrich_student_expected_concepts,
        )

        effective_slot = slot_id or f"pas_{int(pattern_key.split('_')[1]):03d}"
        enriched = enrich_student_expected_concepts(
            dict(payload),
            pattern_key=pattern_key,
            slot_id=effective_slot,
            target_language=str(target_lang or "pascal"),
            slot_pattern_id=str(
                showcase_fields.get("slot_pattern_id")
                or showcase_fields.get("exercise_pattern_id")
                or curriculum.get("exercise_pattern_id")
                or pattern_key
            ),
        )
        transfer = payload.get("transfer") or curriculum.get("transfer")
        if transfer:
            enriched["transfer"] = transfer
            cur = dict(enriched.get("curriculum") or {})
            cur["transfer"] = transfer
            enriched["curriculum"] = cur
        return _apply_showcase_target_language(enriched, showcase_fields)

    if teacher_override:
        teacher_ids = _teacher_expected_concept_ids_for_language(hint_input, target_lang)
        if teacher_ids:
            from application.curriculum.validation.expected_concept_checker import (
                build_display_expected_concept_cards,
            )
            from application.tasks.services.authoring_expected_concepts import (
                resolve_authoring_expected_concepts_by_language,
            )

            cards = build_display_expected_concept_cards(teacher_ids)
            result = dict(payload)
            result["expected_concept_ids"] = teacher_ids
            result["expected_concepts"] = cards
            curriculum = dict(result.get("curriculum") or {})
            curriculum["expected_concept_ids"] = teacher_ids
            curriculum["expected_concepts"] = cards
            if isinstance(code_examples, dict):
                by_lang = resolve_authoring_expected_concepts_by_language(code_examples)
                if by_lang:
                    curriculum["expected_concept_ids_by_language"] = {
                        lang: list(ids) for lang, ids in by_lang.items()
                    }
                    curriculum["expected_concepts_by_language"] = {
                        lang: build_display_expected_concept_cards(ids)
                        for lang, ids in by_lang.items()
                    }
            result["curriculum"] = curriculum
            return _apply_showcase_target_language(result, showcase_fields)

    if not primary_tc:
        teacher_ids = _teacher_expected_concept_ids_for_language(hint_input, target_lang)
        if teacher_ids:
            from application.curriculum.validation.expected_concept_checker import (
                build_display_expected_concept_cards,
            )

            cards = build_display_expected_concept_cards(teacher_ids)
            result = dict(payload)
            result["expected_concept_ids"] = teacher_ids
            result["expected_concepts"] = cards
            curriculum = dict(result.get("curriculum") or {})
            curriculum["expected_concept_ids"] = teacher_ids
            curriculum["expected_concepts"] = cards
            result["curriculum"] = curriculum
            return _apply_showcase_target_language(result, showcase_fields)

    known_langs = [
        lang
        for lang in _known_languages_from_payload(hint_input)
        if lang in {"pascal", "python", "cpp", "java", "csharp"}
    ]

    concepts_payload = build_expected_concepts_payload(

        primary_tc=str(primary_tc),

        task_payload=hint_input,

        known_languages=known_langs,

        learning_language=target_lang,

    )



    payload = dict(payload)

    payload.update(concepts_payload)

    payload["technical_concepts"] = concepts_payload["detected_technical_concepts"]



    curriculum = dict(payload.get("curriculum") or {})

    curriculum["technical_concept_id"] = str(primary_tc)

    curriculum.update(concepts_payload)

    curriculum["technical_concepts"] = concepts_payload["detected_technical_concepts"]

    payload["curriculum"] = curriculum

    return _apply_showcase_target_language(payload, showcase_fields)


def finalize_student_task_payload(
    payload: dict[str, Any],
    *,
    source_language: str | None = None,
    target_language: str | None = None,
) -> dict[str, Any]:
    """Last-mile student payload: clean title, algo concepts, MPLT transfer."""
    result = dict(payload)
    raw_examples = result.get("code_examples")
    showcase_fields = _extract_showcase_student_fields(raw_examples)
    curriculum = result.get("curriculum") if isinstance(result.get("curriculum"), dict) else {}

    title = result.get("title")
    if title is not None:
        from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled
        from application.curriculum.mirror.curriculum_slot_mirror import canonical_title_for_slot

        slot_id = str(
            showcase_fields.get("slot_id")
            or curriculum.get("slot_id")
            or result.get("slot_id")
            or ""
        ).strip()
        canonical = None
        if is_catalog_sync_enabled():
            canonical = canonical_title_for_slot(slot_id or None)
        result["title"] = canonical if canonical else strip_showcase_title_prefix(str(title))

    result = enrich_pascal_showcase_hints(result)
    result = promote_task_pedagogy_fields(result)
    effective_target = (
        str(target_language or result.get("target_language") or result.get("language") or "").strip().lower()
        or None
    )
    return refresh_language_pair_pedagogy(
        result,
        source_language=source_language,
        target_language=effective_target,
    )


def promote_task_pedagogy_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Expose teacher-authored hints and post-solve text on the student payload."""
    examples = payload.get("code_examples")
    if not isinstance(examples, dict):
        return payload

    showcase = examples.get("curriculum_showcase")
    showcase_dict = showcase if isinstance(showcase, dict) else {}

    hints_raw = examples.get("hints") or showcase_dict.get("hints")
    hints: list[str] = []
    if isinstance(hints_raw, list):
        hints = [str(item).strip() for item in hints_raw if str(item).strip()]

    post_solve = str(
        examples.get("post_solve_explanation")
        or showcase_dict.get("post_solve_explanation")
        or ""
    ).strip()

    if not hints and not post_solve:
        return payload

    result = dict(payload)
    curriculum = dict(result.get("curriculum") or {})

    if hints:
        result["hints"] = hints
        curriculum["hints"] = hints

    if post_solve:
        result["post_solve_explanation"] = post_solve
        curriculum["post_solve_explanation"] = post_solve

    result["curriculum"] = curriculum
    return result





def _merge_known_language_examples(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any],
) -> None:
    """Expose «Я знаю» reference code in code_examples when only variants metadata exists."""
    from application.curriculum.display.pascal_hint_engine import KNOWN_SOURCE_LANGUAGES

    target = _resolve_showcase_target_language(
        showcase_fields,
        payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {},
        payload,
    )
    if target == "python":
        from application.curriculum.python.catalog.python_known_language import (
            code_examples_from_variants,
        )
    elif target == "cpp":
        from application.curriculum.cpp.catalog.cpp_known_language import (
            code_examples_from_variants,
        )
    elif target == "csharp":
        from application.curriculum.csharp.catalog.csharp_known_language import (
            code_examples_from_variants,
        )
    elif target == "java":
        from application.curriculum.java.catalog.java_known_language import (
            code_examples_from_variants,
        )
    else:
        from application.curriculum.pascal.catalog.pascal_known_language import (
            code_examples_from_variants,
        )

    examples = dict(payload.get("code_examples") or {})
    variants = payload.get("known_language_variants") or showcase_fields.get("known_language_variants")
    if isinstance(variants, dict) and variants:
        for lang, code in code_examples_from_variants(variants).items():
            if not str(examples.get(lang) or "").strip():
                examples[lang] = code

    assemble = payload.get("assemble_context") or showcase_fields.get("assemble_context")
    if isinstance(assemble, dict):
        for lang, code in assemble.items():
            lang_key = str(lang).lower()
            if lang_key in KNOWN_SOURCE_LANGUAGES and str(code or "").strip():
                if not str(examples.get(lang_key) or "").strip():
                    examples[lang_key] = str(code or "")

    source_language = str(payload.get("source_language") or "").lower()
    source_code = str(payload.get("source_code") or "").strip()
    if source_language in KNOWN_SOURCE_LANGUAGES and source_code:
        if not str(examples.get(source_language) or "").strip():
            examples[source_language] = source_code

    payload["code_examples"] = examples


def _sync_formatted_reference_codes(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any],
    *,
    teacher_override: bool = False,
) -> None:
    """Ensure algo-syntax reference snippets are multi-line and readable."""
    from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled

    if not is_catalog_sync_enabled():
        return
    if teacher_override:
        return

    from application.curriculum.content.algo_syntax_task_extra import (
        is_algo_syntax_slot,
        resolve_slot_pattern_key,
    )
    from application.curriculum.content.v4_code_format import normalize_authoring_code
    from application.curriculum.content.v4_reference_code import get_reference_code
    from application.curriculum.display.pascal_hint_engine import KNOWN_SOURCE_LANGUAGES

    curriculum = payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {}
    slot_id = str(
        showcase_fields.get("slot_id")
        or showcase_fields.get("slug")
        or payload.get("slot_id")
        or curriculum.get("slot_id")
        or ""
    ).strip()
    if not is_algo_syntax_slot(slot_id):
        return

    pattern_key = resolve_slot_pattern_key(
        slot_id,
        slot_pattern_id=str(
            showcase_fields.get("slot_pattern_id")
            or payload.get("slot_pattern_id")
            or curriculum.get("slot_pattern_id")
            or ""
        ).strip()
        or None,
    )

    task_format = str(
        showcase_fields.get("task_format")
        or payload.get("task_format")
        or curriculum.get("task_format")
        or ""
    )
    action = str(
        showcase_fields.get("primary_action")
        or curriculum.get("action")
        or payload.get("primary_action")
        or ""
    ).lower()
    is_debug_task = task_format in {"исправление", "поиск_ошибки"} or action == "debug"
    is_translation_task = task_format.startswith("перевод") or action == "implement"
    examples = dict(payload.get("code_examples") or {})

    if is_debug_task:
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_debug_starter,
            algo_fixed_code,
        )

        for lang in KNOWN_SOURCE_LANGUAGES:
            if str(examples.get(lang) or "").strip():
                continue
            fixed = str(algo_fixed_code(slot_id, lang) or "")
            if fixed.strip():
                examples[lang] = fixed

        variants = showcase_fields.get("known_language_variants")
        if isinstance(variants, dict):
            refreshed_variants = dict(variants)
            for lang in KNOWN_SOURCE_LANGUAGES:
                if isinstance(refreshed_variants.get(lang), dict):
                    entry = refreshed_variants[lang]
                    if str(entry.get("source_code") or "").strip():
                        continue
                fixed = str(algo_fixed_code(slot_id, lang) or "")
                if not fixed.strip():
                    continue
                entry = refreshed_variants.get(lang)
                refreshed_variants[lang] = {
                    **(entry if isinstance(entry, dict) else {}),
                    "source_code": fixed,
                }
            showcase_fields["known_language_variants"] = refreshed_variants

        for lang in _KNOWN_STARTER_LANGS:
            starter_key = f"starter_{lang}"
            buggy_key = f"buggy_{lang}"
            if str(examples.get(buggy_key) or "").strip():
                continue
            if str(showcase_fields.get(starter_key) or "").strip():
                continue
            starter = str(algo_debug_starter(slot_id, lang) or "")
            if starter.strip():
                showcase_fields[starter_key] = starter

        payload["code_examples"] = examples
        return

    if is_translation_task:
        from application.curriculum.content.algo_syntax_task_extra import algo_translation_starter

        target = _resolve_showcase_target_language(
            showcase_fields,
            curriculum if isinstance(curriculum, dict) else {},
            payload,
        )
        starter = str(
            showcase_fields.get(f"starter_{target}")
            or payload.get(f"starter_{target}")
            or algo_translation_starter(slot_id, target)
        ).strip()
        if starter:
            showcase_fields[f"starter_{target}"] = starter
            if not str(examples.get(target) or "").strip():
                examples[target] = starter

        payload["code_examples"] = examples
        return

    for lang in KNOWN_SOURCE_LANGUAGES:
        existing = str(examples.get(lang) or "")
        if existing.strip():
            examples[lang] = normalize_authoring_code(existing)
            continue
        fresh = str(get_reference_code(slot_id, lang, pattern_key=pattern_key) or "")
        if fresh.strip():
            examples[lang] = fresh

    variants = showcase_fields.get("known_language_variants")
    if isinstance(variants, dict):
        refreshed_variants = dict(variants)
        for lang, entry in variants.items():
            lang_key = str(lang).lower()
            if not isinstance(entry, dict):
                continue
            existing = str(entry.get("source_code") or "")
            if existing.strip():
                refreshed_variants[lang_key] = {
                    **entry,
                    "source_code": normalize_authoring_code(existing),
                }
                continue
            fresh = str(get_reference_code(slot_id, lang_key, pattern_key=pattern_key) or "")
            code = fresh if fresh.strip() else existing
            if code.strip():
                refreshed_variants[lang_key] = {**entry, "source_code": code}
        showcase_fields["known_language_variants"] = refreshed_variants
        for lang, entry in refreshed_variants.items():
            if isinstance(entry, dict) and entry.get("source_code"):
                examples[str(lang).lower()] = str(entry["source_code"])

    assemble = showcase_fields.get("assemble_context")
    if isinstance(assemble, dict):
        refreshed_assemble = {}
        for lang, code in assemble.items():
            lang_key = str(lang).lower()
            existing = str(code or "")
            if existing.strip():
                refreshed_assemble[lang_key] = normalize_authoring_code(existing)
                continue
            fresh = str(get_reference_code(slot_id, lang_key, pattern_key=pattern_key) or "")
            text = fresh if fresh.strip() else existing
            if text.strip():
                refreshed_assemble[lang_key] = text
        showcase_fields["assemble_context"] = refreshed_assemble
        for lang, code in refreshed_assemble.items():
            if lang in KNOWN_SOURCE_LANGUAGES:
                examples[lang] = code

    payload["code_examples"] = examples


def _assembly_payload_is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not value
    return False


def _showcase_fields_need_catalog_refresh(showcase_fields: dict[str, Any]) -> bool:
    from application.curriculum.pascal.catalog.pascal_catalog_runtime import (
        _LEGACY_ROWS,
        catalog_extra_for_slot,
        is_pascal_catalog_slot,
    )
    from application.curriculum.python.catalog.python_catalog_runtime import is_v4_python_slot
    from application.curriculum.python.catalog.python_v311_known_code import is_demo_known_code

    slot_id = str(
        showcase_fields.get("slot_id")
        or showcase_fields.get("slug")
        or ""
    ).strip()
    if is_pascal_catalog_slot(slot_id):
        extra = catalog_extra_for_slot(slot_id)
        if not extra:
            return False
        if slot_id in _LEGACY_ROWS:
            return True

        goal = str(showcase_fields.get("educational_goal") or showcase_fields.get("description") or "").strip()
        catalog_goal = str(extra.get("educational_goal") or "").strip()
        if catalog_goal and goal != catalog_goal:
            return True

        blocks = showcase_fields.get("blocks")
        catalog_blocks = extra.get("blocks")
        if _assembly_payload_is_empty(blocks) and not _assembly_payload_is_empty(catalog_blocks):
            return True
        if _assembly_payload_is_empty(blocks) and not _assembly_payload_is_empty(extra.get("template")):
            return True
        return False
    if not is_v4_python_slot(slot_id):
        return False

    variants = showcase_fields.get("known_language_variants")
    if isinstance(variants, dict):
        pascal_entry = variants.get("pascal")
        pascal_code = ""
        if isinstance(pascal_entry, dict):
            pascal_code = str(pascal_entry.get("source_code") or "")
        elif isinstance(pascal_entry, str):
            pascal_code = pascal_entry
        if is_demo_known_code(pascal_code):
            return True

    test_cases = showcase_fields.get("test_cases")
    if not isinstance(test_cases, list) or not test_cases:
        return True

    if _has_teacher_expected_concepts(showcase_fields):
        return False

    expected = showcase_fields.get("expected_concept_ids")
    if not expected:
        return True

    from application.curriculum.python.catalog.python_catalog_runtime import (
        expected_concepts_for_slot,
    )

    catalog_concepts = expected_concepts_for_slot(slot_id)
    if catalog_concepts and list(expected) != catalog_concepts:
        return True

    return False


def _has_teacher_expected_concepts(showcase_fields: dict[str, Any]) -> bool:
    """True when a teacher saved custom TC lists (do not overwrite from catalog)."""
    raw = showcase_fields.get("expected_concepts")
    if not isinstance(raw, dict):
        return False
    return any(isinstance(ids, list) and ids for ids in raw.values())


def _refresh_catalog_showcase_fields(showcase_fields: dict[str, Any]) -> None:
    """Reload catalog metadata for stale DB rows (Python v4 and Pascal pas_*/legacy)."""
    from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled

    if not is_catalog_sync_enabled():
        return

    from application.curriculum.pascal.catalog.pascal_catalog_runtime import (
        apply_catalog_fields_to_showcase as apply_pascal_catalog_fields,
        is_pascal_catalog_slot,
    )
    from application.curriculum.python.catalog.python_catalog_runtime import (
        apply_catalog_fields_to_showcase,
        is_v4_python_slot,
    )
    from application.curriculum.python.catalog.python_v311_known_code import (
        is_demo_known_code,
        resolve_known_codes,
    )

    slot_id = str(
        showcase_fields.get("slot_id")
        or showcase_fields.get("slug")
        or ""
    ).strip()
    if is_pascal_catalog_slot(slot_id):
        refreshed = apply_pascal_catalog_fields(showcase_fields)
        showcase_fields.clear()
        showcase_fields.update(refreshed)
        return
    if not is_v4_python_slot(slot_id):
        return

    refreshed = apply_catalog_fields_to_showcase(showcase_fields)
    showcase_fields.clear()
    showcase_fields.update(refreshed)

    _refresh_demo_known_variants(showcase_fields)

    variants = showcase_fields.get("known_language_variants")
    if isinstance(variants, dict):
        pascal_entry = variants.get("pascal")
        pascal_code = ""
        if isinstance(pascal_entry, dict):
            pascal_code = str(pascal_entry.get("source_code") or "")
        if is_demo_known_code(pascal_code):
            pascal, cpp, java, csharp = resolve_known_codes(slot_id)
            if not is_demo_known_code(pascal):
                from application.curriculum.python.catalog.python_known_language import (
                    build_known_language_variants,
                    code_examples_from_variants,
                )

                rebuilt = build_known_language_variants(
                    pascal=pascal,
                    cpp=cpp,
                    java=java,
                    csharp=csharp,
                )
                if isinstance(variants.get("python"), dict):
                    rebuilt["python"] = variants["python"]
                showcase_fields["known_language_variants"] = rebuilt
                showcase_fields["assemble_context"] = code_examples_from_variants(rebuilt)


def _refresh_demo_known_variants(showcase_fields: dict[str, Any]) -> None:
    """Replace seeded demo stubs with catalog/v4 snippets for Python showcase tasks."""
    variants = showcase_fields.get("known_language_variants")
    if not isinstance(variants, dict) or not variants:
        return
    pascal_entry = variants.get("pascal")
    pascal_code = ""
    if isinstance(pascal_entry, dict):
        pascal_code = str(pascal_entry.get("source_code") or "")
    elif isinstance(pascal_entry, str):
        pascal_code = pascal_entry

    from application.curriculum.python.catalog.python_v311_known_code import (
        is_demo_known_code,
        resolve_known_codes,
    )

    if not is_demo_known_code(pascal_code):
        return

    slot_id = str(
        showcase_fields.get("slot_id")
        or showcase_fields.get("slug")
        or ""
    ).strip()
    if not slot_id:
        return

    target = str(showcase_fields.get("target_language") or "").strip().lower()
    if target and target != "python":
        return

    pascal, cpp, java, csharp = resolve_known_codes(slot_id)
    if is_demo_known_code(pascal):
        return

    from application.curriculum.python.catalog.python_known_language import (
        build_known_language_variants,
        code_examples_from_variants,
    )

    refreshed = build_known_language_variants(
        pascal=pascal,
        cpp=cpp,
        java=java,
        csharp=csharp,
    )
    if isinstance(variants.get("python"), dict):
        refreshed["python"] = variants["python"]
    showcase_fields["known_language_variants"] = refreshed
    showcase_fields["assemble_context"] = code_examples_from_variants(refreshed)


def _resolve_algo_pattern_key(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any] | None,
) -> str | None:
    """Map student task payload to ALGO_SYNTAX_META pattern key (task_NNN)."""
    fields = showcase_fields or {}
    curriculum = payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {}
    from application.curriculum.content.algo_syntax_task_extra import (
        resolve_slot_pattern_key,
    )

    from application.curriculum.content.algo_syntax_showcase_meta import resolve_pattern_key

    slot_id = str(
        fields.get("slot_id")
        or fields.get("slug")
        or payload.get("slot_id")
        or curriculum.get("slot_id")
        or ""
    ).strip()
    slot_pattern = str(
        fields.get("slot_pattern_id")
        or fields.get("exercise_pattern_id")
        or payload.get("slot_pattern_id")
        or payload.get("exercise_pattern_id")
        or curriculum.get("slot_pattern_id")
        or curriculum.get("exercise_pattern_id")
        or ""
    ).strip()
    return resolve_pattern_key(
        slot_id or None,
        slot_pattern_id=slot_pattern or None,
        exercise_pattern_id=slot_pattern or None,
    )


def _attach_transfer_pitfall_meta(
    payload: dict[str, Any],
    showcase_fields: dict[str, Any] | None,
    *,
    source_language: str | None = None,
    target_language: str | None = None,
) -> None:
    """Expose MPLT pitfall texts on student task payload (proactive warnings)."""
    pattern = _resolve_algo_pattern_key(payload, showcase_fields)
    if not pattern:
        return

    curriculum = payload.get("curriculum") if isinstance(payload.get("curriculum"), dict) else {}
    target_lang = str(
        target_language
        or payload.get("target_language")
        or payload.get("language")
        or _resolve_showcase_target_language(
            showcase_fields or {},
            curriculum,
            payload,
        )
        or "",
    ).strip().lower()
    if not target_lang:
        return

    from application.curriculum.content.algo_syntax_showcase_meta import (
        resolve_source_language,
        transfer_meta_for_language_pair,
    )

    if source_language:
        payload["requested_source_language"] = str(source_language).strip().lower()

    source_lang = (
        str(source_language).strip().lower()
        if source_language
        else resolve_source_language(
            payload,
            showcase_fields or {},
            target_language=target_lang,
        )
    )
    transfer = transfer_meta_for_language_pair(
        pattern,
        source_language=source_lang,
        target_language=target_lang,
    )
    from application.curriculum.display.proactive_scope import (
        filter_proactive_items_for_workspace,
    )

    transfer = filter_proactive_items_for_workspace(
        transfer,
        payload,
        showcase_fields,
        target_language=target_lang,
    )
    payload["transfer"] = transfer
    curriculum_dict = dict(payload.get("curriculum") or {})
    curriculum_dict["transfer"] = transfer
    payload["curriculum"] = curriculum_dict


def refresh_language_pair_pedagogy(
    payload: dict[str, Any],
    *,
    source_language: str | None = None,
    target_language: str | None = None,
) -> dict[str, Any]:
    """Recompute MPLT banner + expected concept cards for source → target pair."""
    result = dict(payload)
    showcase_fields = _extract_showcase_student_fields(result.get("code_examples"))
    curriculum = dict(result.get("curriculum") or {})

    target_lang = str(
        target_language
        or result.get("target_language")
        or result.get("language")
        or _resolve_showcase_target_language(showcase_fields, curriculum, result)
        or "pascal",
    ).strip().lower()

    from application.curriculum.content.algo_syntax_showcase_meta import resolve_source_language
    from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta
    from application.curriculum.validation.expected_concept_checker import (
        build_display_expected_concept_cards_for_pair,
    )
    from application.tasks.services.authoring_expected_concepts import (
        resolve_authoring_expected_concepts_by_language,
    )

    source_lang = (
        str(source_language).strip().lower()
        if source_language
        else resolve_source_language(result, showcase_fields, target_language=target_lang)
    )

    if source_lang:
        result["requested_source_language"] = source_lang
        result["source_language"] = source_lang
    result["requested_target_language"] = target_lang
    result["target_language"] = target_lang
    result["language"] = target_lang

    _attach_transfer_pitfall_meta(
        result,
        showcase_fields,
        source_language=source_lang,
        target_language=target_lang,
    )

    pattern = _resolve_algo_pattern_key(result, showcase_fields)
    transfer = result.get("transfer") if isinstance(result.get("transfer"), dict) else {}
    transfer_pitfall_ids = [
        str(pid).strip()
        for pid in (transfer.get("pitfall_ids") or [])
        if str(pid).strip()
    ]
    if not transfer_pitfall_ids and pattern:
        legacy = resolve_v128_transfer_meta(pattern).get("pitfall_id")
        if legacy:
            transfer_pitfall_ids = [str(legacy)]

    from application.curriculum.display.proactive_scope import (
        proactive_pitfall_applies_to_student_workspace,
    )

    active_pitfall_ids = [
        pid
        for pid in transfer_pitfall_ids
        if proactive_pitfall_applies_to_student_workspace(
            result,
            showcase_fields,
            pitfall_id=pid,
            target_language=target_lang,
        )
    ]
    pair_pitfall_id = active_pitfall_ids[0] if active_pitfall_ids else None

    from application.curriculum.content.algo_syntax_showcase_meta import build_pair_task_hints
    from application.curriculum.display.chapter1_algo_basics_hints import (
        chapter1_hints_for_pattern,
    )
    from application.curriculum.display.chapter1_algo_basics_pitfalls import (
        is_chapter1_pattern,
    )
    from application.curriculum.display.chapter2_branches_hints import (
        chapter2_hints_for_pattern,
    )
    from application.curriculum.display.chapter2_branches_pitfalls import (
        is_chapter2_pattern,
    )
    from application.curriculum.display.chapter3_loops_hints import (
        chapter3_hints_for_pattern,
    )
    from application.curriculum.display.chapter3_loops_pitfalls import (
        is_chapter3_pattern,
    )
    from application.curriculum.display.chapter4_arrays_hints import (
        chapter4_hints_for_pattern,
    )
    from application.curriculum.display.chapter4_arrays_pitfalls import (
        is_chapter4_pattern,
    )
    from application.curriculum.display.chapter5_strings_hints import (
        chapter5_hints_for_pattern,
    )
    from application.curriculum.display.chapter5_strings_pitfalls import (
        is_chapter5_pattern,
    )

    base_hints = list(
        result.get("hints")
        or curriculum.get("hints")
        or (showcase_fields.get("hints") if isinstance(showcase_fields.get("hints"), list) else [])
        or [],
    )
    if not base_hints and pattern and is_chapter1_pattern(pattern):
        base_hints = chapter1_hints_for_pattern(pattern)
    elif not base_hints and pattern and is_chapter2_pattern(pattern):
        base_hints = chapter2_hints_for_pattern(pattern)
    elif not base_hints and pattern and is_chapter3_pattern(pattern):
        base_hints = chapter3_hints_for_pattern(pattern)
    elif not base_hints and pattern and is_chapter4_pattern(pattern):
        base_hints = chapter4_hints_for_pattern(pattern)
    elif not base_hints and pattern and is_chapter5_pattern(pattern):
        base_hints = chapter5_hints_for_pattern(pattern)
    pair_hints = build_pair_task_hints(
        base_hints,
        pitfall_id=str(pair_pitfall_id) if pair_pitfall_id else None,
        source_language=source_lang,
        target_language=target_lang,
    )
    if pair_hints:
        result["hints"] = pair_hints
        curriculum["hints"] = pair_hints

    raw_examples = result.get("code_examples")
    by_lang_ids = curriculum.get("expected_concept_ids_by_language")
    if not isinstance(by_lang_ids, dict) and isinstance(raw_examples, dict):
        by_lang_ids = resolve_authoring_expected_concepts_by_language(raw_examples)

    if isinstance(by_lang_ids, dict) and by_lang_ids:
        cards_by_lang = {
            lang: build_display_expected_concept_cards_for_pair(
                list(ids),
                source_language=source_lang,
                target_language=str(lang).strip().lower(),
                pitfall_ids=active_pitfall_ids or None,
            )
            for lang, ids in by_lang_ids.items()
            if isinstance(ids, list) and ids
        }
        if cards_by_lang and pattern and is_chapter2_pattern(pattern):
            from application.curriculum.display.chapter2_branches_concept_examples import (
                enrich_chapter2_concept_cards,
            )

            cards_by_lang = {
                lang: enrich_chapter2_concept_cards(
                    list(rows),
                    pattern_key=pattern,
                    pitfall_ids=active_pitfall_ids,
                    source_language=source_lang,
                    target_language=str(lang).strip().lower(),
                )
                for lang, rows in cards_by_lang.items()
            }
        if cards_by_lang and pattern and is_chapter3_pattern(pattern):
            from application.curriculum.display.chapter3_loops_concept_examples import (
                enrich_chapter3_concept_cards,
            )

            cards_by_lang = {
                lang: enrich_chapter3_concept_cards(
                    list(rows),
                    pattern_key=pattern,
                    pitfall_ids=active_pitfall_ids,
                    source_language=source_lang,
                    target_language=str(lang).strip().lower(),
                )
                for lang, rows in cards_by_lang.items()
            }
        if cards_by_lang:
            curriculum["expected_concepts_by_language"] = cards_by_lang
            result["expected_concepts_by_language"] = cards_by_lang
            target_cards = cards_by_lang.get(target_lang) or next(iter(cards_by_lang.values()))
            target_ids = list(by_lang_ids.get(target_lang) or by_lang_ids.get(next(iter(by_lang_ids))) or [])
            curriculum["expected_concepts"] = target_cards
            curriculum["expected_concept_ids"] = target_ids
            result["expected_concepts"] = target_cards
            result["expected_concept_ids"] = target_ids
            result["constructions"] = target_ids
            result["required_structures"] = target_ids
    else:
        ids = list(
            curriculum.get("expected_concept_ids")
            or result.get("expected_concept_ids")
            or []
        )
        if ids:
            cards = build_display_expected_concept_cards_for_pair(
                ids,
                source_language=source_lang,
                target_language=target_lang,
                pitfall_ids=active_pitfall_ids or None,
            )
            if pattern and is_chapter2_pattern(pattern):
                from application.curriculum.display.chapter2_branches_concept_examples import (
                    enrich_chapter2_concept_cards,
                )

                cards = enrich_chapter2_concept_cards(
                    cards,
                    pattern_key=pattern,
                    pitfall_ids=active_pitfall_ids,
                    source_language=source_lang,
                    target_language=target_lang,
                )
            if pattern and is_chapter3_pattern(pattern):
                from application.curriculum.display.chapter3_loops_concept_examples import (
                    enrich_chapter3_concept_cards,
                )

                cards = enrich_chapter3_concept_cards(
                    cards,
                    pattern_key=pattern,
                    pitfall_ids=active_pitfall_ids,
                    source_language=source_lang,
                    target_language=target_lang,
                )
            curriculum["expected_concepts"] = cards
            result["expected_concepts"] = cards

    result["curriculum"] = curriculum
    return result


def sanitize_public_task_payload(task: dict[str, Any]) -> dict[str, Any]:

    payload = dict(task)

    raw_examples = payload.get("code_examples")

    showcase_fields = _extract_showcase_student_fields(raw_examples)
    from application.tasks.services.teacher_assembly_preservation import (
        merge_teacher_expected_concepts_into_showcase,
        payload_has_teacher_editor_override,
    )

    teacher_override = payload_has_teacher_editor_override(payload, raw_examples if isinstance(raw_examples, dict) else None)
    db_title = payload.get("title")
    db_description = payload.get("description")

    title = payload.get("title")

    from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled

    if title is not None and not teacher_override:
        from application.curriculum.mirror.curriculum_slot_mirror import canonical_title_for_slot

        slot_id = showcase_fields.get("slot_id") if showcase_fields else None
        if not slot_id:
            curriculum = payload.get("curriculum") or {}
            if isinstance(curriculum, dict):
                slot_id = curriculum.get("slot_id")
        canonical = None
        if is_catalog_sync_enabled():
            canonical = canonical_title_for_slot(str(slot_id) if slot_id else None)
        payload["title"] = canonical if canonical else strip_showcase_title_prefix(str(title))

    if showcase_fields:

        if teacher_override and isinstance(raw_examples, dict):
            merge_teacher_expected_concepts_into_showcase(showcase_fields, raw_examples)
        elif is_catalog_sync_enabled():
            from application.curriculum.python.catalog.python_catalog_runtime import (
                sync_v4_expected_concepts,
            )

            sync_v4_expected_concepts(showcase_fields)

        for key in ("blocks", "template", "correct_order", "original_code"):
            if key in payload and not _assembly_payload_is_empty(payload.get(key)):
                showcase_fields.setdefault(key, payload[key])

        assembly_before = {
            key: payload[key]
            for key in ("blocks", "template", "correct_order", "original_code")
            if key in payload and not _assembly_payload_is_empty(payload.get(key))
        }

        skip_assembly_catalog = False
        from application.tasks.services.teacher_assembly_preservation import (
            should_skip_catalog_assembly_refresh,
        )

        if should_skip_catalog_assembly_refresh(payload):
            skip_assembly_catalog = True
        elif isinstance(raw_examples, dict) and raw_examples.get("teacher_assembly_override"):
            skip_assembly_catalog = True

        if (
            _showcase_fields_need_catalog_refresh(showcase_fields)
            and not skip_assembly_catalog
            and not teacher_override
            and is_catalog_sync_enabled()
        ):
            _refresh_catalog_showcase_fields(showcase_fields)

        if teacher_override:
            from application.tasks.use_cases.debug_code_keys import strip_starter_fields

            strip_starter_fields(showcase_fields)
            if db_title is not None:
                payload["title"] = strip_showcase_title_prefix(str(db_title))
            if db_description is not None:
                payload["description"] = db_description
        else:
            goal = str(showcase_fields.get("educational_goal") or showcase_fields.get("description") or "").strip()
            if goal:
                payload["description"] = goal

        payload.update(showcase_fields)

        for key, value in assembly_before.items():
            if _assembly_payload_is_empty(payload.get(key)):
                payload[key] = value

        curriculum = dict(payload.get("curriculum") or {})

        if showcase_fields.get("known_language_variants"):

            curriculum["known_language_variants"] = showcase_fields["known_language_variants"]

        if showcase_fields.get("expected_output") is not None:

            curriculum["expected_output"] = showcase_fields["expected_output"]

        if showcase_fields.get("assemble_context"):

            curriculum["assemble_context"] = showcase_fields["assemble_context"]

        if showcase_fields.get("technical_concept_id"):

            curriculum["technical_concept_id"] = showcase_fields["technical_concept_id"]

        if showcase_fields.get("primary_action"):

            curriculum["action"] = showcase_fields["primary_action"]

        if showcase_fields.get("expected_concept_ids"):

            curriculum["expected_concept_ids"] = showcase_fields["expected_concept_ids"]

        if isinstance(showcase_fields.get("expected_concepts"), dict):

            curriculum["expected_concept_ids_by_language"] = {
                lang: list(ids)
                for lang, ids in showcase_fields["expected_concepts"].items()
                if isinstance(ids, list) and ids
            }

        if showcase_fields.get("pascal_features"):

            curriculum["pascal_features"] = showcase_fields["pascal_features"]

        if showcase_fields.get("task_format"):

            curriculum["task_format"] = showcase_fields["task_format"]

        if not teacher_override:
            curriculum = _merge_starter_fields_into_curriculum(curriculum, showcase_fields)

        if curriculum:

            payload["curriculum"] = curriculum

        target = _resolve_showcase_target_language(showcase_fields, curriculum, payload)
        if target:
            payload["language"] = target
            payload["target_language"] = target

    if "code_examples" in payload:

        payload["code_examples"] = sanitize_student_code_examples(raw_examples)

        _merge_known_language_examples(payload, showcase_fields)
        _sync_formatted_reference_codes(
            payload,
            showcase_fields or {},
            teacher_override=teacher_override,
        )

        if showcase_fields:
            curriculum = dict(payload.get("curriculum") or {})
            if showcase_fields.get("known_language_variants"):
                curriculum["known_language_variants"] = showcase_fields["known_language_variants"]
            if not teacher_override:
                curriculum = _merge_starter_fields_into_curriculum(curriculum, showcase_fields)
            if curriculum:
                payload["curriculum"] = curriculum

        if teacher_override:
            from application.tasks.use_cases.debug_code_keys import strip_starter_fields

            strip_starter_fields(payload)
            curriculum = dict(payload.get("curriculum") or {})
            strip_starter_fields(curriculum)
            if curriculum:
                payload["curriculum"] = curriculum

    from application.curriculum.catalog_sync_policy import is_catalog_sync_enabled
    from application.curriculum.python.catalog.python_catalog_runtime import (
        apply_catalog_fields_to_task_payload,
        is_v4_python_slot,
        sync_v4_expected_concepts,
    )

    if showcase_fields and not teacher_override and is_catalog_sync_enabled():
        sync_v4_expected_concepts(showcase_fields)
        slot_id = str(
            showcase_fields.get("slot_id") or showcase_fields.get("slug") or ""
        ).strip()
        if is_v4_python_slot(slot_id):
            concepts = showcase_fields.get("expected_concept_ids")
            if concepts:
                payload = dict(payload)
                payload["expected_concept_ids"] = list(concepts)
                curriculum = dict(payload.get("curriculum") or {})
                curriculum["expected_concept_ids"] = list(concepts)
                payload["curriculum"] = curriculum

    if (
        showcase_fields
        and _showcase_fields_need_catalog_refresh(showcase_fields)
        and not teacher_override
        and is_catalog_sync_enabled()
    ):
        from application.tasks.services.teacher_assembly_preservation import (
            should_skip_catalog_assembly_refresh,
        )

        if not should_skip_catalog_assembly_refresh(payload):
            payload = apply_catalog_fields_to_task_payload(payload, showcase_fields)

    _attach_transfer_pitfall_meta(payload, showcase_fields)

    return enrich_pascal_showcase_hints(payload)
