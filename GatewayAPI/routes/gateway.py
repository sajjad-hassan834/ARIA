import logging
from typing import Optional
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from models.schemas import (
    CommandResponse,
    GatewayStatusResponse,
    HistoryResponse,
    TextCommandRequest,
)
from services.orchestrator import orchestrator_service

logger = logging.getLogger("routes.gateway")

router = APIRouter(prefix="/api/gateway", tags=["Gateway"])


@router.post(
    "/command/text",
    response_model=CommandResponse,
    summary="Process text command through ARIA",
    description="Accept a user text command, generate a structured execution plan via Brain API, dispatch to the target subsystem (Browser, Desktop, or File API), and return the execution result."
)
async def process_text_command_endpoint(payload: TextCommandRequest):
    if not payload.command or not payload.command.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Command text cannot be empty."
        )

    result = await orchestrator_service.process_text_command(
        text=payload.command,
        language=payload.language or "auto"
    )
    return result


@router.post(
    "/command/audio",
    response_model=CommandResponse,
    summary="Process spoken voice command through ARIA",
    description="Upload an audio recording, transcribe speech via Speech API (8000), plan via Brain API (8001), and execute via the appropriate subsystem."
)
async def process_audio_command_endpoint(
    file: UploadFile = File(..., description="Audio file containing speech utterance (WAV, MP3, WebM, M4A, OGG)")
):
    try:
        audio_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded audio file: {str(e)}"
        )

    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty."
        )

    filename = file.filename or "audio.wav"
    content_type = file.content_type or "audio/wav"

    result = await orchestrator_service.process_audio_command(
        audio_bytes=audio_bytes,
        filename=filename,
        content_type=content_type
    )
    return result


@router.get(
    "/status",
    response_model=GatewayStatusResponse,
    summary="Check status of Gateway and all connected satellite APIs",
    description="Probes the health status of Speech API (8000), Brain API (8001), Browser API (8002), Desktop API (8003), File API (8004), and Ollama service."
)
async def get_system_status():
    status_data = await orchestrator_service.check_all_apis()
    return status_data


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get recent command execution history",
    description="Returns the last 50 executed commands with plan details, execution subsystems, and timestamps."
)
async def get_command_history(
    limit: Optional[int] = Query(
        default=50,
        ge=1,
        le=100,
        description="Max history items to retrieve"
    )
):
    history_items = orchestrator_service.get_history(limit=limit)
    return HistoryResponse(
        total=len(history_items),
        history=history_items
    )
