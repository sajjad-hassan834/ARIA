import asyncio
import os
import shutil
import tempfile
import time
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Request, status

from models.schemas import TranscribeResponse
from exceptions import (
    AudioFormatNotSupportedException,
    ModelNotLoadedException,
    AudioProcessingException
)
import config

router = APIRouter(prefix="/api/speech", tags=["Speech To Text"])

@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="Transcribe audio file to text",
    description="Upload an audio file (WAV, MP3, WebM, M4A, OGG) to transcribe with the cached Whisper model."
)
async def transcribe_audio(
    request: Request,
    file: UploadFile = File(..., description="Audio file to transcribe")
):
    # Validate extension
    file_ext = Path(file.filename or "audio.wav").suffix.lower()
    if file_ext not in config.SUPPORTED_AUDIO_EXTENSIONS:
        raise AudioFormatNotSupportedException(file_ext, config.SUPPORTED_AUDIO_EXTENSIONS)

    # Access cached Whisper service from app state
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

    # Write temporary file safely
    temp_path = None
    start_time = time.perf_counter()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_path = Path(tmp.name)
            shutil.copyfileobj(file.file, tmp)

        result = await asyncio.to_thread(whisper_service.transcribe, str(temp_path))
        elapsed = round(time.perf_counter() - start_time, 3)

        return TranscribeResponse(
            text=result["text"],
            confidence=result["confidence"],
            language=result["language"],
            processing_time=elapsed
        )
    except Exception as e:
        raise AudioProcessingException(
            message=str(e),
            details={"filename": file.filename, "content_type": file.content_type}
        )
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
