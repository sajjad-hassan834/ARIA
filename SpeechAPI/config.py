import sys
from pathlib import Path

# Ensure ARIA root is on sys.path for global common module
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import common

BASE_DIR = Path(__file__).resolve().parent

# Server Config from Global Common
API_HOST = common.DEFAULT_HOST
API_PORT = common.PORTS["speech_api"]
DEBUG = True

# Whisper Speech Recognition Config
WHISPER_MODEL = common.WHISPER_MODEL
LANGUAGE = common.SPEECH_LANGUAGE
SUPPORTED_AUDIO_EXTENSIONS = [".wav", ".mp3", ".webm", ".m4a", ".ogg", ".flac"]

# NLU & Intent Matching Config
FUZZY_THRESHOLD = 75

# LLM / Ollama Fallback Config
USE_LLM_FALLBACK = True
OLLAMA_MODEL = "phi3:mini"
OLLAMA_HOST = "http://localhost:11434"


# Command Processor & History Config
MAX_HISTORY = 50
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "command_history.json"

# Text to Speech Config
DEFAULT_TTS_LANG = "en"
AUDIO_OUTPUT_DIR = BASE_DIR / "temp_audio"
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
