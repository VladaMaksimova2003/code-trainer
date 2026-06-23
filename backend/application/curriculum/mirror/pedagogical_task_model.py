"""Canonical pedagogical task model — concept-centric unified showcase shape."""

from __future__ import annotations

from typing import Any

from application.curriculum.mirror.curriculum_slot_mirror import (
    canonical_title_for_slot,
    slot_language,
)
from application.curriculum.mirror.curriculum_slot_mirror_map import (
    PYTHON_ONLY_CHAPTERS,
    is_python_only_slot,
)

FORBIDDEN_TASK_FORMATS = frozenset({"сопоставление", "matching"})
FORBIDDEN_PRIMARY_ACTIONS = frozenset({"analyze"})

CHAPTER_CONCEPT_ID: dict[str, str] = {
    "program_skeleton": "program_entry",
    "program_entry": "program_entry",
    "typed_variables": "variables",
    "io": "input_output",
    "expressions": "arithmetic",
    "conditions": "conditions",
    "loops": "loops",
    "functions": "functions",
    "procedures": "parameters",
    "parameters": "parameters",
    "static_arrays": "arrays",
    "lists": "arrays",
    "dynamic_arrays": "dynamic_arrays",
    "dynamic_lists": "dynamic_arrays",
    "strings": "strings",
    "records": "records_struct",
    "mappings": "key_value_map",
    "files": "files",
    "units": "modules",
    "modules": "modules",
    "recursion": "recursion",
    "oop": "oop_basics",
    "error_handling": "exceptions",
    "comprehensions": "comprehension",
    "exceptions": "exceptions",
    "pro_python": "decorators",
    "advanced_python": "decorators",
    "advanced_python": "decorators",
    "typing_diagnostics": "typing_static",
    "pascal_pitfalls": "pitfalls",
    "python_pitfalls": "pitfalls",
    "compiler_diagnostics": "diagnostics",
    "python_diagnostics": "diagnostics",
    "capstones": "program_entry",
    "cpp_entry": "program_entry",
    "cpp_types": "variables",
    "cpp_io": "input_output",
    "cpp_expr": "arithmetic",
    "cpp_cond": "conditions",
    "cpp_loops": "loops",
    "cpp_functions": "functions",
    "cpp_params": "parameters",
    "cpp_arrays": "arrays",
    "cpp_vector": "dynamic_arrays",
    "cpp_string": "strings",
    "cpp_pointers": "reference_semantics",
    "cpp_files": "files",
    "cpp_headers": "modules",
    "cpp_recursion": "recursion",
    "cpp_oop": "oop_basics",
    "cpp_pitfalls": "pitfalls",
    "cpp_diagnostics": "diagnostics",
    "cpp_preprocessor": "preprocessor_directives",
    "cpp_templates": "templates",
    "cpp_enums": "enum_class",
    "cpp_stl_associative": "stl_containers",
    "cpp_stl_algorithms": "stl_algorithms",
    "cpp_move": "move_semantics",
    "cpp_exceptions": "exceptions",
    "cpp_capstones": "program_entry",
}

SLOT_PREFIX_CONCEPT_ID: dict[str, str] = {
    "psk": "program_entry",
    "pyk": "program_entry",
    "cpk": "program_entry",
    "typ": "variables",
    "pyt": "variables",
    "cpt": "variables",
    "io": "input_output",
    "pyi": "input_output",
    "cpi": "input_output",
    "exp": "arithmetic",
    "pye": "arithmetic",
    "cpe": "arithmetic",
    "cnd": "conditions",
    "pyc": "conditions",
    "cpc": "conditions",
    "lop": "loops",
    "pyl": "loops",
    "cpl": "loops",
    "fn": "functions",
    "pyf": "functions",
    "prc": "parameters",
    "pypr": "parameters",
    "cpfn": "functions",
    "cpp": "parameters",
    "arr": "arrays",
    "pya": "arrays",
    "cpa": "arrays",
    "dyn": "dynamic_arrays",
    "pyd": "dynamic_arrays",
    "cpd": "dynamic_arrays",
    "str": "strings",
    "pys": "strings",
    "cps": "strings",
    "cppt": "reference_semantics",
    "cppr": "preprocessor_directives",
    "cptpl": "templates",
    "cpen": "enum_class",
    "cpas": "stl_containers",
    "cpalg": "stl_algorithms",
    "cpmv": "move_semantics",
    "cpex": "exceptions",
    "cpcap": "program_entry",
    "cpfl": "files",
    "cpm": "modules",
    "cprc": "recursion",
    "cpo": "oop_basics",
    "cppit": "pitfalls",
    "cpdg": "diagnostics",
    "rec": "records_struct",
    "pyr": "key_value_map",
    "fil": "files",
    "pyfl": "files",
    "unt": "modules",
    "pym": "modules",
    "rcu": "recursion",
    "pyrc": "recursion",
    "oop": "oop_basics",
    "pyo": "oop_basics",
    "exc": "exceptions",
    "pyx": "exceptions",
    "pit": "pitfalls",
    "pypit": "pitfalls",
    "cdg": "diagnostics",
    "pydg": "diagnostics",
    "pycmp": "comprehension",
    "pyex": "exceptions",
    "pyp": "decorators",
    "pyadv": "decorators",
    "pytd": "typing_static",
}

