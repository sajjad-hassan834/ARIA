import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure GatewayAPI root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from models.schemas import HealthResponse
from routes import gateway_router
from services.orchestrator import orchestrator_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gateway.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager: verifies satellite APIs connectivity on startup."""
    logger.info("==================================================")
    logger.info("  Starting ARIA Master Gateway API on Port %d", config.PORT)
    logger.info("==================================================")
    logger.info("Performing startup connectivity check on connected ARIA APIs...")

    try:
        status_report = await orchestrator_service.check_all_apis()
        for api_name, info in status_report.get("apis", {}).items():
            st = info.get("status", "unknown")
            port = info.get("port", "?")
            logger.info("  [%s] API (Port %s): %s", api_name, port, st.upper())
        logger.info("  [Ollama LLM]: %s", status_report.get("ollama", "unknown").upper())
    except Exception as exc:
        logger.warning("Startup connectivity check error: %s", exc)

    logger.info("Gateway API initialized and ready to receive commands.")
    yield
    logger.info("Shutting down ARIA Master Gateway API.")


app = FastAPI(
    title="ARIA Master Gateway API",
    description=(
        "Master Controller and Entrypoint for the ARIA Assistant System. "
        "Unifies Speech API (8000), Brain API (8001), Browser API (8002), "
        "Desktop API (8003), and File API (8004) under a single interface."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware for cross-origin local apps & UI clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(gateway_router)


@app.get("/", tags=["General"], summary="Gateway API Root")
async def root():
    return {
        "service": "ARIA Master Gateway API",
        "version": "1.0.0",
        "status": "online",
        "port": config.PORT,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "text_command": "POST /api/gateway/command/text",
            "audio_command": "POST /api/gateway/command/audio",
            "system_status": "GET /api/gateway/status",
            "command_history": "GET /api/gateway/history",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["General"], summary="Health check endpoint")
async def health_check():
    """Returns gateway health status and connectivity overview."""
    status_report = await orchestrator_service.check_all_apis()
    apis_simple = {name: detail["status"] for name, detail in status_report.get("apis", {}).items()}
    all_online = all(s == "online" for s in apis_simple.values())

    return {
        "status": "healthy" if all_online else "degraded",
        "gateway": "online",
        "port": config.PORT,
        "apis": apis_simple,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )
