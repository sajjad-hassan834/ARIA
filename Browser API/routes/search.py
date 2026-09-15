import logging
from fastapi import APIRouter
from models.schemas import SearchRequest, BrowserResponse
from services.browser_service import browser_service
from services.search_service import SearchService

logger = logging.getLogger("routes.search")
router = APIRouter(prefix="/api/browser", tags=["Search"])


@router.post("/search", response_model=BrowserResponse)
async def search(req: SearchRequest):
    """Conducts a search on specified platform (youtube, google, amazon, github)."""
    try:
        res = await SearchService.search(browser_service, query=req.query, platform=req.platform)
        return BrowserResponse(
            status=res["status"],
            action=res["action"],
            url=res.get("details", {}).get("url"),
            details=res.get("details", {}),
            time=res["time"],
        )
    except Exception as e:
        logger.error(f"Error searching '{req.query}' on '{req.platform}': {e}")
        return BrowserResponse(
            status="error",
            action="search_failed",
            details={"query": req.query, "platform": req.platform, "error": str(e)},
            time="0.0s",
        )
