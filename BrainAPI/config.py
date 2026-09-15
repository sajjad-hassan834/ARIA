import sys
from pathlib import Path

# Ensure ARIA root is on sys.path for global common module
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import common

BASE_DIR = Path(__file__).resolve().parent

# Server Config from Global Common
PORT = common.PORTS["brain_api"]
HOST = common.DEFAULT_HOST

# Subsystem API URLs from Global Common
SPEECH_API_URL = common.SPEECH_API_URL
BROWSER_API_URL = common.BROWSER_API_URL
DESKTOP_API_URL = common.DESKTOP_API_URL
FILE_API_URL = common.FILE_API_URL

# Ollama Config for phi3:mini
OLLAMA_MODEL = "phi3:mini"
OLLAMA_HOST = "http://localhost:11434"
USE_LLM = True


# Data Directories
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONTEXT_HISTORY_FILE = DATA_DIR / "context_history.json"
