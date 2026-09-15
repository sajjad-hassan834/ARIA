import logging
import time
from typing import Any, Dict
from services.browser_service import BrowserService

logger = logging.getLogger("search_service")


class SearchService:
    @staticmethod
    async def search(browser_svc: BrowserService, query: str, platform: str = "google") -> Dict[str, Any]:
        """Dispatches search request to the requested platform."""
        platform = platform.lower().strip()

        if platform == "youtube":
            return await browser_svc.search_youtube(query)
        elif platform == "google":
            return await browser_svc.search_google(query)
        elif platform == "amazon":
            return await SearchService.search_amazon(browser_svc, query)
        elif platform == "github":
            return await SearchService.search_github(browser_svc, query)
        else:
            # Fallback to Google
            logger.info(f"Unknown platform '{platform}', defaulting to Google search.")
            return await browser_svc.search_google(query)

    @staticmethod
    async def search_amazon(browser_svc: BrowserService, query: str) -> Dict[str, Any]:
        """Searches Amazon for query."""
        await browser_svc.ensure_active()
        start_time = time.perf_counter()
        
        # Amazon search URL directly or via home page
        search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
        await browser_svc.page.goto(search_url, wait_until="domcontentloaded")

        try:
            await browser_svc.page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=8000)
        except Exception:
            pass

        elapsed = time.perf_counter() - start_time
        time_str = f"{elapsed:.2f}s"
        details = {"platform": "amazon", "query": query, "url": browser_svc.page.url}
        await browser_svc.record_history("search", details, status="success", elapsed=time_str)
        return {"status": "success", "action": "searched", "details": details, "time": time_str}

    @staticmethod
    async def search_github(browser_svc: BrowserService, query: str) -> Dict[str, Any]:
        """Searches GitHub for query."""
        await browser_svc.ensure_active()
        start_time = time.perf_counter()
        
        search_url = f"https://github.com/search?q={query.replace(' ', '+')}&type=repositories"
        await browser_svc.page.goto(search_url, wait_until="domcontentloaded")

        try:
            await browser_svc.page.wait_for_selector('div[data-testid="results-list"], .repo-list', timeout=8000)
        except Exception:
            pass

        elapsed = time.perf_counter() - start_time
        time_str = f"{elapsed:.2f}s"
        details = {"platform": "github", "query": query, "url": browser_svc.page.url}
        await browser_svc.record_history("search", details, status="success", elapsed=time_str)
        return {"status": "success", "action": "searched", "details": details, "time": time_str}
