"""Per-slot expected pedagogical concepts for Pascal v3.1.1 tasks.

Each task gets an explicit ``expected_concept_ids`` list at catalog build time.
Teacher reference code (C++/Python) is analyzed first; manual overrides win.
"""

from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path

from application.curriculum.display.pascal_tc_pedagogy import PEDAGOGY_CARDS

_SCRIPTS = Path(__file__).resolve().parents[4] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from application.curriculum.pascal.catalog.pascal_v311_capstone_catalog import (
    capstone_expected_concepts,
    capstone_known_code,
)

_SHORT_FEATURE_KEYWORDS = frozenset({"do", "to", "of", "or", "if", "in", "mod"})
_SLOT_CONCEPT_KEYWORDS: dict[str, list[str]] = {
    "program_entry": ["program"],
    "block_scope": ["begin", "end"],
    "typed_declaration": ["var", "const", "integer", "real", "boolean", "char", "string", "type"],
    "assignment": [":=", "присваива"],
    "arithmetic_ops": ["+", "-", "*", "/", "div", "mod", "арифм"],
    "stdin_read": ["readln", "read", "ввод"],
    "stdout_write": ["writeln", "write", "вывод", "format"],
    "simple_branch": ["if", "then", "else", "условие", "ветвл"],
    "multi_branch": ["else if", "elseif", "elsif", "вложен", "несколько"],
    "switch_selection": ["case", "of", "вариант"],
    "conditional_expression": ["тернар"],
    "counted_loop": ["for", "to", "downto"],
    "pre_condition_loop": ["while", "do"],
    "post_condition_loop": ["repeat", "until"],
    "loop_control": ["break", "continue", "exit", "управление"],
    "nested_iteration": ["вложен", "nested"],
    "collection_iteration": ["array", "массив"],
    "function_definition": ["function", "функц"],
    "parameter_passing": ["procedure", "параметр"],
    "return_flow": ["result", "return"],
    "function_invocation": ["вызов", "invoke"],
    "indexed_sequence": ["array", "массив", "индекс"],
    "dynamic_array": ["setlength", "dynamic", "динамич"],
    "string_sequence": ["string", "строка", "length", "copy"],
    "key_value_map": ["record", "запись", "field"],
    "file_read": ["file", "assign", "reset", "rewrite", "файл"],
    "import_dependency": ["unit", "uses", "модуль"],
    "unit_definition": ["unit", "interface", "implementation"],
    "recursion": ["рекурс", "recursion"],
    "class_type": ["class", "object", "oop", "класс"],
}

_BRANCH_GROUP = frozenset(
    {"simple_branch", "multi_branch", "switch_selection", "conditional_expression"}
)
_LOOP_GROUP = frozenset({"counted_loop", "pre_condition_loop", "post_condition_loop"})

