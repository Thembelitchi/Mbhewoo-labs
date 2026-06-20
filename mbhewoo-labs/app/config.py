from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application settings for Mbhewoo Labs.
    Loads and validates values from environment variables or a .env file.
    """
    # Environment mode
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    
    # Security Key for cryptographic signings and credentials
    SECRET_KEY: str = "dev_secret_key_change_me_in_production_1234567890"

    # Supabase / PostgreSQL Connection Database URL (compatible with asyncpg)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mbhewoo_labs"

    # Neo4j Database configuration values
    NEO4J_URI: str = "neo4j://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Pydantic Settings configuration meta-class
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore any other environment variables not defined here
    )


# Instantiate the settings container
settings = Settings()
