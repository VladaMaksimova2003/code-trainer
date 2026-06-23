"""Pascal canonical slot ↔ C++ track slug mapping (Universal Core extension)."""

from __future__ import annotations

from application.curriculum.mirror.curriculum_slot_mirror_map import (
    PASCAL_SLOTS_WITHOUT_STRICT_PYTHON_MIRROR,
)

PASCAL_TO_CPP_PREFIX: dict[str, str] = {
    "psk": "cpk",
    "typ": "cpt",
    "io": "cpi",
    "exp": "cpe",
    "cnd": "cpc",
    "lop": "cpl",
    "fn": "cpfn",
    "prc": "cpp",
    "arr": "cpa",
    "dyn": "cpd",
    "str": "cps",
    "rec": "cpr",
    "fil": "cpfl",
    "unt": "cpm",
    "rcu": "cprc",
    "oop": "cpo",
    "exc": "cpex",
    "pit": "cppit",
    "cdg": "cpdg",
}

CPP_TO_PASCAL_PREFIX: dict[str, str] = {value: key for key, value in PASCAL_TO_CPP_PREFIX.items()}

# Explicit overrides where suffix numbering diverges (mirror Python strict map style).
STRICT_EXPLICIT_PASCAL_TO_CPP: dict[str, str] = {
    "psk_09": "cpk_08",
    "psk_12": "cpk_10",
    "typ_06": "cpt_06",
    "typ_09": "cpt_09",
    "typ_10": "cpt_10",
}

# Pascal slots without a C++ track (language-specific or deferred).
PASCAL_SLOTS_WITHOUT_CPP_MIRROR: frozenset[str] = frozenset({
    *PASCAL_SLOTS_WITHOUT_STRICT_PYTHON_MIRROR,
    "typ_07",  # subrange — C++ uses size_t / validation separately
    "exp_04",  # set of — no Pascal-equivalent in C++ core
})

# C++-only pedagogical slots (Group C) — own task row, no Pascal mirror.
CPP_ONLY_SLOTS: frozenset[str] = frozenset({
    "cpk_12",
    "cpk_13",
    "cpk_14",
    "cpt_14",
    "cpt_15",
    "cpi_10",
    "cpe_10",
    "cpe_11",
    # MVP-2 Group C
    "cpc_15",
    "cpc_16",
    "cpc_17",
    "cpl_15",
    "cpl_16",
    "cpfn_15",
    "cpfn_16",
    "cpfn_17",
    "cpp_15",
    "cpp_16",
    "cpp_17",
    # MVP-3 Group C
    "cpa_15",
    "cpa_16",
    "cpa_17",
    "cpd_15",
    "cpd_16",
    "cpd_17",
    "cps_15",
    "cps_16",
    "cps_17",
    "cppt_01",
    "cppt_02",
    "cppt_03",
    "cppt_04",
    "cppt_05",
    "cppt_06",
    "cppt_07",
    "cppt_08",
    "cppt_09",
    "cppt_10",
    "cppt_11",
    "cppt_12",
    "cppt_13",
    "cppt_14",
    "cppt_15",
    "cppt_16",
    # v1-full Group C
    "cpfl_15",
    "cpfl_16",
    "cpm_15",
    "cpm_16",
    "cpm_17",
    "cprc_15",
    "cpo_15",
    "cpo_18",
    "cpo_19",
    "cpo_20",
    "cppit_20",
    "cppit_21",
    "cppit_22",
    "cppit_23",
    "cppit_24",
    "cppit_25",
    "cpdg_15",
    "cpdg_16",
    "cpdg_17",
    # v1.1 Group C
    "cppr_01",
    "cppr_02",
    "cppr_03",
    "cppr_04",
    "cppr_05",
    "cppr_06",
    "cptpl_01",
    "cptpl_02",
    "cptpl_03",
    "cptpl_04",
    "cptpl_05",
    "cptpl_06",
    "cptpl_07",
    "cptpl_08",
    "cptpl_09",
    "cptpl_10",
    "cptpl_11",
    "cptpl_12",
    "cpen_01",
    "cpen_02",
    "cpen_03",
    "cpen_04",
    "cpen_05",
    "cpas_01",
    "cpas_02",
    "cpas_03",
    "cpas_04",
    "cpas_05",
    "cpas_06",
    "cpas_07",
    "cpas_08",
    "cpas_09",
    "cpas_10",
    "cpalg_01",
    "cpalg_02",
    "cpalg_03",
    "cpalg_04",
    "cpalg_05",
    "cpalg_06",
    "cpalg_07",
    "cpalg_08",
    "cpmv_01",
    "cpmv_02",
    "cpmv_03",
    "cpmv_04",
    "cpmv_05",
    "cpmv_06",
    "cpmv_07",
    # capstones Group C
    "cpcap_01",
    "cpcap_02",
    "cpcap_03",
    "cpcap_04",
    "cpcap_05",
    "cpcap_06",
    "cpcap_07",
    "cpcap_08",
})

