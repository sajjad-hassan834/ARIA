import sys
from pathlib import Path

# Add FileAPI folder to python path
file_api_dir = Path(__file__).resolve().parent / "FileAPI"
if str(file_api_dir) not in sys.path:
    sys.path.insert(0, str(file_api_dir))

import uvicorn
from FileAPI.config import PORT

if __name__ == "__main__":
    print(f"Starting ARIA File API on http://127.0.0.1:{PORT}")
    uvicorn.run("FileAPI.main:app", host="0.0.0.0", port=PORT, reload=True)
