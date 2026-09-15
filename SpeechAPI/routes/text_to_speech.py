from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from models.schemas import TTSRequest
from services.tts_service import tts_service
from exceptions import TTSSynthesisException

router = APIRouter(prefix="/api/tts", tags=["Text To Speech"])

@router.post(
    "/speak",
    summary="Convert text to speech audio",
    description="Accepts text input and language, synthesizes speech with gTTS, and streams back an MP3 audio file.",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "MP3 audio stream"
        }
    }
)
async def speak_text(payload: TTSRequest):
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text field cannot be empty."
        )

    try:
        audio_stream = tts_service.text_to_speech_mp3(
            text=payload.text.strip(),
            lang=payload.language or "en",
            slow=payload.slow or False
        )

        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="speech.mp3"',
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        raise TTSSynthesisException(
            message=str(e),
            details={"text_snippet": payload.text[:50], "language": payload.language}
        )
