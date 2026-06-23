"""Explicit Pascal v3.1.1 ↔ Python v1 slot alignment (pedagogy-first)."""

from __future__ import annotations

PASCAL_TO_PY_PREFIX: dict[str, str] = {
    "psk": "pyk",
    "typ": "pyt",
    "io": "pyi",
    "exp": "pye",
    "cnd": "pyc",
    "lop": "pyl",
    "fn": "pyf",
    "prc": "pypr",
    "arr": "pya",
    "dyn": "pyd",
    "str": "pys",
    "rec": "pyr",
    "fil": "pyfl",
    "unt": "pym",
    "rcu": "pyrc",
    "oop": "pyo",
    "exc": "pyx",
    "pit": "pypit",
    "cdg": "pydg",
}

PY_TO_PASCAL_PREFIX: dict[str, str] = {value: key for key, value in PASCAL_TO_PY_PREFIX.items()}

PYTHON_ONLY_CHAPTERS = frozenset({"comprehensions", "exceptions", "pro_python", "advanced_python", "typing_diagnostics", "capstones"})

# Type B — pedagogically related, different chapter/concept; NOT for Universal Core merge.
SEMANTIC_RELATED_PASCAL_TO_PYTHON: dict[str, str] = {
    # pitfalls ↔ tasks in other chapters (coverage audit only)
    "pit_01": "pypit_20",
    "pit_03": "pys_03",
    "pit_04": "pyl_14",
    "pit_12": "pypit_20",
    "pit_18": "pyd_10",
    "pit_22": "pyd_09",
    # loops ↔ strings / dynamic (cross-chapter)
    "lop_11": "pys_06",
    # records pointer semantics ↔ mappings mutation
    "rec_04": "pyr_06",
}

# Type A — strict mirror: one pedagogical_slot_id, merge into single DB task.
STRICT_EXPLICIT_PASCAL_TO_PYTHON: dict[str, str] = {
    # program_skeleton ↔ program_entry
    "psk_09": "pyk_08",
    "psk_12": "pyk_10",
    # typed_variables
    "typ_06": "pyt_08",
    "typ_07": "pyt_07",
    "typ_09": "pyt_10",
    "typ_10": "pyt_11",
    # io (gaps in numbering)
    "io_04": "pyi_03",
    "io_05": "pyi_04",
    # expressions
    "exp_02": "pye_01",
    "exp_06": "pye_06",
    "exp_08": "pye_08",
    # loops — override suffix (lop_07≠pyl_07, lop_08≠pyl_08 break/continue)
    "lop_07": "pyl_05",
    "lop_09": "pyl_08",
    # functions
    "fn_06": "pyf_08",
    "fn_08": "pyf_11",
    # diagnostics (1:1 chapter)
    "cdg_01": "pydg_01",
    "cdg_02": "pydg_02",
    "cdg_03": "pydg_03",
    "cdg_04": "pydg_04",
    "cdg_05": "pydg_05",
    "cdg_06": "pydg_06",
    "cdg_07": "pydg_07",
    "cdg_09": "pydg_08",
    "cdg_13": "pydg_11",
    "cdg_14": "pydg_12",
    "cdg_15": "pydg_09",
    # error_handling ↔ exceptions (explicit; suffix differs for some slots)
    "exc_01": "pyx_01",
    "exc_02": "pyx_02",
    "exc_03": "pyx_04",
    "exc_04": "pyx_09",
    "exc_05": "pyx_07",
    "exc_06": "pyx_05",
    "exc_07": "pyx_12",
    # pitfalls / diagnostics v3.2 delta
    "pit_05": "pypit_02",
    "pit_06": "pypit_06",
    "pit_20": "pypit_25",
    "cdg_08": "pydg_14",
    "cdg_10": "pydg_15",
    # oop property slots (Python v1.2 mirrors)
    "oop_19": "pyo_19",
    "oop_20": "pyo_20",
    "oop_21": "pyo_21",
}

# Pascal slots without a strict Python mirror (debug-only or language-specific).
PASCAL_SLOTS_WITHOUT_STRICT_PYTHON_MIRROR: frozenset[str] = frozenset({
    "lop_05",
    "lop_08",
    "lop_16",
    "fn_13",
    "dyn_12",
    "unt_14",
    "unt_15",
    "prc_14",
    "rec_12",
    "fil_09",
    "exc_08",
    "pit_02",  # nil-pointer debug; strict mirror is pit_05 ↔ pypit_02 only
})
EXPLICIT_PASCAL_TO_PYTHON: dict[str, str] = {
    **STRICT_EXPLICIT_PASCAL_TO_PYTHON,
    **SEMANTIC_RELATED_PASCAL_TO_PYTHON,
}