PASCAL_ONLY_CONCEPTS = frozenset(
    {
        "begin_end_blocks",
        "setlength",
        "unit_system",
        "text_file_api",
        "variant_record",
        "set_operations",
        "subrange_type",
    }
)

PYTHON_ONLY_CONCEPTS = frozenset(
    {
        "comprehension",
        "decorators",
        "generators",
        "context_manager",
        "dataclass",
        "typing_static",
        "async_await",
        "indentation_errors",
        "for_else",
        "pattern_matching",
        "packages",
    }
)


def slot_prefix(slot_id: str) -> str:
    raw = str(slot_id or "").strip()
    if "_cap" in raw:
        return raw.split("_")[0]
    return raw.split("_")[0] if raw else ""


def concept_id_for_showcase(showcase: dict[str, Any], *, language: str | None = None) -> str | None:
    explicit = str(showcase.get("concept_id") or "").strip()
    if explicit:
        return explicit
    chapter = str(showcase.get("collection_key") or "").strip()
    if chapter and chapter in CHAPTER_CONCEPT_ID:
        return CHAPTER_CONCEPT_ID[chapter]
    slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
    prefix = slot_prefix(slug)
    if prefix in SLOT_PREFIX_CONCEPT_ID:
        return SLOT_PREFIX_CONCEPT_ID[prefix]
    return None


def _track_has_slug(track: dict[str, Any]) -> bool:
    return bool(str(track.get("slug") or track.get("slot_id") or "").strip())


def extract_track_fields(
    showcase: dict[str, Any],
    *,
    language: str | None = None,
) -> dict[str, Any]:
    from application.curriculum.mirror.pedagogical_task_store import (
        _TRACK_FIELD_KEYS,
        language_track,
    )

    slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
    lang = str(
        language
        or showcase.get("target_language")
        or showcase.get("language")
        or slot_language(slug)
        or ""
    ).strip().lower()
    if lang in {"pascal", "python", "cpp"}:
        embedded = language_track(showcase, lang)
        if embedded and _track_has_slug(embedded):
            track = dict(embedded)
            track.setdefault("slug", slug or embedded.get("slug"))
            track.setdefault("slot_id", track.get("slot_id") or track.get("slug"))
            track.setdefault("target_language", lang)
            track.setdefault("language", lang)
            concept = concept_id_for_showcase(track, language=lang)
            if concept:
                track.setdefault("concept_id", concept)
            return track

    track: dict[str, Any] = {}
    for key in _TRACK_FIELD_KEYS:
        if key in showcase:
            track[key] = showcase[key]
    if slug:
        track.setdefault("slug", slug)
        track.setdefault("slot_id", slug)
    if lang:
        track.setdefault("target_language", lang)
        track.setdefault("language", lang)
    concept = concept_id_for_showcase(showcase, language=lang)
    if concept:
        track.setdefault("concept_id", concept)
    return track


def available_language_tracks(showcase: dict[str, Any]) -> list[str]:
    from application.curriculum.content.algo_syntax_task_extra import is_algo_syntax_slot

    ped = str(showcase.get("pedagogical_slot_id") or "").strip()
    slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
    if is_algo_syntax_slot(ped) or is_algo_syntax_slot(slug):
        return sorted({"pascal", "python", "cpp", "csharp", "java"})

    tracks = showcase.get("language_tracks")
    if isinstance(tracks, dict) and tracks:
        langs = []
        for key in tracks:
            lang = str(key).strip()
            if not lang:
                continue
            track = tracks.get(key)
            if isinstance(track, dict) and _track_has_slug(track):
                langs.append(lang)
        if langs:
            return sorted(langs)
    lang = str(
        showcase.get("target_language")
        or slot_language(str(showcase.get("slug") or ""))
        or ""
    ).strip().lower()
    return [lang] if lang in {"pascal", "python", "cpp", "csharp", "java"} else []


def is_universal_core_showcase(showcase: dict[str, Any]) -> bool:
    tracks = available_language_tracks(showcase)
    return "pascal" in tracks and "python" in tracks


