"""Normalize assignment task_type values (legacy -> canonical)

Revision ID: 20260514_0009
Revises: 20260513_0008
Create Date: 2026-05-14

"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260514_0009"
down_revision: Union[str, None] = "20260513_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE task SET task_type = 'task_build_from_blocks' "
        "WHERE task_type IN ('block_reorder', 'code_assembly')"
    )
    op.execute(
        "UPDATE task SET task_type = 'task_translate_full_program' "
        "WHERE task_type = 'translation'"
    )
    op.execute(
        "UPDATE task SET task_type = 'task_flowchart_to_code' "
        "WHERE task_type = 'diagram'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE task SET task_type = 'block_reorder' "
        "WHERE task_type = 'task_build_from_blocks'"
    )
    op.execute(
        "UPDATE task SET task_type = 'translation' "
        "WHERE task_type IN ('task_translate_snippet', 'task_translate_full_program')"
    )
    op.execute(
        "UPDATE task SET task_type = 'diagram' "
        "WHERE task_type = 'task_flowchart_to_code'"
    )
