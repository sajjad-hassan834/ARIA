from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    text: str = Field(..., description="User input command or utterance", example="YouTube par Arijit Singh ke gaane chalao")
    language: str = Field(default="auto", description="Detected or specified language (e.g., auto, hi, en)")


class PlanStep(BaseModel):
    step: int = Field(..., description="1-based step order")
    action: str = Field(..., description="Action name to execute")
    target: Optional[str] = Field(default=None, description="Target application, website, or resource")
    query: Optional[str] = Field(default=None, description="Search query or text parameter")
    location: Optional[str] = Field(default=None, description="Filesystem or UI target location")
    name: Optional[str] = Field(default=None, description="Item or folder name")

    class Config:
        extra = "allow"


class PlanResponse(BaseModel):
    input: Optional[str] = ""
    thinking: Optional[str] = None
    reasoning: Optional[str] = None
    intent: str
    steps: List[Dict[str, Any]]
    api_route: str
    port: int
    confidence: float
    estimated_time: Optional[str] = "1.0s"
    response: Optional[str] = None

    class Config:
        extra = "allow"


class ClassifyRequest(BaseModel):
    text: str = Field(..., description="User utterance to classify", example="Desktop par folder banao")


class ClassifyResponse(BaseModel):
    input: str
    api: str
    port: int
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ContextRequest(BaseModel):
    input: Optional[str] = Field(default=None, description="Utterance or user command to log in context")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional command execution metadata")


class ContextResponse(BaseModel):
    status: str
    recent_commands: List[Dict[str, Any]]
    last_plan: Optional[Dict[str, Any]] = None


class HistoryResponse(BaseModel):
    total: int
    tasks: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    brain: str
    speech_api: str
    browser_api: str
    desktop_api: str
    file_api: str
    ollama: str
