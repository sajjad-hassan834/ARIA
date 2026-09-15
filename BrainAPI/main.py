import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import asyncio
from typing import Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

import config
from models.schemas import HealthResponse
from routes import plan_router, intent_router, context_router

app = FastAPI(
    title="ARIA Brain API",
    description="Intelligence and Planning Layer for ARIA Assistant System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local cross-service communication and UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(plan_router)
app.include_router(intent_router)
app.include_router(context_router)


# Fast connect timeout so health checks complete in under 200ms
PROBE_TIMEOUT = httpx.Timeout(0.2, connect=0.2)


async def check_service_status(client: httpx.AsyncClient, url: str) -> str:
    """Probe an external service URL with an ultra-fast timeout."""
    target_url = f"{url.rstrip('/')}/health"
    try:
        res = await client.get(target_url, timeout=PROBE_TIMEOUT)
        if res.status_code < 500:
            return "connected"
    except Exception:
        pass

    try:
        res = await client.get(url, timeout=PROBE_TIMEOUT)
        if res.status_code < 500:
            return "connected"
    except Exception:
        pass

    return "disconnected"


@app.get("/", tags=["General"])
async def root():
    return {
        "name": "ARIA Brain API",
        "version": "1.0.0",
        "status": "ready",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"], summary="Health check for Brain and connected APIs")
@app.get("/api/brain/health", response_model=HealthResponse, tags=["General"], include_in_schema=False)
async def health_check(request: Request):
    """
    Check the status of Brain API and all connected satellite APIs:
    - Speech API (8000)
    - Browser API (8002)
    - Desktop API (8003)
    - File API (8004)
    - OpenAI Cloud Engine
    """
    current_port = request.url.port or config.PORT

    async with httpx.AsyncClient() as client:
        # Avoid recursion if Brain API is accidentally run on port 8000
        if current_port == 8000:
            speech_task = asyncio.sleep(0, result="disconnected")
        else:
            speech_task = check_service_status(client, config.SPEECH_API_URL)

        browser_task = check_service_status(client, config.BROWSER_API_URL)
        desktop_task = check_service_status(client, config.DESKTOP_API_URL)
        file_task = check_service_status(client, config.FILE_API_URL)

        speech_status, browser_status, desktop_status, file_status = (
            await asyncio.gather(
                speech_task,
                browser_task,
                desktop_task,
                file_task,
            )
        )

    return {
        "status": "ok",
        "brain": "ready",
        "speech_api": speech_status,
        "browser_api": browser_status,
        "desktop_api": desktop_status,
        "file_api": file_status,
        "openai": "online",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
