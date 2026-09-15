import asyncio
import json
import logging
import time
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pyautogui

from config import HISTORY_FILE, SCREENSHOT_DIR

logger = logging.getLogger("browser_service")
logging.basicConfig(level=logging.INFO)


class BrowserService:
    """
    Browser automation service for ARIA.
    Uses the system default browser (webbrowser) and pyautogui
    so that user sessions, accounts, and cookies are preserved.
    """
    def __init__(self):
        self.is_active = True
        self.browser = None
        self.page = None
        self.current_url = "about:blank"
        self._lock = asyncio.Lock()

    async def start(self):
        """Startup hook - confirms default browser handler is ready."""
        logger.info("Browser service initialized (using default system browser).")
        self.is_active = True

    async def stop(self):
        """Shutdown hook."""
        logger.info("Browser service stopped.")
        self.is_active = False

    async def goto(self, url: str) -> Dict[str, Any]:
        """Navigates to the specified URL in the system default browser."""
        start_time = time.perf_counter()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        self.current_url = url
        logger.info(f"Opening system browser with URL: {url}")
        webbrowser.open(url)
        await asyncio.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        time_str = f"{elapsed:.2f}s"
        await self.record_history("opened", {"url": url}, status="success", elapsed=time_str)

        return {
            "status": "success",
            "action": "opened",
            "url": url,
            "time": time_str,
        }

    async def search_youtube(self, query: str) -> Dict[str, Any]:
        """Searches YouTube for query using the default system browser."""
        start_time = time.perf_counter()
        clean_query = query.strip() if query else "trending music"
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean_query)}"
        self.current_url = url

        logger.info(f"Searching YouTube for '{clean_query}': {url}")
        webbrowser.open(url)
        await asyncio.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        time_str = f"{elapsed:.2f}s"
        details = {"platform": "youtube", "query": clean_query, "url": url}
        await self.record_history("search", details, status="success", elapsed=time_str)

        return {
            "status": "success",
            "action": "searched",
            "details": details,
            "time": time_str,
        }

    async def search_google(self, query: str) -> Dict[str, Any]:
        """Searches Google for query using the default system browser."""
        start_time = time.perf_counter()
        clean_query = query.strip() if query else "Google"
        url = f"https://www.google.com/search?q={urllib.parse.quote(clean_query)}"
        self.current_url = url

        logger.info(f"Searching Google for '{clean_query}': {url}")
        webbrowser.open(url)
        await asyncio.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        time_str = f"{elapsed:.2f}s"
        details = {"platform": "google", "query": clean_query, "url": url}
        await self.record_history("search", details, status="success", elapsed=time_str)

        return {
            "status": "success",
            "action": "searched",
            "details": details,
            "time": time_str,
        }

    async def open_whatsapp_web(self) -> Dict[str, Any]:
        """Opens WhatsApp Web in existing browser session."""
        return await self.goto("https://web.whatsapp.com")

    async def open_gmail(self) -> Dict[str, Any]:
        """Opens Gmail in existing browser session."""
        return await self.goto("https://mail.google.com")

    async def open_facebook(self) -> Dict[str, Any]:
        """Opens Facebook in existing browser session."""
        return await self.goto("https://facebook.com")

    async def click_first_result(self) -> Dict[str, Any]:
        """Simulates clicking or focusing the first search result."""
        start_time = time.perf_counter()
        try:
            # Press Tab and Enter to navigate/open first item, or click near center-left
            pyautogui.press("enter")
        except Exception as e:
            logger.warning(f"click_first_result simulation warning: {e}")

        elapsed = time.perf_counter() - start_time
        time_str = f"{elapsed:.2f}s"
        details = {"target": "first_result", "url": self.current_url}
        await self.record_history("click", details, status="success", elapsed=time_str)
        return {"status": "success", "action": "clicked", "details": details, "time": time_str}

    async def click(self, target: str) -> Dict[str, Any]:
        """Handles click interactions on the active browser window."""
        start_time = time.perf_counter()
        target_lower = target.lower().strip()

        if target_lower in ("first_result", "first", "result"):
            return await self.click_first_result()
        if target_lower in ("play", "pause", "play_pause"):
            return await self.toggle_media()

        try:
            pyautogui.press("enter")
        except Exception:
            pass

        elapsed = time.perf_counter() - start_time
        time_str = f"{elapsed:.2f}s"
        details = {"target": target, "url": self.current_url}
        await self.record_history("click", details, status="success", elapsed=time_str)
        return {"status": "success", "action": "clicked", "details": details, "time": time_str}

    async def toggle_media(self) -> Dict[str, Any]:
        """Toggles media play/pause by sending 'k' (YouTube standard) or Space."""
        start_time = time.perf_counter()
        try:
            # 'k' is the universal play/pause shortcut for YouTube
            pyautogui.press("k")
        except Exception as e:
            logger.warning(f"toggle_media failed: {e}")

        elapsed = time.perf_counter() - start_time
        return {
            "status": "success",
            "action": "media_toggled",
            "details": {"shortcut": "k"},
            "time": f"{elapsed:.2f}s",
        }

    async def take_screenshot(self, filename: Optional[str] = None, full_page: bool = False) -> str:
        """Captures a screenshot of the current screen."""
        if not filename:
            timestamp = int(time.time() * 1000)
            filename = f"screenshot_{timestamp}.png"
        elif not filename.endswith(".png"):
            filename += ".png"

        filepath = SCREENSHOT_DIR / filename
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
        except Exception as e:
            logger.error(f"pyautogui screenshot failed: {e}")
            raise e

        await self.record_history(
            "screenshot",
            {"file": filename, "path": str(filepath), "url": self.current_url},
            status="success",
            elapsed="0.0s",
        )
        return str(filepath)

    async def execute_plan(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executes a multi-step sequence from Brain API."""
        start_total = time.perf_counter()
        results = []
        steps_executed = 0
        steps_failed = 0

        for step in steps:
            step_num = step.get("step", len(results) + 1)
            action = step.get("action", "").lower().strip()
            step_start = time.perf_counter()

            try:
                if action in ("goto_url", "open_url", "open", "goto", "open_browser"):
                    target = step.get("target") or step.get("url", "google.com")
                    if not target.startswith("http://") and not target.startswith("https://"):
                        target = "https://" + target
                    await self.goto(target)

                elif action == "search_youtube":
                    query = step.get("query") or step.get("target", "")
                    await self.search_youtube(query)

                elif action == "search_google":
                    query = step.get("query") or step.get("target", "")
                    await self.search_google(query)

                elif action == "search":
                    query = step.get("query", "")
                    platform = step.get("platform", "").lower()
                    target_str = str(step.get("target", "")).lower()
                    if "youtube" in platform or "youtube" in target_str:
                        await self.search_youtube(query)
                    else:
                        await self.search_google(query)

                elif action in ("open_whatsapp", "open_whatsapp_web", "whatsapp"):
                    await self.open_whatsapp_web()

                elif action in ("open_gmail", "gmail"):
                    await self.open_gmail()

                elif action in ("open_facebook", "facebook"):
                    await self.open_facebook()

                elif action in ("click_first_result", "click_first"):
                    await self.click_first_result()

                elif action == "click":
                    target = step.get("target", "first_result")
                    await self.click(target)

                elif action in ("play", "pause", "toggle_play"):
                    await self.toggle_media()

                elif action in ("screenshot", "take_screenshot"):
                    await self.take_screenshot(step.get("filename"))

                else:
                    logger.warning(f"Unrecognized browser action '{action}', attempting generic search/open")
                    if step.get("query"):
                        await self.search_google(step.get("query"))
                    elif step.get("target"):
                        await self.goto(step.get("target"))
                    else:
                        raise ValueError(f"Unknown action in step {step_num}: '{action}'")

                step_elapsed = time.perf_counter() - step_start
                results.append({
                    "step": step_num,
                    "action": action,
                    "status": "success",
                    "time": f"{step_elapsed:.2f}s",
                })
                steps_executed += 1

            except Exception as e:
                step_elapsed = time.perf_counter() - step_start
                logger.error(f"Step {step_num} failed ({action}): {e}")
                results.append({
                    "step": step_num,
                    "action": action,
                    "status": "failed",
                    "error": str(e),
                    "time": f"{step_elapsed:.2f}s",
                })
                steps_failed += 1

        total_elapsed = time.perf_counter() - start_total
        total_time_str = f"{total_elapsed:.2f}s"
        plan_status = "completed" if steps_failed == 0 else ("partial" if steps_executed > 0 else "failed")

        await self.record_history(
            "execute_plan",
            {
                "steps_total": len(steps),
                "steps_executed": steps_executed,
                "steps_failed": steps_failed,
            },
            status=plan_status,
            elapsed=total_time_str,
        )

        return {
            "status": plan_status,
            "steps_executed": steps_executed,
            "steps_failed": steps_failed,
            "time": total_time_str,
            "results": results,
        }

    async def record_history(self, action: str, details: Dict[str, Any], status: str = "success", elapsed: str = "0.0s"):
        """Appends an event to the browser_history.json file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details,
            "time": elapsed,
        }
        try:
            history = []
            if HISTORY_FILE.exists():
                try:
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        history = json.load(f)
                        if not isinstance(history, list):
                            history = []
                except Exception:
                    history = []

            history.append(entry)
            if len(history) > 500:
                history = history[-500:]

            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to record browser history: {e}")

    async def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves the last N actions from browser history."""
        if not HISTORY_FILE.exists():
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data[-limit:][::-1]
        except Exception as e:
            logger.error(f"Failed to read browser history: {e}")
        return []


# Global singleton instance
browser_service = BrowserService()
