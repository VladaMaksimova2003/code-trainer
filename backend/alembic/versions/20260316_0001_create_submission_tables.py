"""create submission tables

Revision ID: 20260316_0001
Revises: None
Create Date: 2026-03-16 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260316_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "submission",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_submission_task_id", "submission", ["task_id"], unique=False)

    op.create_table(
        "submission_lint_error",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("submission.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("error_type", sa.String(length=64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_submission_lint_error_submission_id",
        "submission_lint_error",
        ["submission_id"],
        unique=False,
    )

    op.create_table(
        "submission_pattern_error",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("submission.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("error_type", sa.String(length=64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_submission_pattern_error_submission_id",
        "submission_pattern_error",
        ["submission_id"],
        unique=False,
    )

    op.create_table(
        "submission_test_result",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("submission.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("case_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("inputs", sa.Text(), nullable=False, server_default=""),
        sa.Column("expected", sa.Text(), nullable=False, server_default=""),
        sa.Column("actual", sa.Text(), nullable=False, server_default=""),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index(
        "ix_submission_test_result_submission_id",
        "submission_test_result",
        ["submission_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_submission_test_result_submission_id", table_name="submission_test_result"
    )
    op.drop_table("submission_test_result")

    op.drop_index(
        "ix_submission_pattern_error_submission_id",
        table_name="submission_pattern_error",
    )
    op.drop_table("submission_pattern_error")

    op.drop_index(
        "ix_submission_lint_error_submission_id", table_name="submission_lint_error"
    )
    op.drop_table("submission_lint_error")

    op.drop_index("ix_submission_task_id", table_name="submission")
    op.drop_table("submission")
