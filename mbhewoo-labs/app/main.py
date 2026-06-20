from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health

# Intialize the FastAPI application
app = FastAPI(
    title="Mbhewoo Labs API",
    description="Collaborative credibility forecasting platform for African biomedical and biotechnology research",
    version="0.1.0",
)

# Apply CORS middleware for API routing and external interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints and routers
app.include_router(health.router)


@app.get("/")
async def root():
    """
    Root greeting metadata.
    """
    return {
        "message": "Welcome to Mbhewoo Labs - African Biomedical & Biotechnology Credibility Forecasting Platform",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    # Local fallback execution runner
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
