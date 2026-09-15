import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from config import PORT, SCREENSHOT_DIR, HEADLESS
from routes import browse_router, search_router, media_router
from services.browser_service import browser_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: starts browser session on startup and stops on shutdown."""
    logger.info("Initializing Browser API service...")
    try:
        await browser_service.start()
        logger.info("Browser session initialized and ready.")
    except Exception as e:
        logger.error(f"Failed to start browser on application startup: {e}")
    
    yield

    logger.info("Shutting down Browser API service...")
    try:
        await browser_service.stop()
        logger.info("Browser session closed.")
    except Exception as e:
        logger.error(f"Error while closing browser session: {e}")


app = FastAPI(
    title="ARIA Browser API",
    description="Browser automation service for the ARIA system using Playwright",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount screenshots directory for static viewing/download
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOT_DIR)), name="screenshots")

# Register API Routers
app.include_router(browse_router)
app.include_router(search_router)
app.include_router(media_router)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/api/browser/health", tags=["Health"])
async def health_check():
    """Health check endpoint providing browser connectivity status."""
    is_active = getattr(browser_service, "is_active", True)
    current_url = getattr(browser_service, "current_url", None)

    return {
        "status": "ok",
        "service": "ARIA Browser API",
        "port": PORT,
        "headless": False,
        "browser_active": is_active,
        "current_url": current_url,
    }



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)
