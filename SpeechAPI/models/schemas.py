from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class TranscribeResponse(BaseModel):
    text: str = Field(..., description="Transcribed text from speech")
    confidence: float = Field(..., description="Model confidence score between 0.0 and 1.0")
    language: str = Field(..., description="Detected audio language code (e.g., 'en', 'ur', 'roman_urdu')")
    processing_time: float = Field(..., description="Audio processing duration in seconds")

class CommandResponse(BaseModel):
    raw_text: str = Field(..., description="Transcribed spoken user text")
    intent: str = Field(..., description="Extracted user intent")
    action: str = Field(..., description="Action identifier or status")
    response: str = Field(..., description="System verbal/text feedback")
    success: bool = Field(..., description="Whether the command was successfully processed")
    timestamp: str = Field(..., description="ISO 8601 timestamp of command execution")

class IntentRequest(BaseModel):
    text: str = Field(..., description="Raw text command to analyze", min_length=1)

class IntentResponse(BaseModel):
    input: str = Field(..., description="Input text provided")
    intent: str = Field(..., description="Resolved intent key")
    confidence: float = Field(..., description="Fuzzy match confidence score (0.0 to 1.0)")
    language: str = Field(..., description="Detected text language: en, ur, or roman_urdu")

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to be spoken / converted to audio", min_length=1)
    language: Optional[str] = Field("en", description="Language code (e.g., 'en', 'ur')")
    slow: Optional[bool] = Field(False, description="Speak slowly if supported")

class HistoryResponse(BaseModel):
    total: int = Field(..., description="Number of history items returned")
    history: List[Dict[str, Any]] = Field(..., description="List of recorded voice commands")

class StreamEvent(BaseModel):
    event: str = Field(..., description="Stream event type: transcribing, recognized, executing, done, error")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Event payload")
