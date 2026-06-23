"""Sync task.id PostgreSQL sequence after explicit-id seed inserts."""

from typing import Sequence, Union

from alembic import op

revision: str = "20260611_0014"
down_revision: Union[str, None] = "20260611_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
DO $$
DECLARE
    seq_name text;
BEGIN
    seq_name := pg_get_serial_sequence('task', 'id');
    IF seq_name IS NOT NULL THEN
        EXECUTE format(
            'SELECT setval(%L, COALESCE((SELECT MAX(id) FROM task), 0))',
            seq_name
        );
    END IF;
END
$$;
"""
    )


def downgrade() -> None:
    pass
