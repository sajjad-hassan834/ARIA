import logging
import time
from fastapi import APIRouter, HTTPException, Query
from models.schemas import (
    BrowseRequest,
    ClickRequest,
    ExecutePlanRequest,
    ScreenshotRequest,
    BrowserResponse,
    PlanResponse,
    HistoryResponse,
)
from services.browser_service import browser_service

logger = logging.getLogger("routes.browse")
router = APIRouter(prefix="/api/browser", tags=["Browser"])


@router.post("/open", response_model=BrowserResponse)
async def open_url(req: BrowseRequest):
    """Navigates the browser to the requested URL."""
    try:
        res = await browser_service.goto(req.url)
        return BrowserResponse(
            status=res["status"],
            action=res["action"],
            url=res["url"],
            details={"requested_url": req.url},
            time=res["time"],
        )
    except Exception as e:
        logger.error(f"Error opening URL {req.url}: {e}")
        return BrowserResponse(
            status="error",
            action="open_failed",
            url=req.url,
            details={"error": str(e)},
            time="0.0s",
        )


@router.post("/click", response_model=BrowserResponse)
async def click_element(req: ClickRequest):
    """Clicks an element by alias ('first_result', 'play') or selector."""
    try:
        res = await browser_service.click(req.target)
        return BrowserResponse(
            status=res["status"],
            action=res["action"],
            url=res.get("details", {}).get("url"),
            details=res.get("details", {}),
            time=res["time"],
        )
    except Exception as e:
        logger.error(f"Error clicking {req.target}: {e}")
        return BrowserResponse(
            status="error",
            action="click_failed",
            details={"target": req.target, "error": str(e)},
            time="0.0s",
        )


@router.post("/screenshot", response_model=BrowserResponse)
async def capture_screenshot(req: ScreenshotRequest = ScreenshotRequest()):
    """Captures a screenshot of the current page and returns the file path."""
    start_time = time.perf_counter()
    try:
        path = await browser_service.take_screenshot(filename=req.filename, full_page=req.full_page)
        elapsed = time.perf_counter() - start_time
        return BrowserResponse(
            status="success",
            action="screenshot_taken",
            url=browser_service.page.url if browser_service.page else None,
            details={"path": path, "filename": req.filename or path.split("\\")[-1].split("/")[-1]},
            time=f"{elapsed:.2f}s",
        )
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return BrowserResponse(
            status="error",
            action="screenshot_failed",
            details={"error": str(e)},
            time="0.0s",
        )


@router.post("/execute-plan", response_model=PlanResponse)
async def execute_plan(req: ExecutePlanRequest):
    """Executes a multi-step sequence from Brain API."""
    try:
        res = await browser_service.execute_plan(req.steps)
        return PlanResponse(
            status=res["status"],
            steps_executed=res["steps_executed"],
            steps_failed=res["steps_failed"],
            time=res["time"],
            results=res.get("results", []),
        )
    except Exception as e:
        logger.error(f"Error executing plan: {e}")
        return PlanResponse(
            status="error",
            steps_executed=0,
            steps_failed=len(req.steps),
            time="0.0s",
            results=[{"error": str(e)}],
        )


@router.get("/history", response_model=HistoryResponse)
async def get_history(limit: int = Query(default=20, ge=1, le=100)):
    """Retrieves the last N browser actions from history."""
    try:
        items = await browser_service.get_history(limit=limit)
        return HistoryResponse(
            status="success",
            total=len(items),
            history=items,
        )
    except Exception as e:
        logger.error(f"Error reading history: {e}")
        return HistoryResponse(status="error", total=0, history=[])
