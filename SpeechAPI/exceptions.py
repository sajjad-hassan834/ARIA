from typing import Optional, Any, Dict

class SpeechAPIException(Exception):
    """Base exception class for SpeechAPI."""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class ModelNotLoadedException(SpeechAPIException):
    """Raised when Whisper speech model is not ready or failed to load."""
    def __init__(self, message: str = "Speech recognition model is not loaded or currently unavailable.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=503,
            error_code="MODEL_NOT_READY",
            details=details
        )


class AudioFormatNotSupportedException(SpeechAPIException):
    """Raised when uploaded audio format/extension is unsupported."""
    def __init__(self, extension: str, supported: list):
        super().__init__(
            message=f"Audio format '{extension}' is not supported. Allowed formats: {supported}",
            status_code=400,
            error_code="UNSUPPORTED_AUDIO_FORMAT",
            details={"extension": extension, "supported_formats": supported}
        )


class AudioProcessingException(SpeechAPIException):
    """Raised when audio decoding, conversion, or reading fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Audio processing error: {message}",
            status_code=422,
            error_code="AUDIO_PROCESSING_ERROR",
            details=details
        )


class TTSSynthesisException(SpeechAPIException):
    """Raised when Text-to-Speech synthesis fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Text-to-Speech synthesis failed: {message}",
            status_code=500,
            error_code="TTS_SYNTHESIS_ERROR",
            details=details
        )
