import os
import subprocess
import psutil
from typing import Dict, Optional, Tuple

APPS: Dict[str, str] = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "chrome": "chrome.exe",
    "vs_code": "code",
    "vscode": "code",
    "word": "winword.exe",
    "excel": "excel.exe",
    "task_manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
}

# Mapping of known process names for termination
PROCESS_NAMES: Dict[str, list[str]] = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe", "calculatorapp.exe", "calculator.exe"],
    "paint": ["mspaint.exe", "paintstudio.view.exe"],
    "explorer": ["explorer.exe"],
    "chrome": ["chrome.exe"],
    "vs_code": ["code.exe"],
    "vscode": ["code.exe"],
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "task_manager": ["taskmgr.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
}


def open_app(app_name: str) -> Tuple[bool, str]:
    normalized_key = app_name.strip().lower()
    exe = APPS.get(normalized_key)
    if not exe:
        # Check if user provided an executable directly or known name
        return False, f"Unsupported application '{app_name}'. Supported: {', '.join(sorted(APPS.keys()))}"

    try:
        # Use shell=True to support PATH resolution (like 'code') on Windows
        subprocess.Popen(exe, shell=True)
        return True, f"Successfully launched {app_name} ({exe})"
    except Exception as e:
        return False, f"Failed to launch {app_name}: {str(e)}"


def close_app(app_name: str) -> Tuple[bool, str]:
    normalized_key = app_name.strip().lower()
    search_targets = PROCESS_NAMES.get(normalized_key, [normalized_key])

    closed_count = 0
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pname = (proc.info.get("name") or "").lower()
            for target in search_targets:
                if target in pname:
                    proc.terminate()
                    closed_count += 1
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if closed_count > 0:
        return True, f"Closed {closed_count} process(es) matching '{app_name}'"
    return False, f"No running processes found for '{app_name}'"
