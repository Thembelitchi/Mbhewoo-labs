"""
Application settings loaded from environment variables via pydantic-settings.

Add a real .env file (never commit it) or export variables in your shell.
The .env.example file shows every variable you need to set.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me")

    # ── Postgres (Supabase) ──────────────────────────────────────────────────
    database_url: str = Field(default="")

    # ── Neo4j (AuraDB / Sandbox) ─────────────────────────────────────────────
    # Works with any scheme (bolt://, neo4j://, neo4j+s://) — the driver picks
    # transport from the URI, so switching Sandbox → AuraDB is a .env change.
    neo4j_uri: str = Field(default="")
    neo4j_username: str = Field(default="neo4j")
    neo4j_password: str = Field(default="")
    neo4j_database: str = Field(default="neo4j")

    # ── Feature flags ────────────────────────────────────────────────────────
    # When True, synthetic forecasters and demo data are active.
    # Flip to False before real-user launch to remove all synthetic records.
    demo_mode: bool = Field(default=True)


# Single shared instance — import this everywhere instead of re-instantiating.
settings = Settings()
