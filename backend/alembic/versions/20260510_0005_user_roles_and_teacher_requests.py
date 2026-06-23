"""User roles (multi-role RBAC) and teacher role requests

Revision ID: 20260510_0005
Revises: 20260509_0004
Create Date: 2026-05-10

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260510_0005"
down_revision: Union[str, None] = "20260509_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role", name="uq_user_role_user_id_role"),
    )
    op.create_index("ix_user_role_user_id", "user_role", ["user_id"], unique=False)

    op.create_table(
        "teacher_role_request",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_teacher_role_request_user_id",
        "teacher_role_request",
        ["user_id"],
        unique=False,
    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO user_role (user_id, role)
            SELECT id, role FROM "user"
            WHERE NOT EXISTS (
                SELECT 1 FROM user_role ur WHERE ur.user_id = "user".id
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_teacher_role_request_user_id", table_name="teacher_role_request")
    op.drop_table("teacher_role_request")
    op.drop_index("ix_user_role_user_id", table_name="user_role")
    op.drop_table("user_role")
