import sys
from pathlib import Path

# Ensure ARIA root is on sys.path for global common module
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import common

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
HISTORY_FILE = DATA_DIR / "browser_history.json"

# Ensure data and screenshot directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

PORT = common.PORTS["browser_api"]
BRAIN_API_URL = common.BRAIN_API_URL
HEADLESS = common.HEADLESS

# Navigation & selector timeouts
DEFAULT_TIMEOUT = int(common.DEFAULT_TIMEOUT * 1000)
PAGE_LOAD_TIMEOUT = common.PAGE_LOAD_TIMEOUT
