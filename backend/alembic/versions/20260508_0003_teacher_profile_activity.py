"""Teacher profile and teacher activity tables.

Revision ID: 20260508_0003
Revises: 20260318_0002
Create Date: 2026-05-08

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260508_0003"
down_revision: Union[str, None] = "20260318_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teacher_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("full_name", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("languages", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "teacher_activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("action_type", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_teacher_activity_teacher_occurred",
        "teacher_activity",
        ["teacher_id", "occurred_at"],
        unique=False,
    )

    op.execute(
        sa.text("""
            INSERT INTO teacher_activity (teacher_id, occurred_at, action_type)
            SELECT teacher_id, COALESCE(created_at, CURRENT_TIMESTAMP), 'created_task'
            FROM task
            WHERE teacher_id IS NOT NULL
            AND NOT is_delete
        """)
    )


def downgrade() -> None:
    op.drop_index("ix_teacher_activity_teacher_occurred", table_name="teacher_activity")
    op.drop_table("teacher_activity")
    op.drop_table("teacher_profile")
