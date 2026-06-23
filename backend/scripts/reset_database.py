"""
Wipe the database schema and bootstrap a fresh dev environment.

Steps:
  1. DROP SCHEMA public CASCADE + recreate (full wipe)
  2. alembic upgrade head    (recreate schema)
  3. ensure_super_user       (admin@test.com with ADMIN + TEACHER + STUDENT)
  4. optional: load_showcase_tasks (demo assignments by Admin)

Usage (from backend/):
  poetry run python scripts/reset_database.py --yes
  poetry run python scripts/reset_database.py --yes --with-tasks
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _confirm(force: bool) -> bool:
    print("WARNING: This will DELETE ALL DATA in the application database.")
    print("Postgres must be running and DB__* / .env must point to the target DB.")
    if force:
        return True
    typed = input("Type 'RESET DATABASE' to continue: ").strip()
    return typed == "RESET DATABASE"


def _run_alembic(*args: str) -> None:
    cmd = [sys.executable, "-m", "alembic", *args]
    print(f">>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=BACKEND_ROOT, check=True)


def _drop_public_schema() -> None:
    sys.path.insert(0, str(BACKEND_ROOT))
    from shared.config import Settings

    settings = Settings()
    print(
        f">>> Database: {settings.db.host}:{settings.db.port}/{settings.db.name} "
        f"(user={settings.db.user})"
    )

    engine = create_engine(settings.db.dsn, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(
            text(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = current_database()
                  AND pid <> pg_backend_pid()
                """
            )
        )
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        conn.execute(text(f'GRANT ALL ON SCHEMA public TO "{settings.db.user}"'))

        remaining = conn.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
            )
        ).fetchall()
        if remaining:
            print(">>> Extra cleanup for leftover tables:", [r[0] for r in remaining])
            for (table_name,) in remaining:
                conn.execute(text(f'DROP TABLE IF EXISTS public."{table_name}" CASCADE'))
        else:
            print(">>> Schema public is empty.")
    engine.dispose()


def _create_schema_from_orm() -> None:
    """Create tables from current SQLAlchemy models (migrations chain is incomplete for greenfield)."""
    sys.path.insert(0, str(BACKEND_ROOT))
    from sqlalchemy.orm import configure_mappers

    from infrastructure.db.models.base import Base
    from infrastructure.db.models.task.registry import load_models
    from shared.config import Settings

    load_models()
    configure_mappers()

    settings = Settings()
    engine = create_engine(settings.db.dsn)
    print(">>> Base.metadata.create_all()")
    Base.metadata.create_all(engine)
    engine.dispose()


def reset_database(*, with_tasks: bool, skip_migrations: bool) -> None:
    if not skip_migrations:
        _drop_public_schema()
        _create_schema_from_orm()
        _run_alembic("stamp", "head")
    else:
        print("Skipping schema wipe/migrations (--skip-migrations).")

    sys.path.insert(0, str(BACKEND_ROOT))
    from ensure_super_user import ensure_super_user

    ensure_super_user()

    if with_tasks:
        from load_showcase_tasks import load_showcase_tasks

        load_showcase_tasks(replace_existing=False)

    print()
    print("Bootstrap complete.")
    print("  Login: admin@test.com (SEED_ADMIN_EMAIL)")
    print("  Password: SEED_ADMIN_PASSWORD from .env")
    print("  Roles: admin, teacher, student")


def main() -> None:
    parser = argparse.ArgumentParser(description="Full database reset + super-user seed.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")
    parser.add_argument(
        "--with-tasks",
        action="store_true",
        help="Load showcase tasks from scripts/load_showcase_tasks.py",
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Only seed super-user (schema already exists).",
    )
    args = parser.parse_args()

    if not _confirm(force=args.yes):
        print("Cancelled.")
        return

    reset_database(with_tasks=args.with_tasks, skip_migrations=args.skip_migrations)


if __name__ == "__main__":
    main()
