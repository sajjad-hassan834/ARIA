"""
ARIA Complete System Launcher
Launches all backend services (Speech, Brain, Browser, Desktop, File, Gateway)
and the ARIA Frontend in one command.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

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
    print("         LAUNCHING COMPLETE ARIA AI SYSTEM (FULL STACK)        ")
    print("=" * 65)

    # Free port 3000 in case an old Vite server is still running
    free_port(3000)

    processes = []

    try:
        # 1. Start all 6 Backend Microservices (Ports 8000-8080)
        print("[*] Starting all ARIA backend services via start_backend.py...")
        backend_proc = subprocess.Popen(
            [sys.executable, "start_backend.py"],
            cwd=ROOT_DIR,
            shell=False
        )
        processes.append(("Backend Services", backend_proc))

        # 2. Wait 5 seconds for backend microservices to initialize
        time.sleep(5.0)

        # 3. Start Frontend Dev Server (Port 3000)
        print("[*] Starting ARIA Cyber Frontend (Port 3000)...")
        frontend_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=ROOT_DIR / "ARIAFrontend",
            shell=True
        )
        processes.append(("ARIA Frontend", frontend_proc))

        print("\n" + "=" * 65)
        print("  ARIA SYSTEM IS FULLY ONLINE & READY!")
        print("  -> Cyber HUD UI       : http://localhost:3000")
        print("  -> Gateway Master API : http://127.0.0.1:8080")
        print("  -> Interactive Docs   : http://127.0.0.1:8080/docs")
        print("=" * 65)
        print("Press Ctrl+C to shut down all frontend and backend services.\n")

        for _, proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        print("\n[*] Shutting down ARIA system...")
        for name, proc in processes:
            try:
                proc.terminate()
            except Exception:
                pass
        print("[+] All ARIA services stopped cleanly.")

if __name__ == "__main__":
    main()