CPP_ONLY_CHAPTERS: frozenset[str] = frozenset({
    "cpp_pointers",
    "cpp_preprocessor",
    "cpp_templates",
    "cpp_enums",
    "cpp_stl_associative",
    "cpp_stl_algorithms",
    "cpp_move",
})

PASCAL_CHAPTER_TO_CPP: dict[str, str] = {
    "program_skeleton": "cpp_entry",
    "typed_variables": "cpp_types",
    "io": "cpp_io",
    "expressions": "cpp_expr",
    "conditions": "cpp_cond",
    "loops": "cpp_loops",
    "functions": "cpp_functions",
    "procedures": "cpp_params",
    "static_arrays": "cpp_arrays",
    "dynamic_arrays": "cpp_vector",
    "strings": "cpp_string",
    "records": "cpp_struct",
    "files": "cpp_files",
    "units": "cpp_headers",
    "recursion": "cpp_recursion",
    "oop": "cpp_oop",
    "pascal_pitfalls": "cpp_pitfalls",
    "compiler_diagnostics": "cpp_diagnostics",
    "error_handling": "cpp_exceptions",
}

CPP_CHAPTER_TO_PASCAL: dict[str, str] = {v: k for k, v in PASCAL_CHAPTER_TO_CPP.items()}

MVP_STAGES: dict[str, tuple[str, ...]] = {
    "MVP-1": ("cpp_entry", "cpp_types", "cpp_io", "cpp_expr"),
    "MVP-2": ("cpp_cond", "cpp_loops", "cpp_functions", "cpp_params"),
    "MVP-3": ("cpp_arrays", "cpp_vector", "cpp_string", "cpp_pointers"),
    "v1-full": (
        "cpp_files",
        "cpp_headers",
        "cpp_recursion",
        "cpp_oop",
        "cpp_pitfalls",
        "cpp_diagnostics",
    ),
    "v1.1": (
        "cpp_pointers",
        "cpp_preprocessor",
        "cpp_templates",
        "cpp_enums",
        "cpp_stl_associative",
        "cpp_stl_algorithms",
        "cpp_move",
    ),
    "v1.2": (
        "cpp_exceptions",
        "cpp_capstones",
    ),
}


def all_cpp_chapters() -> tuple[str, ...]:
    from application.curriculum.cpp.showcase.cpp_v311_registry import V311_CHAPTER_ORDER

    return V311_CHAPTER_ORDER


def _split_slot_id(slot_id: str) -> tuple[str, str] | None:
    if "_" not in slot_id:
        return None
    prefix, suffix = slot_id.split("_", 1)
    if not prefix or not suffix:
        return None
    return prefix, suffix


def is_cpp_only_slot(slot_id: str) -> bool:
    return str(slot_id or "").strip() in CPP_ONLY_SLOTS


def pascal_to_cpp_slot(pascal_slot_id: str) -> str | None:
    pas = str(pascal_slot_id or "").strip()
    if not pas or pas in PASCAL_SLOTS_WITHOUT_CPP_MIRROR:
        return None
    explicit = STRICT_EXPLICIT_PASCAL_TO_CPP.get(pas)
    if explicit:
        return explicit
    parts = _split_slot_id(pas)
    if not parts:
        return None
    prefix, suffix = parts
    cpp_prefix = PASCAL_TO_CPP_PREFIX.get(prefix)
    if not cpp_prefix:
        return None
    return f"{cpp_prefix}_{suffix}"


def cpp_to_pascal_slot(cpp_slot_id: str) -> str | None:
    cpp = str(cpp_slot_id or "").strip()
    if not cpp or cpp in CPP_ONLY_SLOTS:
        return None
    for pas, mapped in STRICT_EXPLICIT_PASCAL_TO_CPP.items():
        if mapped == cpp:
            return pas
    parts = _split_slot_id(cpp)
    if not parts:
        return None
    prefix, suffix = parts
    pas_prefix = CPP_TO_PASCAL_PREFIX.get(prefix)
    if not pas_prefix:
        return None
    return f"{pas_prefix}_{suffix}"


def mirror_chapter_to_cpp(pascal_chapter: str) -> str | None:
    return PASCAL_CHAPTER_TO_CPP.get(str(pascal_chapter or "").strip())


def mirror_chapter_from_cpp(cpp_chapter: str) -> str | None:
    return CPP_CHAPTER_TO_PASCAL.get(str(cpp_chapter or "").strip())


def chapters_for_stage(stage: str) -> tuple[str, ...]:
    key = str(stage or "").strip()
    if key in {"all", "full", "v1.2-full"}:
        return all_cpp_chapters()
    if key not in MVP_STAGES:
        raise ValueError(f"Unknown C++ stage: {stage!r}")
    return MVP_STAGES[key]
