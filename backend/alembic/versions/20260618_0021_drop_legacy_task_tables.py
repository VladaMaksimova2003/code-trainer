"""Migrate diagram_task rows into task.flow_spec; drop legacy task tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

revision = "20260618_0021"
down_revision = "20260617_0020"
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    bind = op.get_bind()
    return set(inspect(bind).get_table_names())


def upgrade() -> None:
    tables = _table_names()

    if "diagram_task" in tables and "task" in tables:
        op.execute(
            text(
                """
                UPDATE task AS t
                SET flow_spec = COALESCE(t.flow_spec, '{}'::json)::jsonb
                    || jsonb_build_object(
                        'nodes', COALESCE(d.diagram->'nodes', '[]'::jsonb),
                        'edges', COALESCE(d.diagram->'edges', '[]'::jsonb),
                        'flow', COALESCE(d.diagram->'flow', '[]'::jsonb)
                    )
                FROM diagram_task AS d
                WHERE d.task_id = t.id
                  AND (
                    t.flow_spec IS NULL
                    OR NOT COALESCE(t.flow_spec, '{}'::json)::jsonb ? 'nodes'
                  )
                """
            )
        )
        op.drop_table("diagram_task")

    if "algorithm_task" in tables and "task" in tables:
        op.execute(
            text(
                """
                UPDATE task AS t
                SET test_cases = COALESCE(t.test_cases, '[]'::json)::jsonb
                    || COALESCE(a.tests, '[]'::json)::jsonb
                FROM algorithm_task AS a
                WHERE a.task_id = t.id
                  AND (
                    t.test_cases IS NULL
                    OR t.test_cases = '[]'::json
                    OR t.test_cases = '[]'::jsonb
                  )
                  AND a.tests IS NOT NULL
                """
            )
        )
        op.execute(
            text(
                """
                UPDATE task AS t
                SET description = COALESCE(NULLIF(t.description, ''), a.algorithm_hint)
                FROM algorithm_task AS a
                WHERE a.task_id = t.id
                  AND a.algorithm_hint IS NOT NULL
                  AND (t.description IS NULL OR t.description = '')
                """
            )
        )
        op.drop_table("algorithm_task")


def downgrade() -> None:
    op.create_table(
        "algorithm_task",
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task.id", ondelete="CASCADE")),
        sa.Column("tests", sa.JSON(), nullable=False),
        sa.Column("algorithm_hint", sa.Text(), nullable=True),
    )
    op.create_table(
        "diagram_task",
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task.id", ondelete="CASCADE")),
        sa.Column("diagram", sa.JSON(), nullable=False),
    )
