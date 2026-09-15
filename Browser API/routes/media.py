import logging
from fastapi import APIRouter
from models.schemas import BrowserResponse
from services.browser_service import browser_service
from services.media_service import MediaService

logger = logging.getLogger("routes.media")
router = APIRouter(prefix="/api/browser/media", tags=["Media"])


@router.post("/play", response_model=BrowserResponse)
async def play_media():
    """Resumes or starts playback of media on the current page."""
    try:
        res = await MediaService.play(browser_service)
        return BrowserResponse(
            status=res["status"],
            action=res["action"],
            url=browser_service.page.url if browser_service.page else None,
            details=res.get("details", {}),
            time=res["time"],
        )
    except Exception as e:
        logger.error(f"Error playing media: {e}")
        return BrowserResponse(
            status="error",
            action="play_failed",
            details={"error": str(e)},
            time="0.0s",
        )


@router.post("/pause", response_model=BrowserResponse)
async def pause_media():
    """Pauses playback of media on the current page."""
    try:
        res = await MediaService.pause(browser_service)
        return BrowserResponse(
            status=res["status"],
            action=res["action"],
            url=browser_service.page.url if browser_service.page else None,
            details=res.get("details", {}),
            time=res["time"],
        )
    except Exception as e:
        logger.error(f"Error pausing media: {e}")
        return BrowserResponse(
            status="error",
            action="pause_failed",
            details={"error": str(e)},
            time="0.0s",
        )


@router.post("/toggle", response_model=BrowserResponse)
async def toggle_media():
    """Toggles media play/pause state."""
    try:
        res = await MediaService.toggle(browser_service)
        return BrowserResponse(
            status=res["status"],
            action=res["action"],
            url=browser_service.page.url if browser_service.page else None,
            details=res.get("details", {}),
            time=res["time"],
        )
    except Exception as e:
        logger.error(f"Error toggling media: {e}")
        return BrowserResponse(
            status="error",
            action="toggle_failed",
            details={"error": str(e)},
            time="0.0s",
        )
