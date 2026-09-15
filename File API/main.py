import sys
from pathlib import Path

# Ensure FileAPI folder is in sys.path
file_api_dir = Path(__file__).resolve().parent / "FileAPI"
if str(file_api_dir) not in sys.path:
    sys.path.insert(0, str(file_api_dir))

from FileAPI.main import app  # noqa: F401
