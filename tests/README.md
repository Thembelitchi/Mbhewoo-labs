# Tests

## How the test database works

The test suite runs against an **in-memory SQLite database via `aiosqlite`**,
provided by the async `db_session` fixture in `conftest.py`. Each test gets a
fresh, isolated database (schema created from `Base.metadata`), so tests are
fast and require no network, no Supabase, and no Neo4j.

## Known coverage gap: SQLite ≠ Postgres

SQLite does **not** enforce the following the way our production Postgres does,
so these are **NOT exercised by the current tests**:

- **Foreign-key enforcement** (SQLite has FK checks off by default)
- **Cascade behaviour** (`ON DELETE CASCADE` / `SET NULL`)
- **CHECK constraints** (e.g. the market invariants)

These *are* enforced in production: the Alembic migrations define FKs, cascades,
and CHECK constraints at the database level regardless of test coverage. What
the SQLite tests validate is schema shape, column defaults, unique constraints,
and association-table wiring.

## Future work: Postgres integration tests

Postgres-only integration tests should be added when we build features that
actually depend on cascade behaviour — most likely the **data-cleanup and
synthetic-purge tools** (removing `is_synthetic=True` records and expecting
edges to cascade). This is a deliberate placeholder, not an oversight: no
cascade-dependent feature is on the near-term roadmap.

When a `TEST_DATABASE_URL` pointing at a real (throwaway) Postgres becomes
available, the `db_session` fixture can be extended to run tests **both ways** —
against SQLite for speed and against Postgres for full FK/cascade/CHECK
fidelity (e.g. parametrised on the backend URL).
