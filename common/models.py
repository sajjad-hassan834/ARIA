from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PlanStep(BaseModel):
    model_config = ConfigDict(extra="allow")

    step: Optional[int] = Field(default=None, description="Step number (1-based)")
    action: str = Field(..., description="Action to perform")
    target: Optional[str] = Field(default=None, description="Target entity or destination")
    query: Optional[str] = Field(default=None, description="Query string or search parameter")
    location: Optional[str] = Field(default=None, description="Target location or directory")
    name: Optional[str] = Field(default=None, description="Name parameter")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action parameters")


class ExecutePlanRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    steps: List[Dict[str, Any]] = Field(..., description="List of plan steps to execute")


class ExecutePlanResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: str = Field(..., description="Status of execution: success, partial, or error")
    steps_executed: int = Field(default=0, description="Count of successfully executed steps")
    steps_failed: int = Field(default=0, description="Count of failed steps")
    results: List[Any] = Field(default_factory=list, description="Step-by-step execution results")
    time: Optional[str] = Field(default=None, description="Execution time (e.g. 1.2s)")
    message: Optional[str] = Field(default=None, description="Human-readable execution outcome")


class APIResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool = Field(..., description="Operation success indicator")
    message: str = Field(..., description="Operation response message")
    data: Optional[Any] = Field(default=None, description="Returned payload data")


class ServiceStatusDetail(BaseModel):
    status: str = Field(..., description="Status: online, offline, or error")
    port: int = Field(..., description="Port number")
    url: Optional[str] = Field(default=None, description="Endpoint URL")


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: str = Field(..., description="Overall health: healthy, degraded, or ok")
    service: Optional[str] = Field(default=None, description="Service identifier name")
    port: Optional[int] = Field(default=None, description="Service listening port")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    apis: Optional[Dict[str, Any]] = Field(default=None, description="Connected services status")
