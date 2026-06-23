"""Idempotent DDL to match ORM when teams skip Alembic or use create_all-only DBs."""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def align_submission_user_id(engine: Engine) -> None:
    """
    When `submission` was created without `user_id` (legacy or old migration),
    `Base.metadata.create_all` will not add columns. Ensures PostgreSQL/SQLite
    have `submission.user_id` + FK/index consistent with Alembic 20260509_0004.
    """
    insp = inspect(engine)
    if "submission" not in insp.get_table_names():
        return

    colnames = [c["name"] for c in insp.get_columns("submission")]
    if "user_id" in colnames:
        return

    dialect = engine.dialect.name

    with engine.begin() as conn:
        if dialect == "postgresql":
            conn.execute(
                text("ALTER TABLE submission ADD COLUMN IF NOT EXISTS user_id INTEGER")
            )
            conn.execute(
                text("""
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE t.relname = 'submission'
          AND c.conname = 'fk_submission_user_id_user'
    ) THEN
        ALTER TABLE submission
        ADD CONSTRAINT fk_submission_user_id_user
        FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE SET NULL;
    END IF;
END $$;
""")
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_submission_user_id "
                    "ON submission (user_id)"
                )
            )
        elif dialect == "sqlite":
            conn.execute(text("ALTER TABLE submission ADD COLUMN user_id INTEGER"))
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_submission_user_id "
                    "ON submission (user_id)"
                )
            )


