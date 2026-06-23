"""Add submission_checked notification kind and task/submission refs on notifications."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260606_0012"
down_revision: Union[str, None] = "20260605_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table)}


def upgrade() -> None:
    if "task_id" not in _column_names("in_app_notification"):
        op.add_column("in_app_notification", sa.Column("task_id", sa.Integer(), nullable=True))
    if "submission_id" not in _column_names("in_app_notification"):
        op.add_column("in_app_notification", sa.Column("submission_id", sa.Integer(), nullable=True))

    op.execute("ALTER TABLE in_app_notification ALTER COLUMN kind TYPE varchar(32)")

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    fk_names = {fk["name"] for fk in inspector.get_foreign_keys("in_app_notification")}
    if "fk_in_app_notification_submission_id" not in fk_names:
        op.create_foreign_key(
            "fk_in_app_notification_submission_id",
            "in_app_notification",
            "submission",
            ["submission_id"],
            ["id"],
            ondelete="SET NULL",
        )

    index_names = {index["name"] for index in inspector.get_indexes("in_app_notification")}
    task_index = op.f("ix_in_app_notification_task_id")
    submission_index = op.f("ix_in_app_notification_submission_id")
    if task_index not in index_names:
        op.create_index(task_index, "in_app_notification", ["task_id"])
    if submission_index not in index_names:
        op.create_index(submission_index, "in_app_notification", ["submission_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_in_app_notification_submission_id"), table_name="in_app_notification")
    op.drop_index(op.f("ix_in_app_notification_task_id"), table_name="in_app_notification")
    op.drop_constraint(
        "fk_in_app_notification_submission_id",
        "in_app_notification",
        type_="foreignkey",
    )
    op.drop_column("in_app_notification", "submission_id")
    op.drop_column("in_app_notification", "task_id")
