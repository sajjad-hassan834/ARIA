import io
import logging
from typing import Optional
from gtts import gTTS

logger = logging.getLogger("speech_api.tts")

class TTSService:
    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang

    def text_to_speech_mp3(self, text: str, lang: Optional[str] = None, slow: bool = False) -> io.BytesIO:
        """
        Synthesize text into speech MP3 bytes buffer using gTTS.
        Falls back to pyttsx3 if network/gTTS request fails.
        """
        language = (lang or self.default_lang).lower()
        # gTTS standard languages: en, ur, hi, ar, fr, es, etc.
        # If roman_urdu is requested, map to ur or en for gTTS
        if language in ["roman_urdu", "roman-urdu"]:
            language = "ur"

        audio_buffer = io.BytesIO()
        try:
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            logger.warning(f"gTTS generation failed ({e}), attempting fallback engine...")
            return self._pyttsx3_fallback(text)

    def _pyttsx3_fallback(self, text: str) -> io.BytesIO:
        """Fallback to local pyttsx3 offline engine if gTTS fails."""
        import tempfile
        import pyttsx3
        from pathlib import Path

        temp_path = None
        try:
            engine = pyttsx3.init()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_path = Path(temp_file.name)

            engine.save_to_file(text, str(temp_path))
            engine.runAndWait()

            audio_buffer = io.BytesIO()
            with open(temp_path, "rb") as f:
                audio_buffer.write(f.read())
            audio_buffer.seek(0)
            return audio_buffer
        finally:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass


tts_service = TTSService()
