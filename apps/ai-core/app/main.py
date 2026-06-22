"""
Waken-Agent AI Core — FastAPI application entry point.

Start: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.models.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Startup: register all built-in tools
    from app.core.tools import register_all_tools

    register_all_tools()
    print("[AI Core] All tools registered [OK]")
    yield
    # Shutdown
    print("[AI Core] Shutting down...")


app = FastAPI(
    title="Waken-Agent AI Core",
    description="Multi-Agent collaboration platform — AI Core service",
    version="0.0.1",
    lifespan=lifespan,
)

# Include routers
app.include_router(agent_router)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version="0.0.1")
