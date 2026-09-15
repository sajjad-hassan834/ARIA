from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TextCommandRequest(BaseModel):
    command: str = Field(..., min_length=1, description="Text command or query for ARIA to execute", examples=["YouTube par Arijit Singh ke gaane chalao"])
    language: Optional[str] = Field(default="auto", description="Command language (e.g. auto, hi, en, ur)")


class CommandResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    command: str = Field(..., description="The user command processed")
    intent: Optional[str] = Field(default=None, description="Classified intent from Brain API")
    executed_by: Optional[str] = Field(default=None, description="Subsystem API executing the plan")
    status: str = Field(..., description="Execution status: success, partial, error, or offline")
    steps_completed: int = Field(default=0, description="Number of execution steps successfully completed")
    response: str = Field(..., description="Human-readable response message")
    time: str = Field(..., description="Total execution time (e.g., 3.2s)")
    plan: Optional[Dict[str, Any]] = Field(default=None, description="Generated plan details from Brain API")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Subsystem execution details")
    error: Optional[str] = Field(default=None, description="Error details if execution encountered problems")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO timestamp of command execution")



class ApiStatusDetail(BaseModel):
    status: str = Field(..., description="Status of the API: online, offline, or error")
    port: int = Field(..., description="Port number of the service")
    url: Optional[str] = Field(default=None, description="Endpoint URL")


class GatewayStatusResponse(BaseModel):
    gateway: str = Field(default="online", description="Gateway API status")
    apis: Dict[str, ApiStatusDetail] = Field(..., description="Status breakdown of all satellite APIs")
    openai: str = Field(default="online", description="OpenAI Cloud Engine status")
    ollama: Optional[str] = Field(default="disconnected", description="Legacy field for backwards compatibility")


class HistoryResponse(BaseModel):
    total: int = Field(..., description="Number of command history entries")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Recent executed commands (up to 50)")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall health state: healthy or degraded")
    gateway: str = Field(default="online", description="Gateway status")
    port: int = Field(default=8080, description="Gateway port")
    apis: Dict[str, str] = Field(default_factory=dict, description="Simple status of each connected API")
