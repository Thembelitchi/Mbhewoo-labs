"""
scripts/test_neo4j.py — Neo4j connectivity check.

Uses the shared async driver from app/database.py (configured from .env) to run
a trivial Cypher query. Works with any Neo4j hosting (Sandbox, AuraDB,
self-hosted) because the driver reads the transport from the URI scheme.

Run from the project root:

    python scripts/test_neo4j.py

Exits 0 on success, 1 on failure. Never prints credentials. Closes the driver
on both the success and failure paths.
"""

from __future__ import annotations

import asyncio
import sys

from neo4j import exceptions as neo4j_exceptions

from app.config import settings
from app.database import close_neo4j_driver, get_neo4j_driver


async def check_connection() -> bool:
    """Run a one-line Cypher query and report success or an actionable error."""
    try:
        driver = get_neo4j_driver()
        async with driver.session(database=settings.neo4j_database) as session:
            result = await session.run("RETURN 'Hello Mbhewoo Labs' AS greeting")
            record = await result.single()
            greeting = record["greeting"]
        print(f"✓ Connected to Neo4j successfully. Response: {greeting}")
        return True
    except neo4j_exceptions.AuthError:
        print(
            "✗ Neo4j connection failed: Neo4j credentials are incorrect. "
            "Check NEO4J_USERNAME and NEO4J_PASSWORD in .env."
        )
    except neo4j_exceptions.ServiceUnavailable:
        print(
            "✗ Neo4j connection failed: Cannot reach Neo4j. Check NEO4J_URI in "
            ".env. If using Sandbox, verify it hasn't expired at "
            "sandbox.neo4j.com."
        )
    except neo4j_exceptions.ConfigurationError:
        print(
            "✗ Neo4j connection failed: Neo4j URI scheme is malformed. "
            "Expected bolt:// or neo4j+s://."
        )
    except neo4j_exceptions.Neo4jError as error:
        print(f"✗ Neo4j connection failed: {type(error).__name__}: {error}")
    except Exception as error:  # noqa: BLE001 — last-resort, report clearly
        print(f"✗ Neo4j connection failed: {type(error).__name__}: {error}")
    finally:
        # Always release the driver, on success and failure alike.
        await close_neo4j_driver()

    return False


def main() -> None:
    """Run the async check and translate the result into an exit code."""
    succeeded = asyncio.run(check_connection())
    sys.exit(0 if succeeded else 1)


if __name__ == "__main__":
    main()
