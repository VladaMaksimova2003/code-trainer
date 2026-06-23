"""MPLT pattern bindings — authoritative Stage 1 (methodology approved).

Each pattern has exactly one of:
  - transfer_category TCC (no dominant_pitfall_id, no debug_id);
  - dominant_pitfall_id → ATCC | FCC | AFCC;
  - debug_id → AlgorithmDebug (transfer_category remains TCC).

Runtime resolver wiring: Stage 2.
"""

from __future__ import annotations

from typing import Any, TypedDict


class MpltPatternBinding(TypedDict):
    dominant_pitfall_id: str | None
    debug_id: str | None
    transfer_category: str


MPLT_PATTERN_BINDINGS: dict[str, MpltPatternBinding] = {
    "task_001": {"dominant_pitfall_id": "for_range_off_by_one", "debug_id": None, "transfer_category": "ATCC"},
    "task_002": {"dominant_pitfall_id": "input_line_model", "debug_id": None, "transfer_category": "AFCC"},
    "task_003": {"dominant_pitfall_id": "for_range_off_by_one", "debug_id": None, "transfer_category": "ATCC"},
    "task_004": {"dominant_pitfall_id": None, "debug_id": "filter_positive", "transfer_category": "TCC"},
    "task_005": {"dominant_pitfall_id": "for_range_off_by_one", "debug_id": None, "transfer_category": "ATCC"},
    "task_006": {"dominant_pitfall_id": "integer_division", "debug_id": None, "transfer_category": "FCC"},
    "task_007": {"dominant_pitfall_id": None, "debug_id": "threshold_count", "transfer_category": "TCC"},
    "task_008": {"dominant_pitfall_id": "integer_division", "debug_id": None, "transfer_category": "FCC"},
    "task_009": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_010": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_011": {"dominant_pitfall_id": "elif_chain", "debug_id": "branch_logic", "transfer_category": "TCC"},
    "task_012": {"dominant_pitfall_id": None, "debug_id": 'branch_logic', "transfer_category": "TCC"},
    "task_013": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_014": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_015": {"dominant_pitfall_id": None, "debug_id": 'multi_branch_discount', "transfer_category": "TCC"},
    "task_016": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_017": {"dominant_pitfall_id": "while_sentinel", "debug_id": None, "transfer_category": "ATCC"},
    "task_018": {"dominant_pitfall_id": "search_first_guard", "debug_id": None, "transfer_category": "FCC"},
    "task_019": {"dominant_pitfall_id": "yes_no_output", "debug_id": None, "transfer_category": "AFCC"},
    "task_020": {"dominant_pitfall_id": "filter_non_negative", "debug_id": None, "transfer_category": "FCC"},
    "task_021": {"dominant_pitfall_id": "loop_upper_bound_n", "debug_id": None, "transfer_category": "ATCC"},
    "task_022": {"dominant_pitfall_id": "search_last_overwrite", "debug_id": None, "transfer_category": "FCC"},
    "task_023": {"dominant_pitfall_id": "frequency_bucket", "debug_id": None, "transfer_category": "AFCC"},
    "task_024": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_025": {"dominant_pitfall_id": "array_reverse_order", "debug_id": None, "transfer_category": "ATCC"},
    "task_026": {"dominant_pitfall_id": "cyclic_shift_mod_k", "debug_id": None, "transfer_category": "AFCC"},
    "task_027": {"dominant_pitfall_id": "array_delete_shift", "debug_id": None, "transfer_category": "FCC"},
    "task_028": {"dominant_pitfall_id": "array_insert_shift", "debug_id": None, "transfer_category": "FCC"},
    "task_029": {"dominant_pitfall_id": "dual_array_concat", "debug_id": None, "transfer_category": "AFCC"},
    "task_030": {"dominant_pitfall_id": "duplicate_pair_loop", "debug_id": None, "transfer_category": "FCC"},
    "task_031": {"dominant_pitfall_id": "merge_sorted_two_ptr", "debug_id": None, "transfer_category": "AFCC"},
    "task_032": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_033": {"dominant_pitfall_id": "string_length_builtin", "debug_id": None, "transfer_category": "ATCC"},
    "task_034": {"dominant_pitfall_id": "string_reverse_chars", "debug_id": None, "transfer_category": "ATCC"},
    "task_035": {"dominant_pitfall_id": "palindrome_symmetry", "debug_id": None, "transfer_category": "AFCC"},
    "task_036": {"dominant_pitfall_id": "substring_first_1based", "debug_id": None, "transfer_category": "FCC"},
    "task_037": {"dominant_pitfall_id": "word_split_spaces", "debug_id": None, "transfer_category": "AFCC"},
    "task_038": {"dominant_pitfall_id": "anagram_letter_freq", "debug_id": None, "transfer_category": "FCC"},
    "task_039": {"dominant_pitfall_id": "rle_run_encoding", "debug_id": None, "transfer_category": "AFCC"},
    "task_040": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_041": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_042": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_043": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_044": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_045": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_046": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_047": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_048": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_049": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_050": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_051": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_052": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_053": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_054": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_055": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_056": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_057": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_058": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_059": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_060": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_061": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_062": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_063": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_064": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_065": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_066": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_067": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_068": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_069": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_070": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_071": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_072": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_073": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_074": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_075": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_076": {"dominant_pitfall_id": None, "debug_id": 'map_key_missing', "transfer_category": "TCC"},
    "task_077": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_078": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_079": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_080": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_081": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_082": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_083": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_084": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_085": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_086": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_087": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_088": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_089": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_090": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_091": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_092": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_093": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_094": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_095": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_096": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_097": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_098": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_099": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_100": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_101": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_102": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_103": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_104": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_105": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_106": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_107": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_108": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_109": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_110": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_111": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_112": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_113": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_114": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_115": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_116": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_117": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_118": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_119": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_120": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_121": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_122": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_123": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_124": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_125": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_126": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_127": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_128": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_129": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_130": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_131": {"dominant_pitfall_id": 'integer_division', "debug_id": None, "transfer_category": "FCC"},
    "task_132": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_133": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_134": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_135": {"dominant_pitfall_id": 'chain_comparison', "debug_id": None, "transfer_category": "FCC"},
    "task_136": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_137": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_138": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_139": {"dominant_pitfall_id": 'for_range_off_by_one', "debug_id": None, "transfer_category": "ATCC"},
    "task_140": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_141": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_142": {"dominant_pitfall_id": None, "debug_id": 'map_key_missing', "transfer_category": "TCC"},
    "task_143": {"dominant_pitfall_id": 'index_1based', "debug_id": None, "transfer_category": "FCC"},
    "task_144": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_145": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_146": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_147": {"dominant_pitfall_id": 'index_1based', "debug_id": None, "transfer_category": "FCC"},
    "task_148": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_149": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_150": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_151": {"dominant_pitfall_id": 'scope_block', "debug_id": None, "transfer_category": "ATCC"},
    "task_152": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_153": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_154": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_155": {"dominant_pitfall_id": 'for_range_off_by_one', "debug_id": None, "transfer_category": "ATCC"},
    "task_156": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_157": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_158": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_159": {"dominant_pitfall_id": 'index_1based', "debug_id": None, "transfer_category": "FCC"},
    "task_160": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_161": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_162": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_163": {"dominant_pitfall_id": 'round_semantics', "debug_id": None, "transfer_category": "AFCC"},
    "task_164": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_165": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_166": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_167": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_168": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_169": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_170": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_171": {"dominant_pitfall_id": 'file_text_mode', "debug_id": None, "transfer_category": "ATCC"},
    "task_172": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_173": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_174": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_175": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_176": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_177": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_178": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_179": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_180": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_181": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_182": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_183": {"dominant_pitfall_id": 'index_1based', "debug_id": None, "transfer_category": "FCC"},
    "task_184": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_185": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_186": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_187": {"dominant_pitfall_id": 'exception_model', "debug_id": None, "transfer_category": "ATCC"},
    "task_188": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_189": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_190": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_191": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
    "task_192": {"dominant_pitfall_id": None, "debug_id": None, "transfer_category": "TCC"},
}


