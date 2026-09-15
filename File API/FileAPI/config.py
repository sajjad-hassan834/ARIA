import os
import sys
from pathlib import Path

# Ensure ARIA root is on sys.path for global common module
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import common

PORT = common.PORTS["file_api"]
BRAIN_API_URL = common.BRAIN_API_URL


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "file_history.json"

# Protected system directories whose contents must never be deleted
PROTECTED_SYSTEM_DIRS = [
    Path(os.environ.get("SystemRoot", r"C:\Windows")).resolve(),
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")).resolve(),
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")).resolve(),
    Path(os.environ.get("ProgramData", r"C:\ProgramData")).resolve(),
]

# Exact root paths that cannot be deleted directly (user root, users root, etc.)
PROTECTED_EXACT_ROOTS = [
    Path(os.path.expanduser("~")).resolve(),
    Path(os.path.expanduser("~")).parent.resolve(),
]
