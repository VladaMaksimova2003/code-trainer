-- Safe additive patch when Alembic 20260512_0007 was not applied.
-- PostgreSQL 11+: DEFAULT backfills existing rows for NOT NULL columns.

ALTER TABLE collections
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE "group"
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
