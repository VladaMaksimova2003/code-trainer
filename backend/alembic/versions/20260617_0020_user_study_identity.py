"""Add study_place and study_group to user_preferences."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260617_0020"
down_revision = "20260616_0019"
branch_labels = None
depends_on = None


def _user_preference_columns() -> set[str]:
    bind = op.get_bind()
    inspector = inspect(bind)
    return {col["name"] for col in inspector.get_columns("user_preferences")}


def upgrade() -> None:
    columns = _user_preference_columns()
    if "study_place" not in columns:
        op.add_column(
            "user_preferences",
            sa.Column("study_place", sa.String(length=255), nullable=True),
        )
    if "study_group" not in columns:
        op.add_column(
            "user_preferences",
            sa.Column("study_group", sa.String(length=128), nullable=True),
        )


def downgrade() -> None:
    columns = _user_preference_columns()
    if "study_group" in columns:
        op.drop_column("user_preferences", "study_group")
    if "study_place" in columns:
        op.drop_column("user_preferences", "study_place")
