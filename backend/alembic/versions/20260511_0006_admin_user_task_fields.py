"""Admin: user moderation fields, task workflow, task_version snapshots

Revision ID: 20260511_0006
Revises: 20260510_0005
Create Date: 2026-05-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260511_0006"
down_revision: Union[str, None] = "20260510_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("is_blocked", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "user",
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "user",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.add_column(
        "task",
        sa.Column(
            "workflow_status",
            sa.String(length=32),
            server_default="active",
            nullable=False,
        ),
    )

    op.create_table(
        "task_version",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(length=32), nullable=False),
        sa.Column("task_type", sa.String(length=32), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_version_task_id", "task_version", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_task_version_task_id", table_name="task_version")
    op.drop_table("task_version")
    op.drop_column("task", "workflow_status")
    op.drop_column("user", "created_at")
    op.drop_column("user", "is_deleted")
    op.drop_column("user", "is_blocked")
