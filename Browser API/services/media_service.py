import logging
import time
from typing import Any, Dict
from services.browser_service import BrowserService

logger = logging.getLogger("media_service")


class MediaService:
    @staticmethod
    async def play(browser_svc: BrowserService) -> Dict[str, Any]:
        """Plays media on current page."""
        await browser_svc.ensure_active()
        start_time = time.perf_counter()

        # Check YouTube play button state
        try:
            yt_play_btn = await browser_svc.page.query_selector("button.ytp-play-button")
            if yt_play_btn:
                title = await yt_play_btn.get_attribute("data-title-no-tooltip")
                # If currently paused (tooltip says "Play"), click it
                if title and "play" in title.lower():
                    await yt_play_btn.click()
                    elapsed = time.perf_counter() - start_time
                    return {"status": "success", "action": "played", "details": {"target": "yt_button"}, "time": f"{elapsed:.2f}s"}
                elif title and "pause" in title.lower():
                    # Already playing
                    elapsed = time.perf_counter() - start_time
                    return {"status": "success", "action": "already_playing", "details": {"target": "yt_button"}, "time": f"{elapsed:.2f}s"}
        except Exception:
            pass

        # HTML5 video element evaluation
        try:
            res = await browser_svc.page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (video) {
                        video.play();
                        return true;
                    }
                    return false;
                }
            """)
            if res:
                elapsed = time.perf_counter() - start_time
                return {"status": "success", "action": "played", "details": {"target": "html5_video"}, "time": f"{elapsed:.2f}s"}
        except Exception:
            pass

        return await browser_svc.toggle_media()

    @staticmethod
    async def pause(browser_svc: BrowserService) -> Dict[str, Any]:
        """Pauses media on current page."""
        await browser_svc.ensure_active()
        start_time = time.perf_counter()

        # Check YouTube play button state
        try:
            yt_play_btn = await browser_svc.page.query_selector("button.ytp-play-button")
            if yt_play_btn:
                title = await yt_play_btn.get_attribute("data-title-no-tooltip")
                # If currently playing (tooltip says "Pause"), click it
                if title and "pause" in title.lower():
                    await yt_play_btn.click()
                    elapsed = time.perf_counter() - start_time
                    return {"status": "success", "action": "paused", "details": {"target": "yt_button"}, "time": f"{elapsed:.2f}s"}
                elif title and "play" in title.lower():
                    elapsed = time.perf_counter() - start_time
                    return {"status": "success", "action": "already_paused", "details": {"target": "yt_button"}, "time": f"{elapsed:.2f}s"}
        except Exception:
            pass

        # HTML5 video element evaluation
        try:
            res = await browser_svc.page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (video) {
                        video.pause();
                        return true;
                    }
                    return false;
                }
            """)
            if res:
                elapsed = time.perf_counter() - start_time
                return {"status": "success", "action": "paused", "details": {"target": "html5_video"}, "time": f"{elapsed:.2f}s"}
        except Exception:
            pass

        return await browser_svc.toggle_media()

    @staticmethod
    async def toggle(browser_svc: BrowserService) -> Dict[str, Any]:
        """Toggles media play/pause on current page."""
        return await browser_svc.toggle_media()
