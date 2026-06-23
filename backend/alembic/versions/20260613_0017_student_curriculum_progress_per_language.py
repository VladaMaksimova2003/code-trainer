"""Unique progress per user, task, and learning language."""

from typing import Sequence, Union

from alembic import op

revision: str = "20260613_0017"
down_revision: Union[str, None] = "20260611_0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_student_curriculum_progress_user_task",
        "student_curriculum_progress",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_student_curriculum_progress_user_task_lang",
        "student_curriculum_progress",
        ["user_id", "task_id", "language"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_student_curriculum_progress_user_task_lang",
        "student_curriculum_progress",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_student_curriculum_progress_user_task",
        "student_curriculum_progress",
        ["user_id", "task_id"],
    )