SLOT_EXPECTED_CONCEPT_OVERRIDES: dict[str, list[str]] = {

    "pas_001": ["program_entry", "stdout_write"],
    "pas_002": ["typed_declaration", "stdout_write", "assignment"],
    "pas_003": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_004": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_005": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_006": ["typed_declaration", "stdout_write", "assignment"],
    "pas_007": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration"],
    "pas_008": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_009": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_010": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_011": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_012": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration"],
    "pas_013": ["typed_declaration", "stdin_read", "stdout_write", "arithmetic_ops"],
    "pas_014": ["typed_declaration", "stdin_read", "stdout_write", "string_sequence"],
    "pas_015": ["typed_declaration", "stdin_read", "stdout_write", "arithmetic_ops"],
    "pas_016": ["typed_declaration", "stdin_read", "stdout_write", "arithmetic_ops"],
    "pas_017": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_018": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_019": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops"],
    "pas_020": ["typed_declaration", "stdin_read", "stdout_write", "arithmetic_ops"],
    "pas_021": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration"],
    "pas_022": ["typed_declaration", "stdin_read", "stdout_write", "arithmetic_ops", "string_sequence"],
    "pas_023": ["typed_declaration", "stdin_read", "stdout_write", "arithmetic_ops", "collection_iteration"],
    "pas_024": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration"],
    "pas_025": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_026": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch"],
    "pas_027": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_028": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_029": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_030": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_031": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "simple_branch", "string_sequence"],
    "pas_032": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_033": ["typed_declaration", "stdin_read", "stdout_write", "arithmetic_ops", "simple_branch"],
    "pas_034": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_035": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_036": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_037": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_038": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "simple_branch"],
    "pas_039": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_040": ["typed_declaration", "stdin_read", "stdout_write", "multi_branch", "switch_selection"],
    "pas_041": ["typed_declaration", "stdin_read", "stdout_write", "multi_branch", "switch_selection"],
    "pas_042": ["typed_declaration", "stdin_read", "stdout_write", "multi_branch", "switch_selection"],
    "pas_043": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_044": ["readln", "end"],
    "pas_045": ["typed_declaration", "stdin_read", "stdout_write", "multi_branch", "switch_selection"],
    "pas_046": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_047": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_048": ["typed_declaration", "stdin_read", "stdout_write", "simple_branch"],
    "pas_049": ["typed_declaration", "stdin_read", "stdout_write", "multi_branch", "switch_selection"],
    "pas_050": ["typed_declaration", "stdin_read", "stdout_write", "multi_branch", "switch_selection"],
    "pas_051": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_052": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_053": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_054": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_055": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_056": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_057": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_058": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_059": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_060": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_061": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_062": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_063": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop"],
    "pas_064": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop"],
    "pas_065": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_066": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_067": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_068": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_069": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_070": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_071": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_072": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_073": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_074": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_075": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop"],
    "pas_076": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_077": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_078": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration"],
    "pas_079": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_080": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_081": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_082": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_083": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_084": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_085": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_086": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_087": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_088": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_089": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_090": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_091": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_092": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_093": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_094": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence"],
    "pas_095": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_096": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_097": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_098": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_099": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_100": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_101": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_102": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_103": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_104": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_105": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_106": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_107": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_108": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "counted_loop", "nested_iteration", "indexed_sequence", "dynamic_array", "string_sequence"],
    "pas_109": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_110": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_111": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_112": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_113": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_114": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_115": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_116": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_117": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_118": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_119": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_120": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_121": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_122": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "key_value_map"],
    "pas_123": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_124": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_125": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_126": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_127": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_128": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_129": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_130": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_131": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_132": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_133": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_134": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_135": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_136": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_137": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_138": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_139": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_140": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_141": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_142": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_143": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_144": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_145": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_146": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_147": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_148": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "collection_iteration", "function_definition", "parameter_passing", "recursion"],
    "pas_149": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_150": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_151": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_152": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_153": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_154": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_155": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_156": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_157": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_158": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_159": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_160": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_161": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_162": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_163": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_164": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_165": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_166": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_167": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_168": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_169": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_170": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_171": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_172": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_173": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_174": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_175": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_176": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "nested_iteration", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_177": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_178": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_179": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_180": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_181": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select", "key_value_map"],
    "pas_182": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select", "key_value_map"],
    "pas_183": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select", "key_value_map"],
    "pas_184": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select", "key_value_map"],
    "pas_185": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_186": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_187": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_188": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select", "key_value_map"],
    "pas_189": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_190": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_191": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_192": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_193": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_194": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_195": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_196": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_197": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_198": ["typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops", "pre_condition_loop", "string_sequence", "file_read", "file_write"],
    "pas_199": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_200": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_201": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_202": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_203": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_204": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_205": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_206": ["import_dependency", "module_namespace", "typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "function_definition", "function_invocation", "parameter_passing", "recursion", "inheritance_hierarchy"],
    "pas_207": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "indexed_sequence", "stack_queue"],
    "pas_208": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "indexed_sequence", "stack_queue"],
    "pas_209": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "indexed_sequence", "stack_queue"],
    "pas_210": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "indexed_sequence", "stack_queue"],
    "pas_211": ["typed_declaration", "stdout_write", "assignment", "key_value_map", "linked_node"],
    "pas_212": ["typed_declaration", "stdout_write", "assignment", "key_value_map", "linked_node"],
    "pas_213": ["typed_declaration", "stdout_write", "assignment", "key_value_map", "linked_node"],
    "pas_214": ["typed_declaration", "stdout_write", "assignment", "key_value_map", "linked_node"],
    "pas_215": ["typed_declaration", "stdout_write", "assignment", "key_value_map", "linked_node"],
    "pas_216": ["typed_declaration", "stdout_write", "assignment", "key_value_map", "linked_node"],
    "pas_217": ["typed_declaration", "stdout_write", "assignment", "indexed_sequence", "string_sequence"],
    "pas_218": ["typed_declaration", "stdout_write", "assignment", "indexed_sequence", "string_sequence"],
    "pas_219": ["typed_declaration", "stdout_write", "assignment", "indexed_sequence", "string_sequence"],
    "pas_220": ["typed_declaration", "stdout_write", "assignment", "indexed_sequence", "string_sequence"],
    "pas_221": ["typed_declaration", "stdout_write", "assignment", "indexed_sequence", "string_sequence"],
    "pas_222": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_223": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_224": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_225": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_226": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_227": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_228": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_229": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_230": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_231": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_232": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_233": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_234": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_235": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_236": ["typed_declaration", "stdout_write", "assignment", "arithmetic_ops", "simple_branch", "counted_loop", "indexed_sequence", "string_sequence", "filter_select"],
    "pas_237": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_238": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_239": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_240": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_241": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_242": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_243": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_244": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_245": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_246": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_247": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_248": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_249": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_250": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_251": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_252": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_253": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_254": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_255": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_256": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_257": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_258": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_259": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_260": ["typed_declaration", "assignment", "arithmetic_ops", "collection_iteration", "string_sequence", "function_definition", "function_invocation", "parameter_passing", "recursion", "class_type", "method_dispatch"],
    "pas_261": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_262": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_263": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_264": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_265": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_266": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_267": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_268": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_269": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],
    "pas_270": ["typed_declaration", "assignment", "function_definition", "function_invocation", "parameter_passing", "class_type", "inheritance_hierarchy"],

}
from application.curriculum.pascal.catalog.pascal_v32_delta_content import V32_EXPECTED_CONCEPT_OVERRIDES

