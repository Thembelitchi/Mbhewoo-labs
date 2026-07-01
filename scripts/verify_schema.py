"""
scripts/verify_schema.py — list all Postgres tables and their columns.

Connects via the shared async engine from app/database.py (configured from
.env) and prints every public table with its columns and types, plus the
current Alembic head. Use it after ``alembic upgrade head`` to confirm the
schema landed as expected.

Run from the project root:

    python scripts/verify_schema.py
"""

from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.database import engine


async def verify_schema() -> None:
    """Print all public tables, their columns, and the Alembic head revision."""
    if engine is None:
        print("✗ DATABASE_URL is not set in .env.")
        raise SystemExit(1)

    async with engine.connect() as connection:
        tables = (
            await connection.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
                    "ORDER BY table_name"
                )
            )
        ).scalars().all()

        print(f"Found {len(tables)} tables in schema 'public':\n")
        for table_name in tables:
            columns = (
                await connection.execute(
                    text(
                        "SELECT column_name, data_type, is_nullable "
                        "FROM information_schema.columns "
                        "WHERE table_schema = 'public' AND table_name = :t "
                        "ORDER BY ordinal_position"
                    ),
                    {"t": table_name},
                )
            ).all()
            print(f"── {table_name} ({len(columns)} columns)")
            for name, data_type, is_nullable in columns:
                null_flag = "NULL" if is_nullable == "YES" else "NOT NULL"
                print(f"     {name:<28} {data_type:<28} {null_flag}")
            print()

        head = None
        if "alembic_version" in tables:
            head = (
                await connection.execute(text("SELECT version_num FROM alembic_version"))
            ).scalar_one_or_none()
        print(f"Alembic head revision: {head}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_schema())
