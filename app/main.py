"""
FastAPI application entry point.

Creates the app, registers routers, and manages database connection lifetimes
via the lifespan context manager. Import `app` to run with uvicorn.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import close_neo4j_driver, get_neo4j_driver
from app.routes import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Runs once at startup (before yield) and once at shutdown (after yield).

    When a Neo4j URI is configured we construct the driver eagerly at startup
    (construction does not connect), and always close it on shutdown.
    """
    if settings.neo4j_uri:
        get_neo4j_driver()

    yield

    await close_neo4j_driver()


app = FastAPI(
    title="Mbhewoo Labs",
    description="Collaborative forecasting platform for African biomedical research credibility",
    version="0.1.0",
    debug=settings.app_debug,
    lifespan=lifespan,
)

# ── Static files and templates (wired up now, populated later) ───────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Landing greeting with a pointer to the interactive API docs."""
    return {
        "message": "Welcome to Mbhewoo Labs — collaborative credibility forecasting "
        "for African biomedical and biotechnology research.",
        "docs": "/docs",
        "health": "/health",
    }
