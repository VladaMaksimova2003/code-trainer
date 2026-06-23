"""Add template column to block_reorder_task

Revision ID: 20260318_0002
Revises: 20260317_0001
Create Date: 2026-03-18 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260318_0002"
down_revision: Union[str, None] = "20260317_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("block_reorder_task", sa.Column("template", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("block_reorder_task", "template")
