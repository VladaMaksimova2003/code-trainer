"""User profile fields, learning preferences, teacher visibility

Revision ID: 20260513_0008
Revises: 20260512_0007
Create Date: 2026-05-13

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260513_0008"
down_revision: Union[str, None] = "20260512_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("avatar_url", sa.String(length=512), nullable=True))
    op.add_column("user", sa.Column("about", sa.Text(), nullable=True))

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("preferred_languages", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "preferred_difficulty",
            sa.String(length=32),
            nullable=False,
            server_default="beginner",
        ),
        sa.Column("preferred_topics", sa.JSON(), nullable=False, server_default="[]"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.add_column(
        "teacher_profile",
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("teacher_profile", "is_public")
    op.drop_table("user_preferences")
    op.drop_column("user", "about")
    op.drop_column("user", "avatar_url")
