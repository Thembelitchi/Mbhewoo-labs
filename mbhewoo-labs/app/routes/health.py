from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Service health check endpoint.
    Verifies that the application server is up, running, and accessible.
    """
    return {
        "status": "ok",
        "service": "mbhewoo-labs",
    }
