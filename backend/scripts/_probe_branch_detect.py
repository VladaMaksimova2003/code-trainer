import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from application.curriculum.content.v4_code_format import format_reference_code
from application.curriculum.validation.expected_concept_checker import (
    concept_present_in_code,
    detect_expected_concepts_in_code,
)
from application.curriculum.validation.technical_concept_detector import detect_technical_concepts

for pid in ("task_010", "task_012", "task_014"):
    mod = importlib.import_module(f"ch2_user_codes.{pid}")
    kind = "debug" if pid in {"task_011", "task_012", "task_013", "task_014", "task_015"} else "assemble"
    for lang in ("pascal", "python"):
        if kind == "debug":
            attr = {"pascal": "FIXED_PASCAL", "python": "FIXED_PYTHON"}[lang]
        else:
            attr = {"pascal": "PASCAL", "python": "PYTHON"}[lang]
        code = format_reference_code(getattr(mod, attr), lang)
        det = detect_technical_concepts(code, lang)
        print(pid, lang, "technical=", sorted(det.technical_ids))
        print("  multi", concept_present_in_code(code, "multi_branch", language=lang))
        print("  simple", concept_present_in_code(code, "simple_branch", language=lang))
        print("  switch", concept_present_in_code(code, "switch_selection", language=lang))
        print("  arith", concept_present_in_code(code, "arithmetic_ops", language=lang))
        print("  display", detect_expected_concepts_in_code(code, language=lang))
