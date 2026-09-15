import asyncio
import logging
from typing import Any, Dict, Optional, Tuple
import httpx

logger = logging.getLogger("common.network")


async def probe_service_health(
    client: httpx.AsyncClient,
    base_url: str,
    port: int,
    timeout: float = 2.0
) -> Dict[str, Any]:
    """Probe the health endpoint of a service, falling back to root endpoint."""
    probe_timeout = httpx.Timeout(timeout, connect=timeout)
    target = f"{base_url.rstrip('/')}/health"
    try:
        r = await client.get(target, timeout=probe_timeout)
        status = "online" if r.status_code < 400 else "error"
    except Exception:
        try:
            r = await client.get(base_url, timeout=probe_timeout)
            status = "online" if r.status_code < 400 else "error"
        except Exception:
            status = "offline"

    return {"status": status, "port": port, "url": base_url}


async def probe_ollama_status(
    client: httpx.AsyncClient,
    host: str,
    timeout: float = 2.0
) -> str:
    """Probe local Ollama tags API endpoint."""
    probe_timeout = httpx.Timeout(timeout, connect=timeout)
    try:
        r = await client.get(f"{host.rstrip('/')}/api/tags", timeout=probe_timeout)
        return "connected" if r.status_code == 200 else "disconnected"
    except Exception:
        return "disconnected"


async def post_with_retry(
    client: httpx.AsyncClient,
    url: str,
    json_data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    timeout: float = 60.0,
    max_retries: int = 1,
) -> Tuple[bool, Optional[httpx.Response], str]:
    """
    Execute an HTTP POST with automatic retry on connection errors or 5xx server errors.
    Returns (success, response, error_message).
    """
    last_error = ""
    for attempt in range(max_retries + 1):
        try:
            if files:
                response = await client.post(url, files=files, timeout=timeout)
            else:
                response = await client.post(url, json=json_data, timeout=timeout)

            if response.status_code < 500:
                return True, response, ""
            else:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.warning(f"Attempt {attempt + 1} to {url} returned 5xx: {last_error}")
        except httpx.RequestError as exc:
            last_error = f"Connection error: {str(exc)}"
            logger.warning(f"Attempt {attempt + 1} to {url} failed: {last_error}")
        except Exception as exc:
            last_error = f"Unexpected error: {str(exc)}"
            logger.warning(f"Attempt {attempt + 1} to {url} error: {last_error}")

        if attempt < max_retries:
            await asyncio.sleep(0.3)

    return False, None, last_error
