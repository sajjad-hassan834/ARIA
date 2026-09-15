"""
ARIA Root Application Entrypoint
Suitable for cloud deployment platforms like Railway, Render, Fly.io.
Launches ARIA services via start_backend.py.
"""
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

if __name__ == "__main__":
    script = ROOT_DIR / "start_backend.py"
    subprocess.run([sys.executable, str(script)], cwd=str(ROOT_DIR))
