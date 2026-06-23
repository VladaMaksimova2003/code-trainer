"""Create support_ticket, support_ticket_message, in_app_notification tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260605_0011"
down_revision: Union[str, None] = "20260604_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_support_ticket_category = sa.Enum(
    "task_content",
    "autograder",
    "technical",
    "account",
    "other",
    name="support_ticket_category_enum",
)
_support_ticket_status = sa.Enum(
    "open",
    "in_progress",
    "resolved",
    "closed",
    name="support_ticket_status_enum",
)
_support_ticket_target = sa.Enum(
    "teacher",
    "admin",
    name="support_ticket_target_enum",
)
_support_ticket_message_type = sa.Enum(
    "user",
    "system",
    name="support_ticket_message_type_enum",
)
_notification_kind = sa.Enum(
    "ticket_created",
    "ticket_reply",
    "ticket_status",
    name="notification_kind_enum",
)


def upgrade() -> None:
    _support_ticket_category.create(op.get_bind(), checkfirst=True)
    _support_ticket_status.create(op.get_bind(), checkfirst=True)
    _support_ticket_target.create(op.get_bind(), checkfirst=True)
    _support_ticket_message_type.create(op.get_bind(), checkfirst=True)
    _notification_kind.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "support_ticket",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("category", _support_ticket_category, nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("status", _support_ticket_status, nullable=False, server_default="open"),
        sa.Column("target", _support_ticket_target, nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("submission_id", sa.Integer(), nullable=True),
        sa.Column("context_json", sa.JSON(), nullable=True),
        sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("escalated_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assignee_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["submission_id"], ["submission.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["escalated_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_support_ticket_author_id"), "support_ticket", ["author_id"])
    op.create_index(op.f("ix_support_ticket_category"), "support_ticket", ["category"])
    op.create_index(op.f("ix_support_ticket_status"), "support_ticket", ["status"])
    op.create_index(op.f("ix_support_ticket_target"), "support_ticket", ["target"])
    op.create_index(op.f("ix_support_ticket_assignee_id"), "support_ticket", ["assignee_id"])
    op.create_index(op.f("ix_support_ticket_task_id"), "support_ticket", ["task_id"])
    op.create_index(op.f("ix_support_ticket_submission_id"), "support_ticket", ["submission_id"])

    op.create_table(
        "support_ticket_message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "message_type",
            _support_ticket_message_type,
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["ticket_id"], ["support_ticket.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_support_ticket_message_ticket_id"),
        "support_ticket_message",
        ["ticket_id"],
    )
    op.create_index(
        op.f("ix_support_ticket_message_author_id"),
        "support_ticket_message",
        ["author_id"],
    )

    op.create_table(
        "in_app_notification",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=True),
        sa.Column("kind", _notification_kind, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.String(length=512), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ticket_id"], ["support_ticket.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_in_app_notification_user_id"), "in_app_notification", ["user_id"])
    op.create_index(op.f("ix_in_app_notification_ticket_id"), "in_app_notification", ["ticket_id"])
    op.create_index(op.f("ix_in_app_notification_is_read"), "in_app_notification", ["is_read"])


def downgrade() -> None:
    op.drop_index(op.f("ix_in_app_notification_is_read"), table_name="in_app_notification")
    op.drop_index(op.f("ix_in_app_notification_ticket_id"), table_name="in_app_notification")
    op.drop_index(op.f("ix_in_app_notification_user_id"), table_name="in_app_notification")
    op.drop_table("in_app_notification")

    op.drop_index(op.f("ix_support_ticket_message_author_id"), table_name="support_ticket_message")
    op.drop_index(op.f("ix_support_ticket_message_ticket_id"), table_name="support_ticket_message")
    op.drop_table("support_ticket_message")

    op.drop_index(op.f("ix_support_ticket_submission_id"), table_name="support_ticket")
    op.drop_index(op.f("ix_support_ticket_task_id"), table_name="support_ticket")
    op.drop_index(op.f("ix_support_ticket_assignee_id"), table_name="support_ticket")
    op.drop_index(op.f("ix_support_ticket_target"), table_name="support_ticket")
    op.drop_index(op.f("ix_support_ticket_status"), table_name="support_ticket")
    op.drop_index(op.f("ix_support_ticket_category"), table_name="support_ticket")
    op.drop_index(op.f("ix_support_ticket_author_id"), table_name="support_ticket")
    op.drop_table("support_ticket")

    _notification_kind.drop(op.get_bind(), checkfirst=True)
    _support_ticket_message_type.drop(op.get_bind(), checkfirst=True)
    _support_ticket_target.drop(op.get_bind(), checkfirst=True)
    _support_ticket_status.drop(op.get_bind(), checkfirst=True)
    _support_ticket_category.drop(op.get_bind(), checkfirst=True)
