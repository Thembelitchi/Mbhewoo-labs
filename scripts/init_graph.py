"""
scripts/init_graph.py — initialise the Neo4j graph schema.

Idempotently creates the corpus constraints and indexes (see app/graph/schema.py)
and then prints what constraints and indexes exist in the database, so you can
confirm the result. Safe to run repeatedly.

Run from the project root:

    python scripts/init_graph.py
"""

from __future__ import annotations

import asyncio
import sys

from neo4j import exceptions as neo4j_exceptions

from app.database import close_neo4j_driver
from app.graph.schema import initialise_graph_schema, list_graph_schema


async def run() -> bool:
    """Create the schema, then list the resulting constraints and indexes."""
    try:
        summary = await initialise_graph_schema()
        schema = await list_graph_schema()
    except neo4j_exceptions.AuthError:
        print(
            "✗ Neo4j credentials are incorrect. Check NEO4J_USERNAME and "
            "NEO4J_PASSWORD in .env."
        )
        return False
    except neo4j_exceptions.ServiceUnavailable:
        print(
            "✗ Cannot reach Neo4j. Check NEO4J_URI in .env. If using Sandbox, "
            "verify it hasn't expired at sandbox.neo4j.com."
        )
        return False
    except neo4j_exceptions.Neo4jError as error:
        print(f"✗ Neo4j error: {type(error).__name__}: {error}")
        return False
    finally:
        await close_neo4j_driver()

    print(
        f"✓ Applied {summary['constraints']} constraints and "
        f"{summary['indexes']} indexes (idempotent).\n"
    )
    print(f"Constraints now in database ({len(schema['constraints'])}):")
    for name in schema["constraints"]:
        print(f"  • {name}")
    print(f"\nIndexes now in database ({len(schema['indexes'])}):")
    for name in schema["indexes"]:
        print(f"  • {name}")
    return True


def main() -> None:
    succeeded = asyncio.run(run())
    sys.exit(0 if succeeded else 1)


if __name__ == "__main__":
    main()