SLOT_EXPECTED_CONCEPT_OVERRIDES.update(V32_EXPECTED_CONCEPT_OVERRIDES)
SLOT_EXPECTED_CONCEPT_OVERRIDES.update(capstone_expected_concepts())

from pascal_v31_tasks import V31_TASKS  # noqa: E402


def _matches_concept(concept_id: str, feat_lower: str) -> bool:
    keywords = _SLOT_CONCEPT_KEYWORDS.get(concept_id, [])
    for kw in keywords:
        if kw in _SHORT_FEATURE_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", feat_lower):
                return True
        elif kw in feat_lower:
            return True
    return False


def _pick_exclusive(
    group: frozenset[str],
    matched: set[str],
    *,
    chapter_key: str,
    feat_lower: str,
    chapter_tc: dict[str, str],
) -> str | None:
    in_group = [cid for cid in matched if cid in group]
    if not in_group:
        return None
    if len(in_group) == 1:
        return in_group[0]

    primary = chapter_tc.get(chapter_key, "")
    if primary in in_group:
        return primary

    if group is _BRANCH_GROUP:
        if "case" in feat_lower or " of " in feat_lower:
            return "switch_selection" if "switch_selection" in in_group else in_group[0]
        if any(kw in feat_lower for kw in ("else if", "elseif", "elsif", "вложен")):
            return "multi_branch" if "multi_branch" in in_group else in_group[0]
        if "тернар" in feat_lower:
            return "conditional_expression" if "conditional_expression" in in_group else in_group[0]
        return "simple_branch" if "simple_branch" in in_group else in_group[0]

    if group is _LOOP_GROUP:
        if "repeat" in feat_lower or "until" in feat_lower:
            return "post_condition_loop" if "post_condition_loop" in in_group else in_group[0]
        if "while" in feat_lower:
            return "pre_condition_loop" if "pre_condition_loop" in in_group else in_group[0]
        if "for" in feat_lower or "to" in feat_lower or "downto" in feat_lower:
            return "counted_loop" if "counted_loop" in in_group else in_group[0]
        return in_group[0]

    return in_group[0]


