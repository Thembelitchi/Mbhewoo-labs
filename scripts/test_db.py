"""
scripts/test_db.py — Supabase Postgres connectivity check.

Verifies that the application can reach the Supabase Postgres instance using the
*shared* async SQLAlchemy engine defined in ``app/database.py`` (which is
configured from ``.env`` via ``app/config.py`` / pydantic-settings). This script
does not create its own engine — it reuses the one the app itself uses, so a
success here means the real application configuration works.

It runs ``SELECT 1`` to prove round-trip connectivity and ``SELECT version()``
to report the server build.

Run from the project root:

    python scripts/test_db.py

Exits with code 0 on success, 1 on failure. Never prints DATABASE_URL or any
credential.
"""

from __future__ import annotations

import asyncio
import socket
import sys

import asyncpg
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

# Reused, actionable messages so the direct-exception and wrapped-exception
# (SQLAlchemy wraps the asyncpg driver error) paths report identically.
_PASSWORD_MSG = (
    "✗ Connection failed: Password in DATABASE_URL is incorrect. "
    "Reset via Supabase dashboard."
)
_DNS_MSG = (
    "✗ Connection failed: Cannot resolve the Supabase host. "
    "Check the DATABASE_URL host portion."
)
_TIMEOUT_MSG = (
    "✗ Connection failed: Connection timed out. "
    "Supabase project may be paused — check the dashboard."
)


def _map_driver_error(error: SQLAlchemyError) -> str:
    """
    Translate a SQLAlchemy error into an actionable message.

    SQLAlchemy wraps the underlying asyncpg/socket failure and exposes it on the
    ``.orig`` attribute, so we unwrap it to detect the specific failure modes
    (bad password, DNS failure, timeout) rather than dumping a raw traceback.
    """
    original = getattr(error, "orig", None) or error
    if isinstance(original, asyncpg.exceptions.InvalidPasswordError):
        return _PASSWORD_MSG
    if isinstance(original, socket.gaierror):
        return _DNS_MSG
    if isinstance(original, (asyncio.TimeoutError, TimeoutError)):
        return _TIMEOUT_MSG
    # Unknown SQLAlchemy error — surface class name and message, never the URL.
    return f"✗ Connection failed: {type(error).__name__}: {error}"


async def check_connection() -> bool:
    """
    Attempt a single round-trip query against Postgres via the shared engine.

    Returns True on success (and prints the version banner), False on any
    failure (and prints a specific, actionable reason).
    """
    if engine is None:
        print(
            "✗ Connection failed: DATABASE_URL is not set in .env. "
            "Add your Supabase connection string and retry."
        )
        return False

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            result = await connection.execute(text("SELECT version()"))
            version = result.scalar_one()
        print(f"✓ Connected to Supabase successfully. Postgres version: {version}")
        return True
    except asyncpg.exceptions.InvalidPasswordError:
        print(_PASSWORD_MSG)
    except socket.gaierror:
        print(_DNS_MSG)
    except (asyncio.TimeoutError, TimeoutError):
        print(_TIMEOUT_MSG)
    except SQLAlchemyError as error:
        print(_map_driver_error(error))
    except Exception as error:  # noqa: BLE001 — last-resort, report clearly
        print(f"✗ Connection failed: {type(error).__name__}: {error}")
    finally:
        # Dispose the shared engine's pool cleanly; does not create a new engine.
        if engine is not None:
            await engine.dispose()

    return False


def main() -> None:
    """Run the async check and translate the boolean result into an exit code."""
    succeeded = asyncio.run(check_connection())
    sys.exit(0 if succeeded else 1)


if __name__ == "__main__":
    main()
