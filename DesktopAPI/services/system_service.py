import datetime
import os
from pathlib import Path
from typing import Optional, Tuple
import pyautogui

from config import PYAUTOGUI_FAILSAFE, PYAUTOGUI_PAUSE

# Safety configuration for PyAutoGUI
pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = PYAUTOGUI_PAUSE


def volume_up(repeats: int = 5) -> Tuple[bool, str]:
    try:
        count = max(1, min(repeats, 50))
        for _ in range(count):
            pyautogui.press("volumeup")
        return True, f"Increased volume by {count} steps"
    except Exception as e:
        return False, f"Failed to increase volume: {str(e)}"


def volume_down(repeats: int = 5) -> Tuple[bool, str]:
    try:
        count = max(1, min(repeats, 50))
        for _ in range(count):
            pyautogui.press("volumedown")
        return True, f"Decreased volume by {count} steps"
    except Exception as e:
        return False, f"Failed to decrease volume: {str(e)}"


def volume_mute() -> Tuple[bool, str]:
    try:
        pyautogui.press("volumemute")
        return True, "Toggled volume mute"
    except Exception as e:
        return False, f"Failed to mute volume: {str(e)}"


def handle_volume(action: str, level: Optional[int] = None) -> Tuple[bool, str]:
    action_lower = action.strip().lower()
    repeats = 5
    if level is not None and level > 0:
        # If user provides a level, use it as steps or 5 by default
        repeats = level if level <= 50 else int(level / 2)

    if action_lower in ["up", "increase", "raise"]:
        return volume_up(repeats)
    elif action_lower in ["down", "decrease", "lower"]:
        return volume_down(repeats)
    elif action_lower in ["mute", "toggle_mute", "unmute"]:
        return volume_mute()
    else:
        return False, f"Invalid volume action '{action}'. Valid: up, down, mute"



def capture_screenshot(save_to: str = "desktop") -> Tuple[bool, str, Optional[str]]:
    try:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if not save_to or save_to.strip().lower() == "desktop":
            target_dir = Path.home() / "Desktop"
        else:
            target_dir = Path(os.path.expanduser(save_to.strip()))

        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"screenshot_{ts}.png"

        img = pyautogui.screenshot()
        img.save(str(file_path))
        return True, f"Screenshot saved successfully to {file_path}", str(file_path)
    except Exception as e:
        return False, f"Failed to capture screenshot: {str(e)}", None


def shutdown(confirm: bool = False) -> Tuple[bool, str]:
    if not confirm:
        return False, "Shutdown requires confirmation. Please set 'confirm': true in your request."
    os.system("shutdown /s /t 10")
    return True, "System shutdown initiated (10s delay)"


def restart(confirm: bool = False) -> Tuple[bool, str]:
    if not confirm:
        return False, "Restart requires confirmation. Please set 'confirm': true in your request."
    os.system("shutdown /r /t 10")
    return True, "System restart initiated (10s delay)"


def lock() -> Tuple[bool, str]:
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return True, "Workstation locked"


def sleep() -> Tuple[bool, str]:
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return True, "System sleep initiated"


def handle_power(action: str, confirm: bool = False) -> Tuple[bool, str]:
    action_lower = action.strip().lower()
    if action_lower == "shutdown":
        return shutdown(confirm=confirm)
    elif action_lower == "restart":
        return restart(confirm=confirm)
    elif action_lower == "lock":
        return lock()
    elif action_lower == "sleep":
        return sleep()
    else:
        return False, f"Unknown power action '{action}'. Valid: shutdown, restart, sleep, lock"
