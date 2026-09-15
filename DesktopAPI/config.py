import sys
from pathlib import Path

# Ensure ARIA root is in sys.path for global common module
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import common

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ACTION_HISTORY_FILE = DATA_DIR / "action_history.json"

PORT = common.PORTS["desktop_api"]
BRAIN_API_URL = common.BRAIN_API_URL
HOST = common.DEFAULT_HOST
PYAUTOGUI_FAILSAFE = common.PYAUTOGUI_FAILSAFE
PYAUTOGUI_PAUSE = common.PYAUTOGUI_PAUSE
