import os
from pathlib import Path
from dotenv import load_dotenv

# Root of the ARIA Project
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load master .env from ARIA project root
ENV_FILE = ROOT_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

# Server Defaults
DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", 60.0))
HEALTH_TIMEOUT = float(os.getenv("HEALTH_TIMEOUT", 3.0))

# Subsystem Port Mapping
PORTS = {
    "speech_api": int(os.getenv("SPEECH_PORT", 8000)),
    "brain_api": int(os.getenv("BRAIN_PORT", 8001)),
    "browser_api": int(os.getenv("BROWSER_PORT", 8002)),
    "desktop_api": int(os.getenv("DESKTOP_PORT", 8003)),
    "file_api": int(os.getenv("FILE_PORT", 8004)),
    "gateway_api": int(os.getenv("PORT", os.getenv("GATEWAY_PORT", 8080))),
}

# Subsystem API URLs
SPEECH_API_URL = os.getenv("SPEECH_API_URL", f"http://127.0.0.1:{PORTS['speech_api']}")
BRAIN_API_URL = os.getenv("BRAIN_API_URL", f"http://127.0.0.1:{PORTS['brain_api']}")
BROWSER_API_URL = os.getenv("BROWSER_API_URL", f"http://127.0.0.1:{PORTS['browser_api']}")
DESKTOP_API_URL = os.getenv("DESKTOP_API_URL", f"http://127.0.0.1:{PORTS['desktop_api']}")
FILE_API_URL = os.getenv("FILE_API_URL", f"http://127.0.0.1:{PORTS['file_api']}")
GATEWAY_API_URL = os.getenv("GATEWAY_API_URL", f"http://127.0.0.1:{PORTS['gateway_api']}")

# Centralized API Map
APIS = {
    "speech_api": {"url": SPEECH_API_URL, "port": PORTS["speech_api"]},
    "brain_api": {"url": BRAIN_API_URL, "port": PORTS["brain_api"]},
    "browser_api": {"url": BROWSER_API_URL, "port": PORTS["browser_api"]},
    "desktop_api": {"url": DESKTOP_API_URL, "port": PORTS["desktop_api"]},
    "file_api": {"url": FILE_API_URL, "port": PORTS["file_api"]},
}

# Subsystem Specific Settings

HEADLESS = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 45000))

PYAUTOGUI_FAILSAFE = os.getenv("PYAUTOGUI_FAILSAFE", "false").lower() in ("true", "1")
PYAUTOGUI_PAUSE = float(os.getenv("PYAUTOGUI_PAUSE", "0.05"))

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
SPEECH_LANGUAGE = os.getenv("SPEECH_LANGUAGE", "en")

# OpenAI API Key (set in .env as OPENAI_API_KEY or openai_api_key)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key", "")
