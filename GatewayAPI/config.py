import sys
from pathlib import Path

# Ensure ARIA root is in sys.path for global common module
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import common

# Server Settings from Global Common Config
HOST = common.DEFAULT_HOST
PORT = common.PORTS["gateway_api"]

# Subsystem Endpoints from Global Common Config
SPEECH_API = common.SPEECH_API_URL
BRAIN_API = common.BRAIN_API_URL
BROWSER_API = common.BROWSER_API_URL
DESKTOP_API = common.DESKTOP_API_URL
FILE_API = common.FILE_API_URL

APIS = common.APIS
PORTS = common.PORTS

# Storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "gateway_history.json"
MAX_HISTORY_ITEMS = 50

# Network Settings
DEFAULT_TIMEOUT = common.DEFAULT_TIMEOUT
HEALTH_TIMEOUT = common.HEALTH_TIMEOUT
MAX_RETRIES = 1