def align_admin_schema(engine: Engine) -> None:
    """Add admin moderation / workflow columns when DB was created via create_all only."""
    insp = inspect(engine)
    dialect = engine.dialect.name

    with engine.begin() as conn:
        if "user" in insp.get_table_names():
            user_cols = {c["name"] for c in insp.get_columns("user")}
            if dialect == "postgresql":
                if "is_blocked" not in user_cols:
                    conn.execute(
                        text(
                            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS '
                            "is_blocked BOOLEAN NOT NULL DEFAULT false"
                        )
                    )
                if "is_deleted" not in user_cols:
                    conn.execute(
                        text(
                            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS '
                            "is_deleted BOOLEAN NOT NULL DEFAULT false"
                        )
                    )
                if "created_at" not in user_cols:
                    conn.execute(
                        text(
                            'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS '
                            "created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP"
                        )
                    )
            elif dialect == "sqlite":
                if "is_blocked" not in user_cols:
                    conn.execute(
                        text(
                            'ALTER TABLE "user" ADD COLUMN is_blocked '
                            "BOOLEAN NOT NULL DEFAULT 0"
                        )
                    )
                if "is_deleted" not in user_cols:
                    conn.execute(
                        text(
                            'ALTER TABLE "user" ADD COLUMN is_deleted '
                            "BOOLEAN NOT NULL DEFAULT 0"
                        )
                    )
                if "created_at" not in user_cols:
                    conn.execute(
                        text(
                            'ALTER TABLE "user" ADD COLUMN created_at '
                            "DATETIME DEFAULT CURRENT_TIMESTAMP"
                        )
                    )

        if "task" in insp.get_table_names():
            task_cols = {c["name"] for c in insp.get_columns("task")}
            if "workflow_status" not in task_cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE task ADD COLUMN IF NOT EXISTS "
                            "workflow_status VARCHAR(32) NOT NULL DEFAULT 'active'"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text(
                            "ALTER TABLE task ADD COLUMN workflow_status "
                            "VARCHAR(32) NOT NULL DEFAULT 'active'"
                        )
                    )

        if "task_version" not in insp.get_table_names():
            if dialect == "postgresql":
                conn.execute(
                    text("""
CREATE TABLE IF NOT EXISTS task_version (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES task(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(32) NOT NULL,
    task_type VARCHAR(32) NOT NULL,
    snapshot JSON NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)
""")
                )
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS ix_task_version_task_id "
                        "ON task_version (task_id)"
                    )
                )
            elif dialect == "sqlite":
                conn.execute(
                    text("""
CREATE TABLE IF NOT EXISTS task_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES task(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(32) NOT NULL,
    task_type VARCHAR(32) NOT NULL,
    snapshot JSON NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
                )
                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS ix_task_version_task_id "
                        "ON task_version (task_id)"
                    )
                )


def align_learning_schema(engine: Engine) -> None:
    """Learning mode columns when Alembic was not applied."""
    insp = inspect(engine)
    dialect = engine.dialect.name

    with engine.begin() as conn:
        tables = insp.get_table_names()
        if "task" in tables:
            cols = {c["name"] for c in insp.get_columns("task")}
            if "visibility" not in cols:
                stmt = (
                    "ALTER TABLE task ADD COLUMN IF NOT EXISTS visibility VARCHAR(16) NOT NULL DEFAULT 'public'"
                    if dialect == "postgresql"
                    else "ALTER TABLE task ADD COLUMN visibility VARCHAR(16) NOT NULL DEFAULT 'public'"
                )
                conn.execute(text(stmt))
            if "topic_id" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE task ADD COLUMN IF NOT EXISTS topic_id INTEGER"
                        )
                    )
                else:
                    conn.execute(text("ALTER TABLE task ADD COLUMN topic_id INTEGER"))
            if "created_at" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE task ADD COLUMN IF NOT EXISTS "
                            "created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text(
                            "ALTER TABLE task ADD COLUMN created_at "
                            "DATETIME DEFAULT CURRENT_TIMESTAMP"
                        )
                    )

        if "group" in tables:
            group_cols = {c["name"] for c in insp.get_columns("group")}
            if "created_at" not in group_cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            'ALTER TABLE "group" ADD COLUMN IF NOT EXISTS '
                            "created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text(
                            'ALTER TABLE "group" ADD COLUMN created_at '
                            "DATETIME DEFAULT CURRENT_TIMESTAMP"
                        )
                    )

        if "collections" in tables:
            cols = {c["name"] for c in insp.get_columns("collections")}
            if "visibility" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN IF NOT EXISTS "
                            "visibility VARCHAR(16) NOT NULL DEFAULT 'private'"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN visibility "
                            "VARCHAR(16) NOT NULL DEFAULT 'private'"
                        )
                    )
            if "group_id" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN IF NOT EXISTS group_id INTEGER"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text("ALTER TABLE collections ADD COLUMN group_id INTEGER")
                    )
            if "deadline_at" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN IF NOT EXISTS "
                            "deadline_at TIMESTAMP WITH TIME ZONE"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text("ALTER TABLE collections ADD COLUMN deadline_at TIMESTAMP")
                    )
            if "is_archived" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN IF NOT EXISTS "
                            "is_archived BOOLEAN NOT NULL DEFAULT false"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN is_archived "
                            "BOOLEAN NOT NULL DEFAULT 0"
                        )
                    )
            if "created_at" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN IF NOT EXISTS "
                            "created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP"
                        )
                    )
                elif dialect == "sqlite":
                    conn.execute(
                        text(
                            "ALTER TABLE collections ADD COLUMN created_at "
                            "DATETIME DEFAULT CURRENT_TIMESTAMP"
                        )
                    )

        if "collection_task_association" in tables:
            cols = {c["name"] for c in insp.get_columns("collection_task_association")}
            if "sort_order" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE collection_task_association ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
                    )
                )
            if "topic" not in cols:
                conn.execute(
                    text("ALTER TABLE collection_task_association ADD COLUMN topic VARCHAR(128)")
                )

        if "teacher_profile" in tables:
            cols = {c["name"] for c in insp.get_columns("teacher_profile")}
            if "specialization" not in cols:
                conn.execute(
                    text("ALTER TABLE teacher_profile ADD COLUMN specialization VARCHAR(256)")
                )
            if "is_public" not in cols:
                if dialect == "postgresql":
                    conn.execute(
                        text(
                            "ALTER TABLE teacher_profile ADD COLUMN IF NOT EXISTS "
                            "is_public BOOLEAN NOT NULL DEFAULT true"
                        )
                    )
                else:
                    conn.execute(
                        text(
                            "ALTER TABLE teacher_profile ADD COLUMN is_public "
                            "BOOLEAN NOT NULL DEFAULT 1"
                        )
                    )


def align_profile_schema(engine: Engine) -> None:
    """User avatar/about, user_preferences, teacher visibility."""
    insp = inspect(engine)
    dialect = engine.dialect.name
    tables = insp.get_table_names()

    with engine.begin() as conn:
        if "user" in tables:
            user_cols = {c["name"] for c in insp.get_columns("user")}
            if "avatar_url" not in user_cols:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN avatar_url VARCHAR(512)'))
            if "about" not in user_cols:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN about TEXT'))

        if "user_preferences" not in tables:
            if dialect == "postgresql":
                conn.execute(
                    text("""
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    preferred_languages JSON NOT NULL DEFAULT '[]',
    preferred_difficulty VARCHAR(32) NOT NULL DEFAULT 'beginner',
    preferred_topics JSON NOT NULL DEFAULT '[]',
    study_place VARCHAR(255),
    study_group VARCHAR(128)
)
""")
                )
            else:
                conn.execute(
                    text("""
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    preferred_languages JSON NOT NULL DEFAULT '[]',
    preferred_difficulty VARCHAR(32) NOT NULL DEFAULT 'beginner',
    preferred_topics JSON NOT NULL DEFAULT '[]',
    study_place VARCHAR(255),
    study_group VARCHAR(128)
)
""")
                )
        elif "user_preferences" in tables:
            pref_cols = {c["name"] for c in insp.get_columns("user_preferences")}
            if "study_place" not in pref_cols:
                conn.execute(text("ALTER TABLE user_preferences ADD COLUMN study_place VARCHAR(255)"))
            if "study_group" not in pref_cols:
                conn.execute(text("ALTER TABLE user_preferences ADD COLUMN study_group VARCHAR(128)"))

        if "teacher_profile" in tables:
            cols = {c["name"] for c in insp.get_columns("teacher_profile")}
            if "is_public" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE teacher_profile ADD COLUMN is_public "
                        "BOOLEAN NOT NULL DEFAULT true"
                    )
                )


def align_task_id_sequence(engine: Engine) -> None:
    """
    After seed scripts insert explicit task.id values, PostgreSQL SERIAL/sequence
    can lag behind MAX(id) and cause duplicate key errors on create.
    """
    if engine.dialect.name != "postgresql":
        return

    insp = inspect(engine)
    if "task" not in insp.get_table_names():
        return

    with engine.begin() as conn:
        conn.execute(
            text(
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
        )
