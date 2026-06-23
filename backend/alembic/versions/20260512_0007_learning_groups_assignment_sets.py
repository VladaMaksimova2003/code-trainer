"""Learning: groups, invitation codes, assignment set visibility, task visibility

Revision ID: 20260512_0007
Revises: 20260511_0006
Create Date: 2026-05-12

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260512_0007"
down_revision: Union[str, None] = "20260511_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "group",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.add_column(
        "collections",
        sa.Column("visibility", sa.String(length=16), server_default="private", nullable=False),
    )
    op.add_column("collections", sa.Column("group_id", sa.Integer(), nullable=True))
    op.add_column(
        "collections",
        sa.Column("is_archived", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "collections",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_collections_group_id",
        "collections",
        "group",
        ["group_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "collection_task_association",
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "collection_task_association",
        sa.Column("topic", sa.String(length=128), nullable=True),
    )

    op.add_column(
        "task",
        sa.Column("visibility", sa.String(length=16), server_default="public", nullable=False),
    )

    op.add_column(
        "teacher_profile",
        sa.Column("specialization", sa.String(length=256), nullable=True),
    )

    op.create_table(
        "invitation_code",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("use_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["group_id"], ["group.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teacher_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_invitation_code_code", "invitation_code", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_invitation_code_code", table_name="invitation_code")
    op.drop_table("invitation_code")
    op.drop_column("teacher_profile", "specialization")
    op.drop_column("task", "visibility")
    op.drop_column("collection_task_association", "topic")
    op.drop_column("collection_task_association", "sort_order")
    op.drop_constraint("fk_collections_group_id", "collections", type_="foreignkey")
    op.drop_column("collections", "created_at")
    op.drop_column("collections", "is_archived")
    op.drop_column("collections", "group_id")
    op.drop_column("collections", "visibility")
    op.drop_column("group", "created_at")
