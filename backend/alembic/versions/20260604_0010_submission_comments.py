"""Create submission_comment table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260604_0010"
down_revision: Union[str, None] = "20260514_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "submission_comment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["submission_id"], ["submission.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teacher_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_submission_comment_submission_id"),
        "submission_comment",
        ["submission_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_submission_comment_teacher_id"),
        "submission_comment",
        ["teacher_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_submission_comment_teacher_id"), table_name="submission_comment")
    op.drop_index(op.f("ix_submission_comment_submission_id"), table_name="submission_comment")
    op.drop_table("submission_comment")
