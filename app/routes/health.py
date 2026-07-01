"""
Health check endpoint.

Used by Railway/Render to verify the app is alive, and by us during
development to confirm the server started correctly.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    env: str
    demo_mode: bool


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Returns 200 if the app is running. Includes env and demo_mode flag."""
    return HealthResponse(
        status="ok",
        env=settings.app_env,
        demo_mode=settings.demo_mode,
    )
