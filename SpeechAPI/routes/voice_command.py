import shutil
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Query, status

from models.schemas import CommandResponse, IntentRequest, IntentResponse, HistoryResponse
from services.nlu_service import nlu_service
from services.command_processor import command_processor
from exceptions import (
    AudioFormatNotSupportedException,
    ModelNotLoadedException,
    AudioProcessingException
)
import config

router = APIRouter(prefix="/api/speech", tags=["Voice Commands & NLU"])

@router.post(
    "/command",
    response_model=CommandResponse,
    summary="Process spoken voice command from audio file",
    description="Upload spoken audio, transcribe with cached Whisper model, extract intent via NLU, and return structured command action."
)
async def process_voice_command(
    request: Request,
    file: UploadFile = File(..., description="Audio file containing voice command")
):
    file_ext = Path(file.filename or "audio.wav").suffix.lower()
    if file_ext not in config.SUPPORTED_AUDIO_EXTENSIONS:
        raise AudioFormatNotSupportedException(file_ext, config.SUPPORTED_AUDIO_EXTENSIONS)

    # Access cached Whisper model
    whisper_service = getattr(request.app.state, "whisper_service", None)
    if not whisper_service:
        from services.whisper_service import whisper_service as fallback_service
        whisper_service = fallback_service

    if not whisper_service.model:
        try:
            whisper_service.load_model()
        except Exception as err:
            raise ModelNotLoadedException(
                message=f"Whisper model could not be initialized: {str(err)}",
                details={"model_name": config.WHISPER_MODEL}
            )

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_path = Path(tmp.name)
            shutil.copyfileobj(file.file, tmp)

        # Transcribe speech
        transcription = whisper_service.transcribe(str(temp_path))
        raw_text = transcription["text"].strip()

        if not raw_text:
            return CommandResponse(
                raw_text="",
                intent="unknown",
                action="no_audio_detected",
                response="No audible speech could be recognized.",
                success=False,
                timestamp=command_processor.process_command("").timestamp
            )

        # Process intent and execute command
        command_result = command_processor.process_command(raw_text)
        return command_result

    except Exception as e:
        raise AudioProcessingException(
            message=str(e),
            details={"filename": file.filename}
        )
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


@router.post(
    "/intent",
    response_model=IntentResponse,
    summary="Extract intent from raw text",
    description="Analyze text string (English, Urdu, or Roman Urdu) and match with defined system intents using RapidFuzz."
)
async def extract_intent(payload: IntentRequest):
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text input cannot be empty."
        )

    result = nlu_service.match_intent(payload.text)
    return IntentResponse(
        input=result["input"],
        intent=result["intent"],
        confidence=result["confidence"],
        language=result["language"]
    )


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get recent voice command execution history",
    description="Returns the last 50 executed voice commands with timestamps and metadata."
)
async def get_command_history(
    limit: Optional[int] = Query(
        config.MAX_HISTORY,
        ge=1,
        le=100,
        description="Max records to return"
    )
):
    try:
        history_records = command_processor.get_history(limit=limit)
        return HistoryResponse(
            total=len(history_records),
            history=history_records
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve command history: {str(e)}"
        )
