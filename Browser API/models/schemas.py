from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BrowseRequest(BaseModel):
    url: str = Field(..., description="Target URL to navigate to")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    platform: str = Field(default="google", description="Search platform: youtube, google, amazon, github")


class ClickRequest(BaseModel):
    target: str = Field(default="first_result", description="Click target alias (e.g. 'first_result', 'play') or CSS/XPath selector")


class ExecutePlanRequest(BaseModel):
    steps: List[Dict[str, Any]] = Field(..., description="List of step dictionaries to execute sequentially")
    source: str = Field(default="brain_api", description="Source of the plan request")


class ScreenshotRequest(BaseModel):
    filename: Optional[str] = Field(default=None, description="Optional custom filename for the screenshot")
    full_page: bool = Field(default=False, description="Whether to capture the entire scrollable page")


class BrowserResponse(BaseModel):
    status: str
    action: str
    url: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    time: str


class PlanResponse(BaseModel):
    status: str
    steps_executed: int
    steps_failed: int
    time: str
    results: List[Dict[str, Any]] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    status: str = "success"
    total: int
    history: List[Dict[str, Any]] = Field(default_factory=list)
