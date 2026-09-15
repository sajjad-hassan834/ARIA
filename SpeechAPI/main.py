import time
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

import config
from exceptions import (
    SpeechAPIException,
    ModelNotLoadedException,
    AudioFormatNotSupportedException,
    AudioProcessingException,
    TTSSynthesisException
)
from services.whisper_service import whisper_service
from services.llm_service import check_ollama_status
from routes.speech_to_text import router as stt_router

from routes.text_to_speech import router as tts_router
from routes.voice_command import router as voice_cmd_router
from routes.websocket_stream import router as ws_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("speech_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan event handler:
    Preloads Whisper model ONCE on server startup and caches in memory.
    Gracefully handles startup exceptions so server remains healthy for other services.
    """
    logger.info("Initializing SpeechAPI server...")
    app.state.whisper_service = None
    app.state.startup_error = None

    try:
        whisper_service.load_model()
        app.state.whisper_service = whisper_service
        logger.info(f"Whisper '{config.WHISPER_MODEL}' model cached in application state.")
    except Exception as e:
        error_msg = f"Failed to preload Whisper model on startup: {str(e)}"
        logger.error(error_msg, exc_info=True)
        app.state.startup_error = error_msg

    yield

    logger.info("Shutting down SpeechAPI server...")

# Initialize FastAPI App with Swagger UI /docs
app = FastAPI(
    title="Speech Recognition & Voice Interaction REST API",
    description="Production-ready FastAPI backend for speech-to-text (Whisper), NLU intent matching (Roman Urdu/English), TTS (gTTS), and real-time WebSocket voice streaming.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware for cross-origin frontend/mobile/desktop app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper for uniform JSON error responses
def format_error_response(
    status_code: int,
    error_code: str,
    message: str,
    path: str,
    details: Any = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": message,
            "details": details,
            "status_code": status_code,
            "path": path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# Request Logging & Exception Safety Middleware
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - {duration_ms}ms")
        return response
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(f"{request.method} {request.url.path} failed with unhandled error after {duration_ms}ms: {exc}", exc_info=True)
        return format_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred while processing your request.",
            path=request.url.path,
            details=str(exc) if config.DEBUG else None
        )

# Global Domain Exception Handler
@app.exception_handler(SpeechAPIException)
async def speech_api_exception_handler(request: Request, exc: SpeechAPIException):
    logger.warning(f"Domain error on {request.url.path} [{exc.error_code}]: {exc.message}")
    return format_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path,
        details=exc.details
    )

# Starlette / FastAPI HTTP Exceptions Handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_code = "HTTP_ERROR"
    if exc.status_code == 404:
        error_code = "RESOURCE_NOT_FOUND"
    elif exc.status_code == 400:
        error_code = "BAD_REQUEST"
    elif exc.status_code == 401:
        error_code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        error_code = "FORBIDDEN"

    return format_error_response(
        status_code=exc.status_code,
        error_code=error_code,
        message=str(exc.detail),
        path=request.url.path
    )

# Request Validation Errors Handler (Pydantic / Form parsing)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        formatted_errors.append({
            "field": field,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error")
        })

    logger.warning(f"Validation error on {request.url.path}: {formatted_errors}")
    return format_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="Request payload or parameters failed validation.",
        path=request.url.path,
        details=formatted_errors
    )

# Fallback Generic Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return format_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        message="An internal server error occurred.",
        path=request.url.path,
        details=str(exc) if config.DEBUG else None
    )

# Register API Routers
app.include_router(stt_router)
app.include_router(tts_router)
app.include_router(voice_cmd_router)
app.include_router(ws_router)

# Health & Root Endpoints
@app.get("/", summary="API Root & Status", tags=["General"])
async def root():
    return {
        "service": "Speech Recognition & Voice Interaction REST API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "endpoints": {
            "transcribe": "POST /api/speech/transcribe",
            "voice_command": "POST /api/speech/command",
            "text_intent": "POST /api/speech/intent",
            "command_history": "GET /api/speech/history",
            "text_to_speech": "POST /api/tts/speak",
            "voice_stream_ws": "WS /ws/voice-stream"
        }
    }

@app.get("/health", summary="Health Check", tags=["General"])
async def health_check():
    is_model_loaded = (
        getattr(app.state, "whisper_service", None) is not None
        and app.state.whisper_service.model is not None
    )
    ollama_connected = await check_ollama_status()

    return {
        "status": "ok",
        "whisper": "loaded" if is_model_loaded else "unloaded",
        "ollama": "connected" if ollama_connected else "disconnected",
        "model": config.OLLAMA_MODEL
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.API_HOST, port=config.API_PORT, reload=config.DEBUG)