def get_mplt_pattern_binding(pattern_id: str | None) -> MpltPatternBinding | None:
    key = str(pattern_id or "").strip()
    if not key:
        return None
    return MPLT_PATTERN_BINDINGS.get(key)


def list_patterns_by_transfer_category(category: str) -> list[str]:
    cat = str(category or "").strip().upper()
    return sorted(
        pat
        for pat, row in MPLT_PATTERN_BINDINGS.items()
        if str(row.get("transfer_category") or "").upper() == cat
    )


def list_patterns_with_dominant_pitfall() -> list[str]:
    return sorted(
        pat
        for pat, row in MPLT_PATTERN_BINDINGS.items()
        if row.get('dominant_pitfall_id')
    )


def list_patterns_with_debug_id() -> list[str]:
    return sorted(
        pat
        for pat, row in MPLT_PATTERN_BINDINGS.items()
        if row.get('debug_id')
    )


def binding_stats() -> dict[str, Any]:
    stats = {
        "total": len(MPLT_PATTERN_BINDINGS),
        "TCC": len(list_patterns_by_transfer_category("TCC")),
        "ATCC": len(list_patterns_by_transfer_category("ATCC")),
        "FCC": len(list_patterns_by_transfer_category("FCC")),
        "AFCC": len(list_patterns_by_transfer_category("AFCC")),
        "with_dominant_pitfall": len(list_patterns_with_dominant_pitfall()),
        "with_debug_id": len(list_patterns_with_debug_id()),
    }
    return stats

