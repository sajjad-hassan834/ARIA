"""
ARIA Backend Master Launcher
Launches all ARIA backend microservices concurrently:
  - Speech API  (Port 8000)
  - Brain API   (Port 8001)
  - Browser API (Port 8002)
  - Desktop API (Port 8003)
  - File API    (Port 8004)
  - Gateway API (Port 8080)
"""

import os
import sys
import time
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def get_python_executable(service_dir: Path) -> str:
    """Find virtualenv python executable if present, otherwise global python."""
    candidates = [
        service_dir / "venv" / "Scripts" / "python.exe",
        service_dir / ".venv" / "Scripts" / "python.exe",
        ROOT_DIR / "venv" / "Scripts" / "python.exe",
        service_dir.parent / "venv" / "Scripts" / "python.exe",
        service_dir.parent / ".venv" / "Scripts" / "python.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable

SERVICES = [
    {
        "name": "Speech API",
        "port": 8000,
        "cwd": ROOT_DIR / "SpeechAPI",
        "script": "main.py",
    },
    {
        "name": "Brain API",
        "port": 8001,
        "cwd": ROOT_DIR / "BrainAPI",
        "script": "main.py",
    },
    {
        "name": "Browser API",
        "port": 8002,
        "cwd": ROOT_DIR / "Browser API",
        "script": "main.py",
    },
    {
        "name": "Desktop API",
        "port": 8003,
        "cwd": ROOT_DIR / "DesktopAPI",
        "script": "main.py",
    },
    {
        "name": "File API",
        "port": 8004,
        "cwd": ROOT_DIR / "File API" / "FileAPI",
        "script": "main.py",
    },
    {
        "name": "Gateway Master API",
        "port": 8080,
        "cwd": ROOT_DIR / "GatewayAPI",
        "script": "main.py",
    },
]

def free_port(port: int):
    """Release port if held by a previous process on Windows."""
    try:
        cmd = f'netstat -ano | findstr :{port}'
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        for line in output.strip().splitlines():
            parts = line.split()
            if len(parts) >= 5 and "LISTENING" in line.upper():
                pid = parts[-1]
                if int(pid) != os.getpid() and int(pid) > 4:
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def main():
    print("=" * 65)
    print("           ARIA MULTI-AGENT BACKEND LAUNCHER             ")
    print("=" * 65)

    # 1. Clean any zombie processes on the 6 ports
    print("[*] Checking and freeing ARIA ports (8000-8080)...")
    for svc in SERVICES:
        free_port(svc["port"])
    time.sleep(1.0)

    processes = []

    try:
        # 2. Start all satellite microservices first
        for svc in SERVICES[:-1]:
            python_bin = get_python_executable(svc["cwd"])
            print(f"[*] Starting {svc['name']:<18} on Port {svc['port']} with {Path(python_bin).name}...")
            p = subprocess.Popen(
                [python_bin, svc["script"]],
                cwd=svc["cwd"],
                shell=False
            )
            processes.append((svc["name"], p))
            time.sleep(1.0)

        print("\n[*] Waiting 4s for satellite services to initialize...")
        time.sleep(4.0)

        # 3. Start Gateway API last so its startup health probe finds them all online!
        gateway_svc = SERVICES[-1]
        gateway_bin = get_python_executable(gateway_svc["cwd"])
        print(f"[*] Starting {gateway_svc['name']:<18} on Port {gateway_svc['port']}...\n")
        gateway_p = subprocess.Popen(
            [gateway_bin, gateway_svc["script"]],
            cwd=gateway_svc["cwd"],
            shell=False
        )
        processes.append((gateway_svc["name"], gateway_p))

        print("=" * 65)
        print("  ALL 6 BACKEND SERVICES ARE RUNNING CONCURRENTLY!")
        print("  -> Gateway Master API : http://127.0.0.1:8080")
        print("  -> Gateway Docs (UI)  : http://127.0.0.1:8080/docs")
        print("  -> Frontend UI        : http://localhost:3000")
        print("=" * 65)
        print("Press Ctrl+C at any time to shut down all APIs cleanly.\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Stopping all ARIA backend services...")
        for name, p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        print("[+] All services stopped cleanly.")

if __name__ == "__main__":
    main()
