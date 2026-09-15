from typing import Optional, Tuple
import pyautogui
from config import PYAUTOGUI_FAILSAFE, PYAUTOGUI_PAUSE

pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = PYAUTOGUI_PAUSE

# Map speed setting to character write interval in seconds
SPEED_INTERVALS = {

    "slow": 0.1,
    "normal": 0.03,
    "fast": 0.005,
}


def type_text(text: str, speed: str = "normal") -> Tuple[bool, str]:
    try:
        interval = SPEED_INTERVALS.get(speed.lower(), 0.03)
        pyautogui.write(text, interval=interval)
        return True, f"Typed {len(text)} characters at speed '{speed}'"
    except Exception as e:
        return False, f"Failed to type text: {str(e)}"


def click_at(x: int, y: int, button: str = "left") -> Tuple[bool, str]:
    try:
        btn = button.strip().lower()
        screen_w, screen_h = pyautogui.size()
        if x < 0 or x > screen_w or y < 0 or y > screen_h:
            return False, f"Coordinates ({x}, {y}) are outside screen boundaries ({screen_w}x{screen_h})"

        if btn == "double":
            pyautogui.doubleClick(x=x, y=y)
            return True, f"Double-clicked at ({x}, {y})"
        elif btn in ["left", "right", "middle"]:
            pyautogui.click(x=x, y=y, button=btn)
            return True, f"Clicked ({btn}) at ({x}, {y})"
        else:
            return False, f"Unsupported mouse button '{button}'. Valid: left, right, middle, double"
    except Exception as e:
        return False, f"Failed to click at ({x}, {y}): {str(e)}"


def scroll_screen(direction: str = "down", amount: int = 3) -> Tuple[bool, str]:
    try:
        dir_clean = direction.strip().lower()
        amt = abs(amount or 3)

        # In pyautogui.scroll, positive numbers scroll up, negative scroll down.
        # Typically on Windows 1 click wheel notch = ~100 to 120 units or direct integer.
        # We multiply by 100 for visible smooth scrolling.
        scroll_units = amt * 100
        if dir_clean in ["down", "d"]:
            pyautogui.scroll(-scroll_units)
            return True, f"Scrolled down by {amt} steps"
        elif dir_clean in ["up", "u"]:
            pyautogui.scroll(scroll_units)
            return True, f"Scrolled up by {amt} steps"
        else:
            return False, f"Invalid scroll direction '{direction}'. Valid: up, down"
    except Exception as e:
        return False, f"Failed to scroll {direction}: {str(e)}"
