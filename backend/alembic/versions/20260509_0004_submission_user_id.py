"""Add student ownership to submissions

Revision ID: 20260509_0004
Revises: 20260508_0003
Create Date: 2026-05-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260509_0004"
down_revision: Union[str, None] = "20260508_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "submission",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_submission_user_id_user",
        "submission",
        "user",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_submission_user_id", "submission", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_submission_user_id", table_name="submission")
    op.drop_constraint("fk_submission_user_id_user", "submission", type_="foreignkey")
    op.drop_column("submission", "user_id")