# Explicit python-only (no Pascal mirror) inside shared chapters.
PYTHON_ONLY_SLOTS: frozenset[str] = frozenset(
    {
        "pyt_05",
        "pyt_06",
        "pyt_09",
        "pye_02",
        "pye_03",
        "pye_04",
        "pye_05",
        "pye_07",
        "pyi_05",
        "pyi_09",
        "pyl_06",
        "pyl_07",
        "pyl_09",
        "pyl_10",
        "pyl_15",
        "pyf_04",
        "pyf_05",
        "pyf_06",
        "pyf_07",
        "pyf_09",
        "pyf_10",
        "pypr_14",
        "pya_11",
        "pyd_12",
        "pyd_13",
        "pys_08",
        "pyr_04",
        "pyfl_09",
        "pym_02",
        "pym_03",
        "pym_05",
        "pym_07",
        "pym_08",
        "pym_11",
        "pym_12",
        "pym_14",
        "pyrc_08",
        "pyo_15",
        "pyo_16",
        "pyo_17",
        "pyo_18",
        "pyc_04",
        "pyc_15",
        "pyk_07",
        "pyk_09",
        "pypit_23",
        "pypit_24",
    }
)

_SEMANTIC_PYTHON_SLOTS: frozenset[str] = frozenset(SEMANTIC_RELATED_PASCAL_TO_PYTHON.values())

_PASCAL_SLOTS: frozenset[str] | None = None
_PYTHON_SLOTS: frozenset[str] | None = None
_BUILT_STRICT_PAS_TO_PY: dict[str, str] | None = None
_BUILT_STRICT_PY_TO_PAS: dict[str, str] | None = None


def _catalog_slot_sets() -> tuple[frozenset[str], frozenset[str]]:
    global _PASCAL_SLOTS, _PYTHON_SLOTS
    if _PASCAL_SLOTS is None or _PYTHON_SLOTS is None:
        from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
            all_v311_task_records as pas_records,
        )
        from application.curriculum.python.catalog.python_curriculum_v3_catalog import (
            all_v311_task_records as py_records,
        )

        _PASCAL_SLOTS = frozenset(r.slot_id for r in pas_records())
        _PYTHON_SLOTS = frozenset(r.slot_id for r in py_records())
    return _PASCAL_SLOTS, _PYTHON_SLOTS


def _python_chapter_for_slot(slot_id: str) -> str | None:
    try:
        from application.curriculum.python.catalog.python_curriculum_v3_catalog import (
            all_v311_task_records as py_records,
        )

        for rec in py_records():
            if rec.slot_id == slot_id:
                return rec.chapter_key
    except Exception:
        pass
    return None


def _suffix_mirror_id(slot_id: str, *, target: str) -> str | None:
    if "_cap" in slot_id:
        cap = slot_id.rsplit("_cap", 1)[1]
        prefix = slot_id.split("_")[0]
        if prefix in PASCAL_TO_PY_PREFIX and target == "python":
            py_prefix = PASCAL_TO_PY_PREFIX[prefix]
            return f"{py_prefix}_cap{cap}"
        if prefix in PY_TO_PASCAL_PREFIX and target == "pascal":
            pas_prefix = PY_TO_PASCAL_PREFIX[prefix]
            return f"{pas_prefix}_cap{cap}"
        return None
    prefix = slot_id.split("_")[0]
    suffix = slot_id[len(prefix) :]
    if prefix in PASCAL_TO_PY_PREFIX and target == "python":
        return f"{PASCAL_TO_PY_PREFIX[prefix]}{suffix}"
    if prefix in PY_TO_PASCAL_PREFIX and target == "pascal":
        return f"{PY_TO_PASCAL_PREFIX[prefix]}{suffix}"
    return None


def _is_semantic_pascal_slot(pascal_slot_id: str) -> bool:
    return pascal_slot_id in SEMANTIC_RELATED_PASCAL_TO_PYTHON


