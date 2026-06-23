"""Pedagogy-first slot mirror map — not naive suffix substitution."""

from __future__ import annotations

from application.curriculum.mirror.curriculum_slot_mirror import mirror_slot_id
from application.curriculum.mirror.curriculum_slot_mirror_map import (
    is_python_only_slot,
    pascal_to_python_slot,
    python_to_pascal_slot,
)


def test_typ_06_mirrors_pyt_08_not_pyt_06():
    assert pascal_to_python_slot("typ_06") == "pyt_08"
    assert python_to_pascal_slot("pyt_06") is None
    assert is_python_only_slot("pyt_06")


def test_typ_09_mirrors_pyt_10_trunc_round():
    assert pascal_to_python_slot("typ_09") == "pyt_10"
    assert python_to_pascal_slot("pyt_09") is None
    assert is_python_only_slot("pyt_09")


def test_exp_02_mirrors_pye_01_not_pye_02():
    assert pascal_to_python_slot("exp_02") == "pye_01"
    assert python_to_pascal_slot("pye_02") is None


def test_io_04_mirrors_pyi_03():
    assert pascal_to_python_slot("io_04") == "pyi_03"
    assert pascal_to_python_slot("io_05") == "pyi_04"


def test_fn_06_mirrors_pyf_08():
    assert pascal_to_python_slot("fn_06") == "pyf_08"


def test_lop_09_strict_mirror_pyl_08():
    from application.curriculum.mirror.curriculum_slot_mirror_map import (
        all_mirrored_pairs,
        strict_pascal_to_python_slot,
    )

    assert strict_pascal_to_python_slot("lop_09") == "pyl_08"
    assert all_mirrored_pairs()["lop_09"] == "pyl_08"


def test_lop_07_strict_mirror_pyl_05():
    from application.curriculum.mirror.curriculum_slot_mirror_map import (
        all_mirrored_pairs,
        strict_pascal_to_python_slot,
    )

    assert strict_pascal_to_python_slot("lop_07") == "pyl_05"
    assert all_mirrored_pairs()["lop_07"] == "pyl_05"


def test_lop_08_has_no_strict_python_mirror():
    from application.curriculum.mirror.curriculum_slot_mirror_map import all_mirrored_pairs

    assert "lop_08" not in all_mirrored_pairs()


def test_pit_cross_chapter_pairs_are_semantic_only():
    from application.curriculum.mirror.curriculum_slot_mirror_map import (
        all_mirrored_pairs,
        all_semantic_related_pairs,
        is_semantic_related_pair,
    )

    semantic = all_semantic_related_pairs()
    assert semantic["pit_03"] == "pys_03"
    assert semantic["pit_04"] == "pyl_14"
    assert is_semantic_related_pair("pit_01", "pypit_20")
    assert all_mirrored_pairs().get("pit_03") != "pys_03"


def test_python_only_none_has_no_pascal_mirror():
    assert is_python_only_slot("pyt_05")
    assert mirror_slot_id("pyt_05", target="pascal") is None