def _concepts_from_teacher_code(slot_id: str, chapter_key: str) -> list[str]:
    from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import CHAPTER_TC
    from application.curriculum.pascal.catalog.pascal_v311_known_code import get_known_code
    from application.curriculum.display.pascal_tc_detection import resolve_technical_concepts

    known = get_known_code(slot_id)
    if not known:
        return []
    py, cpp, java, csharp = known
    primary = CHAPTER_TC.get(chapter_key, "")
    payload = {
        "code_examples": {
            "python": {"source_code": py},
            "cpp": {"source_code": cpp},
            "java": {"source_code": java},
            "csharp": {"source_code": csharp},
        }
    }
    try:
        detected = resolve_technical_concepts(
            primary_tc=primary,
            task_payload=payload,
            source_language="cpp",
        )
    except Exception:
        return []
    return [cid for cid in detected if cid in PEDAGOGY_CARDS]


def _derive_from_features(
    *,
    chapter_key: str,
    pascal_features: str,
    chapter_tc: dict[str, str],
) -> list[str]:
    feat_lower = (pascal_features or "").lower()
    matched = {
        cid
        for cid in _SLOT_CONCEPT_KEYWORDS
        if cid in PEDAGOGY_CARDS and _matches_concept(cid, feat_lower)
    }

    resolved = set(matched)
    for group in (_BRANCH_GROUP, _LOOP_GROUP):
        pick = _pick_exclusive(
            group,
            matched,
            chapter_key=chapter_key,
            feat_lower=feat_lower,
            chapter_tc=chapter_tc,
        )
        if pick:
            for cid in group:
                if cid in resolved and cid != pick:
                    resolved.discard(cid)

    primary = chapter_tc.get(chapter_key, "")
    ordered: list[str] = []
    seen: set[str] = set()

    def add(cid: str) -> None:
        if cid in resolved and cid not in seen:
            seen.add(cid)
            ordered.append(cid)

    if primary in resolved:
        add(primary)
    for cid in sorted(resolved - seen):
        add(cid)

    if not ordered and primary in PEDAGOGY_CARDS:
        return [primary]
    return ordered


def derive_expected_concept_ids(
    *,
    slot_id: str,
    chapter_key: str,
    pascal_features: str,
    task_format: str = "",
    chapter_tc: dict[str, str] | None = None,
) -> list[str]:
    if slot_id in SLOT_EXPECTED_CONCEPT_OVERRIDES:
        concepts = list(SLOT_EXPECTED_CONCEPT_OVERRIDES[slot_id])
    else:
        if chapter_tc is None:
            from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import CHAPTER_TC

            chapter_tc = CHAPTER_TC

        from_teacher = _concepts_from_teacher_code(slot_id, chapter_key)
        from_features = _derive_from_features(
            chapter_key=chapter_key,
            pascal_features=pascal_features,
            chapter_tc=chapter_tc,
        )
        if from_teacher:
            concepts = list(from_teacher)
            for cid in from_features:
                if cid not in concepts:
                    concepts.append(cid)
        else:
            concepts = from_features

    if task_format in {"сборка_фрагмента", "перевод_фрагмента"}:
        concepts = [cid for cid in concepts if cid != "program_entry"]
    return concepts


@lru_cache(maxsize=1)
def expected_concepts_by_slot() -> dict[str, list[str]]:
    from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import CHAPTER_TC

    mapping: dict[str, list[str]] = {}
    for row in V31_TASKS:
        slot_id, chapter, _title, task_format, *_rest = row
        features = row[7]
        mapping[slot_id] = derive_expected_concept_ids(
            slot_id=slot_id,
            chapter_key=chapter,
            pascal_features=features,
            task_format=task_format,
            chapter_tc=CHAPTER_TC,
        )
    return mapping


def expected_concept_ids_for_row(
    *,
    slot_id: str,
    chapter_key: str,
    pascal_features: str,
    task_format: str = "",
) -> list[str]:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_expected_concepts,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        concepts = algo_expected_concepts(slot_id, "pascal")
        if concepts:
            return concepts
    cached = expected_concepts_by_slot().get(slot_id)
    if cached is not None:
        return list(cached)
    return derive_expected_concept_ids(
        slot_id=slot_id,
        chapter_key=chapter_key,
        pascal_features=pascal_features,
        task_format=task_format,
    )