def _build_strict_maps() -> tuple[dict[str, str], dict[str, str]]:
    global _BUILT_STRICT_PAS_TO_PY, _BUILT_STRICT_PY_TO_PAS
    if _BUILT_STRICT_PAS_TO_PY is not None and _BUILT_STRICT_PY_TO_PAS is not None:
        return _BUILT_STRICT_PAS_TO_PY, _BUILT_STRICT_PY_TO_PAS

    pas_slots, py_slots = _catalog_slot_sets()
    pas_to_py: dict[str, str] = dict(STRICT_EXPLICIT_PASCAL_TO_PYTHON)
    py_to_pas: dict[str, str] = {py: pas for pas, py in STRICT_EXPLICIT_PASCAL_TO_PYTHON.items()}

    for pas_id in sorted(pas_slots):
        if pas_id in pas_to_py or pas_id in PASCAL_SLOTS_WITHOUT_STRICT_PYTHON_MIRROR:
            continue
        if pas_id.startswith("cdg_"):
            continue
        candidate = _suffix_mirror_id(pas_id, target="python")
        if not candidate or candidate in PYTHON_ONLY_SLOTS:
            continue
        if candidate in _SEMANTIC_PYTHON_SLOTS:
            continue
        if candidate not in py_slots:
            continue
        chapter = _python_chapter_for_slot(candidate)
        if chapter in PYTHON_ONLY_CHAPTERS:
            continue
        existing_pas = py_to_pas.get(candidate)
        if existing_pas and existing_pas != pas_id:
            continue
        pas_to_py[pas_id] = candidate
        if candidate not in py_to_pas:
            py_to_pas[candidate] = pas_id

    _BUILT_STRICT_PAS_TO_PY = pas_to_py
    _BUILT_STRICT_PY_TO_PAS = py_to_pas
    return pas_to_py, py_to_pas


def all_semantic_related_pairs() -> dict[str, str]:
    """Type B pairs — coverage audit only, excluded from merge."""
    return dict(SEMANTIC_RELATED_PASCAL_TO_PYTHON)


def all_mirrored_pairs() -> dict[str, str]:
    """Type A strict mirror pairs — used by Universal Core merge."""
    pas_to_py, _ = _build_strict_maps()
    return dict(pas_to_py)


def pascal_to_python_slot(pascal_slot_id: str) -> str | None:
    pas_to_py, _ = _build_strict_maps()
    strict = pas_to_py.get(pascal_slot_id)
    if strict:
        return strict
    if _is_semantic_pascal_slot(pascal_slot_id):
        return SEMANTIC_RELATED_PASCAL_TO_PYTHON.get(pascal_slot_id)
    return None


def strict_pascal_to_python_slot(pascal_slot_id: str) -> str | None:
    pas_to_py, _ = _build_strict_maps()
    return pas_to_py.get(pascal_slot_id)


def strict_python_to_pascal_slot(python_slot_id: str) -> str | None:
    if python_slot_id in PYTHON_ONLY_SLOTS:
        return None
    chapter = _python_chapter_for_slot(python_slot_id)
    if chapter in PYTHON_ONLY_CHAPTERS:
        return None
    _, py_to_pas = _build_strict_maps()
    return py_to_pas.get(python_slot_id)


def python_to_pascal_slot(python_slot_id: str) -> str | None:
    if python_slot_id in _SEMANTIC_PYTHON_SLOTS:
        for pas, py in SEMANTIC_RELATED_PASCAL_TO_PYTHON.items():
            if py == python_slot_id:
                return pas
    if python_slot_id in PYTHON_ONLY_SLOTS:
        return None
    chapter = _python_chapter_for_slot(python_slot_id)
    if chapter in PYTHON_ONLY_CHAPTERS:
        return None
    _, py_to_pas = _build_strict_maps()
    return py_to_pas.get(python_slot_id)


def is_python_only_slot(slot_id: str) -> bool:
    if slot_id in PYTHON_ONLY_SLOTS:
        return True
    chapter = _python_chapter_for_slot(slot_id)
    if chapter in PYTHON_ONLY_CHAPTERS:
        return True
    _, py_to_pas = _build_strict_maps()
    if slot_id in py_to_pas:
        return False
    if not slot_id.startswith("py"):
        return False
    return True


def is_semantic_related_pair(pascal_slot_id: str, python_slot_id: str) -> bool:
    return SEMANTIC_RELATED_PASCAL_TO_PYTHON.get(pascal_slot_id) == python_slot_id


def reset_mirror_map_cache() -> None:
    """Clear cached strict maps (for tests after map edits)."""
    global _BUILT_STRICT_PAS_TO_PY, _BUILT_STRICT_PY_TO_PAS, _PASCAL_SLOTS, _PYTHON_SLOTS
    _BUILT_STRICT_PAS_TO_PY = None
    _BUILT_STRICT_PY_TO_PAS = None
    _PASCAL_SLOTS = None
    _PYTHON_SLOTS = None
