import os
import re
import shutil
import logging
import math
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
import config

logger = logging.getLogger("speech_api.whisper")

def ensure_ffmpeg_available():
    """Ensure ffmpeg binary is in system PATH, using imageio-ffmpeg as seamless Windows provider."""
    # Check if ffmpeg is already directly accessible
    if shutil.which("ffmpeg"):
        logger.info("Found system ffmpeg in PATH.")
        return

    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        bin_path = Path(ffmpeg_bin)
        bin_dir = bin_path.parent
        target_ffmpeg = bin_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")

        if not target_ffmpeg.exists():
            shutil.copyfile(bin_path, target_ffmpeg)
            logger.info(f"Created ffmpeg binary alias at {target_ffmpeg}")

        if str(bin_dir) not in os.environ.get("PATH", ""):
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"Added {bin_dir} to PATH for Whisper ffmpeg decoder.")
    except Exception as e:
        logger.warning(f"Could not automatically configure ffmpeg from imageio-ffmpeg: {e}")

# Run ffmpeg configuration check on module load
ensure_ffmpeg_available()

ROMAN_URDU_WORDS = {
    "kholo", "band", "karo", "krdo", "kro", "awaz", "awaaz", "barha", "barhao",
    "teez", "kam", "dheemi", "ghatao", "lo", "tasveer", "chalao", "roko",
    "kya", "hai", "waqt", "salam", "haal", "kaise", "batao", "sunao", "lelo"
}

class WhisperService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WhisperService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = config.WHISPER_MODEL):
        if self._initialized:
            return
        self.model_name = model_name
        self.model = None
        self._initialized = True

    def load_model(self) -> None:
        """Load Whisper model once into memory."""
        if self.model is None:
            import whisper
            logger.info(f"Loading Whisper '{self.model_name}' model into memory...")
            self.model = whisper.load_model(self.model_name)
            logger.info(f"Whisper '{self.model_name}' model loaded successfully.")

    def detect_roman_urdu(self, text: str, whisper_detected_lang: str) -> str:
        """Heuristic auto-detection for Roman Urdu vs Urdu vs English."""
        if re.search(r"[\u0600-\u06FF]", text):
            return "ur"

        tokens = set(re.findall(r"\b\w+\b", text.lower()))
        if tokens.intersection(ROMAN_URDU_WORDS):
            return "roman_urdu"

        return whisper_detected_lang or "en"

    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe an audio file using cached Whisper model.
        Returns:
            {
                "text": str,
                "confidence": float,
                "language": str
            }
        """
        if self.model is None:
            self.load_model()

        # Call whisper transcribe
        transcribe_args = {"fp16": False}
        if language:
            transcribe_args["language"] = language

        result = self.model.transcribe(audio_file_path, **transcribe_args)
        raw_text = result.get("text", "").strip()
        detected_lang = result.get("language", "en")

        # Calculate confidence from segment log probabilities
        segments = result.get("segments", [])
        if segments:
            logprobs = [s.get("avg_logprob", -0.5) for s in segments if "avg_logprob" in s]
            if logprobs:
                avg_logprob = sum(logprobs) / len(logprobs)
                confidence = round(float(math.exp(avg_logprob)), 2)
                confidence = min(max(confidence, 0.05), 0.99)
            else:
                confidence = 0.85
        else:
            confidence = 0.85 if raw_text else 0.0

        resolved_lang = self.detect_roman_urdu(raw_text, detected_lang)

        return {
            "text": raw_text,
            "confidence": confidence,
            "language": resolved_lang
        }


# Singleton service instance
whisper_service = WhisperService()
