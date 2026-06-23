"""Create student_curriculum_progress table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_0016"
down_revision: Union[str, None] = "20260611_0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "student_curriculum_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("learning_concept_id", sa.String(length=64), nullable=False),
        sa.Column("technical_concept_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("exercise_pattern_id", sa.String(length=128), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_status", sa.String(length=16), nullable=True),
        sa.Column("last_submission_id", sa.Integer(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_passed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["last_submission_id"], ["submission.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "task_id",
            name="uq_student_curriculum_progress_user_task",
        ),
    )
    op.create_index(
        "ix_student_curriculum_progress_user_lc",
        "student_curriculum_progress",
        ["user_id", "language", "learning_concept_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_student_curriculum_progress_user_lc",
        table_name="student_curriculum_progress",
    )
    op.drop_table("student_curriculum_progress")
