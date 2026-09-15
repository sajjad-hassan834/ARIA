"""
ARIA TTS Service — Queued, non-blocking voice response.
Uses a background worker thread so speech never blocks the event loop.
"""
import logging
import queue
import threading

logger = logging.getLogger("gateway.tts")

try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not installed — voice response disabled. Run: pip install pyttsx3")


class _TTSWorker:
    """Singleton background thread that drains a speech queue."""

    def __init__(self):
        self._q: queue.Queue[str] = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True, name="ARIA-TTS")
        self._thread.start()

    def enqueue(self, text: str):
        if text and text.strip():
            self._q.put(text.strip())

    def _run(self):
        while True:
            try:
                text = self._q.get(timeout=2)
                self._speak(text)
            except queue.Empty:
                continue
            except Exception as e:
                logger.warning(f"TTS worker error: {e}")

    @staticmethod
    def _speak(text: str):
        if not _PYTTSX3_AVAILABLE:
            return
        try:
            engine = pyttsx3.init()

            # Prefer a clear English/Zira voice if available
            voices = engine.getProperty("voices") or []
            for voice in voices:
                name_lower = (voice.name or "").lower()
                if any(k in name_lower for k in ["zira", "david", "english", "en-us"]):
                    engine.setProperty("voice", voice.id)
                    break

            engine.setProperty("rate", 155)
            engine.setProperty("volume", 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            logger.warning(f"pyttsx3 speak error: {e}")


# ── Singleton instance ──────────────────────────────────────────────────────
_worker = _TTSWorker()


def speak(text: str):
    """
    Public API — enqueue text for async speech. Returns immediately.
    Call this after every successful or failed command execution.
    """
    _worker.enqueue(text)