def is_group_c_showcase(showcase: dict[str, Any]) -> bool:
    tracks = available_language_tracks(showcase)
    if len(tracks) <= 1:
        slug = str(showcase.get("slug") or showcase.get("slot_id") or "").strip()
        if is_python_only_slot(slug):
            return True
        chapter = str(showcase.get("collection_key") or "").strip()
        if chapter in PYTHON_ONLY_CHAPTERS:
            return True
        concept = concept_id_for_showcase(showcase)
        if concept in PASCAL_ONLY_CONCEPTS | PYTHON_ONLY_CONCEPTS:
            return True
    return False


def neutral_title_for_showcase(showcase: dict[str, Any]) -> str | None:
    ped = str(showcase.get("pedagogical_slot_id") or "").strip()
    if ped:
        title = canonical_title_for_slot(ped)
        if title:
            return title
    for lang in available_language_tracks(showcase):
        track = (showcase.get("language_tracks") or {}).get(lang) or {}
        slug = str(track.get("slug") or "").strip()
        title = canonical_title_for_slot(slug)
        if title:
            return title
    slug = str(showcase.get("slug") or "").strip()
    return canonical_title_for_slot(slug)


def normalize_unified_showcase(showcase: dict[str, Any]) -> dict[str, Any]:
    """Ensure pedagogical_slot_id, concept_id, language_tracks, and Pascal-primary overlay."""
    from application.curriculum.mirror.pedagogical_task_store import (
        canonical_pedagogical_slot_id,
        merge_language_track,
        pedagogical_slot_id_from_showcase,
    )

    merged = dict(showcase)
    raw_tracks = dict(merged.get("language_tracks") or {})
    tracks = {
        str(lang): dict(track)
        for lang, track in raw_tracks.items()
        if isinstance(track, dict) and _track_has_slug(track)
    }

    legacy_lang = str(
        merged.get("target_language")
        or slot_language(str(merged.get("slug") or ""))
        or "pascal"
    ).strip().lower()
    if legacy_lang in {"pascal", "python"} and legacy_lang not in tracks:
        tracks[legacy_lang] = extract_track_fields(merged)
        merged = merge_language_track(merged, tracks[legacy_lang], legacy_lang)

    ped_id = pedagogical_slot_id_from_showcase(merged)
    if ped_id:
        merged["pedagogical_slot_id"] = ped_id
    elif tracks:
        for lang, track in tracks.items():
            candidate = canonical_pedagogical_slot_id(
                slot_id=str(track.get("slug") or track.get("slot_id") or ""),
                slug=str(track.get("slug") or ""),
                language=str(lang),
            )
            if candidate:
                merged["pedagogical_slot_id"] = candidate
                break

    normalized_tracks: dict[str, dict[str, Any]] = {}
    for lang, track in tracks.items():
        if not isinstance(track, dict):
            continue
        item = dict(track)
        item.setdefault("target_language", lang)
        item.setdefault("language", lang)
        concept = concept_id_for_showcase(item, language=str(lang))
        if concept:
            item.setdefault("concept_id", concept)
        normalized_tracks[str(lang)] = item
    merged["language_tracks"] = normalized_tracks

    pascal_track = normalized_tracks.get("pascal")
    if pascal_track:
        for key, value in pascal_track.items():
            merged[key] = value
        merged["target_language"] = "pascal"
    elif normalized_tracks:
        first_lang = sorted(normalized_tracks.keys())[0]
        for key, value in normalized_tracks[first_lang].items():
            merged[key] = value
        merged["target_language"] = first_lang

    concept = concept_id_for_showcase(merged)
    if concept:
        merged["concept_id"] = concept

    return merged


def merge_showcase_pair(
    pascal_showcase: dict[str, Any],
    python_showcase: dict[str, Any],
    *,
    pedagogical_slot_id: str,
) -> dict[str, Any]:
    from application.curriculum.mirror.pedagogical_task_store import merge_language_track

    pascal_track = extract_track_fields(pascal_showcase, language="pascal")
    python_track = extract_track_fields(python_showcase, language="python")
    if not pascal_track.get("slug"):
        pascal_track["slug"] = pedagogical_slot_id
    merged: dict[str, Any] = {"pedagogical_slot_id": pedagogical_slot_id}
    merged = merge_language_track(merged, pascal_track, "pascal")
    merged = merge_language_track(merged, python_track, "python")
    return normalize_unified_showcase(merged)


def copy_language_code_examples(source: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    """Merge starter/reference keys from source code_examples into target."""
    src = dict(source or {})
    dst = dict(target or {})
    for key, value in src.items():
        if key == "curriculum_showcase":
            continue
        if key in {"pascal", "python", "python_reference", "cpp", "java", "csharp"}:
            dst[key] = value
        elif key in {"mcq_options", "mcq_correct_index", "patterns"}:
            dst[key] = value
        elif str(key).startswith("python") and key not in dst:
            dst[key] = value
    return dst
