import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from application.curriculum.content.v4_code_format import format_reference_code
from application.curriculum.validation.expected_concept_checker import (
    concept_present_in_code,
    prune_expected_concepts_for_code,
)

mod = importlib.import_module("ch2_user_codes.task_014")
code = format_reference_code(mod.FIXED_PASCAL, "pascal")
print("switch", concept_present_in_code(code, "switch_selection", language="pascal"))
print("multi", concept_present_in_code(code, "multi_branch", language="pascal"))
concepts = [
    "program_entry",
    "typed_declaration",
    "stdin_read",
    "stdout_write",
    "switch_selection",
]
print("pruned", prune_expected_concepts_for_code(concepts, code, "pascal"))
print("---CODE---")
print(repr(code))
