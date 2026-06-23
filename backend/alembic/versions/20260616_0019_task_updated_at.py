"""Add task.updated_at for teacher cabinet last-modified display."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260616_0019"
down_revision = "20260616_0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    task_columns = {col["name"] for col in inspect(bind).get_columns("task")}
    if "updated_at" in task_columns:
        return

    op.add_column(
        "task",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.execute(
        sa.text("UPDATE task SET updated_at = COALESCE(created_at, NOW()) WHERE updated_at IS NULL")
    )
    op.alter_column("task", "updated_at", nullable=False)


def downgrade() -> None:
    op.drop_column("task", "updated_at")
