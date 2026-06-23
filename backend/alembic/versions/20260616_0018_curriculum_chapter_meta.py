"""Create curriculum_chapter_meta table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260616_0018"
down_revision = "20260613_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "curriculum_chapter_meta" in inspect(bind).get_table_names():
        return

    op.create_table(
        "curriculum_chapter_meta",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("language", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("chapter_key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("language", "chapter_key", name="uq_curriculum_chapter_meta_lang_key"),
    )
    op.create_index("ix_curriculum_chapter_meta_chapter_key", "curriculum_chapter_meta", ["chapter_key"])


def downgrade() -> None:
    op.drop_index("ix_curriculum_chapter_meta_chapter_key", table_name="curriculum_chapter_meta")
    op.drop_table("curriculum_chapter_meta")
