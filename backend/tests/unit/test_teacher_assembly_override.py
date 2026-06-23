"""Tests — teacher assembly override skips curriculum catalog refresh."""

from __future__ import annotations

from application.tasks.use_cases.block_reorder.get import _refresh_curriculum_assembly_variants


class _FakeTask:
    def __init__(self, *, override: bool) -> None:
        self.code_examples = {
            "teacher_assembly_override": override,
            "curriculum_showcase": {
                "slot_id": "pas_001",
                "task_format": "блоки с плейсхолдерами",
                "primary_action": "assemble",
            },
        }
        self.block_reorder_task = None


def test_refresh_skipped_when_teacher_override_flag_set():
    task = _FakeTask(override=True)
    payload = {
        "language_variants": {
            "pascal": {
                "template": "begin {0} end.",
                "blocks": ["writeln(1);"],
                "correct_order": [0],
            }
        },
        "template": "begin {0} end.",
    }
    _refresh_curriculum_assembly_variants(task, payload)
    assert payload["language_variants"]["pascal"]["template"] == "begin {0} end."
