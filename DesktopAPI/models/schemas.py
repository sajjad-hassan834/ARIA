from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AppActionRequest(BaseModel):
    app: str = Field(..., description="Application name (e.g. notepad, calculator, chrome, etc.)")


class VolumeRequest(BaseModel):
    action: str = Field(..., description="Volume action: 'up', 'down', or 'mute'")
    level: Optional[int] = Field(None, description="Optional target volume level or repeats")


class ScreenshotRequest(BaseModel):
    save_to: Optional[str] = Field("desktop", description="Save target directory: 'desktop' or specific path")


class PowerRequest(BaseModel):
    action: str = Field(..., description="Power action: 'shutdown', 'restart', 'sleep', or 'lock'")
    confirm: Optional[bool] = Field(
        False,
        description="Safety confirmation required for destructive actions (shutdown, restart)",
    )


class ScreenTypeRequest(BaseModel):
    text: str = Field(..., description="Text string to type")
    speed: Optional[str] = Field("normal", description="Typing speed: 'slow', 'normal', or 'fast'")


class ScreenClickRequest(BaseModel):
    x: int = Field(..., description="X coordinate on screen")
    y: int = Field(..., description="Y coordinate on screen")
    button: Optional[str] = Field("left", description="Mouse button: 'left', 'right', 'middle', or 'double'")


class ScreenScrollRequest(BaseModel):
    direction: str = Field("down", description="Scroll direction: 'up' or 'down'")
    amount: Optional[int] = Field(3, description="Number of scroll steps/clicks")


class PlanStep(BaseModel):
    action: str = Field(..., description="Action name corresponding to desktop capability")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parameters dictionary for the action")
    target: Optional[str] = None
    query: Optional[str] = None

    class Config:
        extra = "allow"


class ExecutePlanRequest(BaseModel):
    steps: List[PlanStep] = Field(..., description="List of plan steps to execute sequentially")


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
