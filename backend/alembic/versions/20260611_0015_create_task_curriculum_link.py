"""Create task_curriculum_link table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_0015"
down_revision: Union[str, None] = "20260611_0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "task_curriculum_link",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("learning_concept_id", sa.String(length=64), nullable=False),
        sa.Column("technical_concept_id", sa.String(length=64), nullable=False),
        sa.Column("exercise_pattern_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "task_id",
            "exercise_pattern_id",
            name="uq_task_curriculum_link_task_pattern",
        ),
    )
    op.create_index(
        "ix_task_curriculum_link_task_id",
        "task_curriculum_link",
        ["task_id"],
    )
    op.create_index(
        "uq_task_curriculum_link_primary",
        "task_curriculum_link",
        ["task_id"],
        unique=True,
        postgresql_where=sa.text("is_primary = true"),
        sqlite_where=sa.text("is_primary = 1"),
    )


def downgrade() -> None:
    op.drop_index("uq_task_curriculum_link_primary", table_name="task_curriculum_link")
    op.drop_index("ix_task_curriculum_link_task_id", table_name="task_curriculum_link")
    op.drop_table("task_curriculum_link")
